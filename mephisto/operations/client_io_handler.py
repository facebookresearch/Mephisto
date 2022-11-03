#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import asyncio
from queue import Queue
from prometheus_client import Histogram  # type: ignore

from mephisto.data_model.packet import (
    Packet,
    PACKET_TYPE_ALIVE,
    PACKET_TYPE_SUBMIT_ONBOARDING,
    PACKET_TYPE_SUBMIT_UNIT,
    PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE,
    PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE,
    PACKET_TYPE_REGISTER_AGENT,
    PACKET_TYPE_AGENT_DETAILS,
    PACKET_TYPE_UPDATE_STATUS,
    PACKET_TYPE_REQUEST_STATUSES,
    PACKET_TYPE_RETURN_STATUSES,
    PACKET_TYPE_ERROR,
    PACKET_TYPE_SUBMIT_METADATA,
)
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.agent import _AgentBase
from mephisto.operations.datatypes import LiveTaskRun
from mephisto.abstractions._subcomponents.channel import Channel, STATUS_CHECK_TIME
from typing import Dict, Tuple, Optional, Any, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB

from mephisto.utils.logger_core import get_logger, format_loud

logger = get_logger(name=__name__)

SYSTEM_CHANNEL_ID = "mephisto"
START_DEATH_TIME = 10

# Initialize monitoring metrics
PACKET_PROCESSING_LATENCY = Histogram(
    "client_io_handler_latency_seconds",
    "Time spent processing a packet on the IO handler",
    ["packet_type"],
)
E2E_PACKET_LATENCY = Histogram(
    "e2e_packet_latency",
    "Time spent processing packets across request lifecycle",
    ["packet_type", "stage"],
)
for packet_type in [
    PACKET_TYPE_SUBMIT_ONBOARDING,
    PACKET_TYPE_SUBMIT_UNIT,
    PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE,
    PACKET_TYPE_REGISTER_AGENT,
    PACKET_TYPE_RETURN_STATUSES,
    PACKET_TYPE_ERROR,
]:
    PACKET_PROCESSING_LATENCY.labels(packet_type=packet_type)
    for stage in [
        "client_to_router",
        "router_processing",
        "router_to_server",
        "server_processing",
        "e2e_time",
    ]:
        E2E_PACKET_LATENCY.labels(packet_type=packet_type, stage=stage)


class ClientIOHandler:
    """
    This class is responsible for managing all of the incoming and outgoing messages
    between the Mephisto backend, the router, and clients. It is tightly coupled with
    the Architect abstraction, and uses components of that API to send and receive
    messages, but operates on the level of message parsing and distribution logic.
    """

    def __init__(self, db: "MephistoDB"):
        self.db = db
        # Tracked IO state
        self.channels: Dict[str, Channel] = {}
        # Map from onboarding id to agent request packet
        self.onboarding_packets: Dict[str, Tuple[Dict[str, Any], str]] = {}
        # Dict from registration id to agent id
        self.agents_by_registration_id: Dict[str, str] = {}
        # Agent status handling
        self._status_task: Optional[asyncio.Task] = None
        # Message handling
        self.message_queue: "Queue[Packet]" = Queue()
        self.agent_id_to_channel_id: Dict[str, str] = {}
        # Map from a request id to the channel that issued it
        self.request_id_to_channel_id: Dict[str, str] = {}
        self.request_id_to_packet: Dict[str, Packet] = {}  # For metrics purposes

        self.is_shutdown = False
        self.last_submission_time = time.time()  # For patience tracking

        self.seen_update_ids: Set[str] = set()

        # Deferred initializiation
        self._live_run: Optional["LiveTaskRun"] = None

    def log_metrics_for_packet(self, packet: "Packet") -> None:
        """
        Log the full metrics for the provided packet, using now as the expected response time
        """
        client_timestamp = packet.client_timestamp
        router_incoming_timestamp = packet.router_incoming_timestamp
        router_outgoing_timestamp = packet.router_outgoing_timestamp
        server_timestamp = packet.server_timestamp
        response_timestamp = time.time()
        if router_outgoing_timestamp is None:
            router_outgoing_timestamp = server_timestamp
        if router_incoming_timestamp is None:
            router_incoming_timestamp = router_outgoing_timestamp
        if client_timestamp is None:
            client_timestamp = router_incoming_timestamp
        client_to_router = max(0, router_incoming_timestamp - client_timestamp)
        router_processing = max(
            0, router_outgoing_timestamp - router_incoming_timestamp
        )
        router_to_server = max(0, server_timestamp - router_outgoing_timestamp)
        server_processing = max(0, response_timestamp - server_timestamp)
        e2e_time = max(0, response_timestamp - client_timestamp)
        E2E_PACKET_LATENCY.labels(
            packet_type=packet.type, stage="client_to_router"
        ).observe(client_to_router)
        E2E_PACKET_LATENCY.labels(
            packet_type=packet.type, stage="router_processing"
        ).observe(router_processing)
        E2E_PACKET_LATENCY.labels(
            packet_type=packet.type, stage="router_to_server"
        ).observe(router_to_server)
        E2E_PACKET_LATENCY.labels(
            packet_type=packet.type, stage="server_processing"
        ).observe(server_processing)
        E2E_PACKET_LATENCY.labels(packet_type=packet.type, stage="e2e_time").observe(
            e2e_time
        )

    def register_run(self, live_run: "LiveTaskRun") -> None:
        """Register a live run for this io handler"""
        assert (
            self._live_run is None
        ), "Cannot associate more than one live run to an io handler at a time"
        self._live_run = live_run

    def get_live_run(self) -> "LiveTaskRun":
        """Get the associated live run for this handler, asserting it's set"""
        live_run = self._live_run
        assert live_run is not None, "Live run must be registered to use this"
        return live_run

    def _on_channel_open(self, channel_id: str) -> None:
        """Handler for what to do when a socket opens, we send an alive"""
        self._send_alive(channel_id)

    def _on_catastrophic_disconnect(self, channel_id: str) -> None:
        """On a catastrophic (unable to reconnect) disconnect event, cleanup this task"""
        logger.error(f"Channel {channel_id} called on_catastrophic_disconnect")

        live_run = self.get_live_run()
        live_run.force_shutdown = True

    async def __on_channel_message_internal(
        self, channel_id: str, packet: Packet
    ) -> None:
        """Incoming message handler defers to the internal handler"""
        try:
            self._on_message(packet, channel_id)
        except Exception as e:
            logger.exception(
                f"Channel {channel_id} encountered error on packet {packet}",
                exc_info=True,
            )
            raise

    def _on_channel_message(self, channel_id: str, packet: Packet) -> None:
        """Channel handler wrapper that passes handling to the local loop"""
        self.get_live_run().loop_wrap.execute_coro(
            self.__on_channel_message_internal(channel_id, packet)
        )

    def _register_channel(self, channel: Channel) -> str:
        """Register this channel"""
        channel_id = channel.channel_id

        self.channels[channel_id] = channel

        channel.open()
        self._send_alive(channel_id)
        start_time = time.time()
        while not channel.is_alive():
            if time.time() - start_time > START_DEATH_TIME:
                # TODO(OWN) Ask channel why it might have failed to connect?
                self.channels[channel_id].close()
                raise ConnectionRefusedError(  # noqa F821 we only support py3
                    "Was not able to establish a connection with the server, "
                    "please try to run again. If that fails,"
                    "please launch with mephisto.log_level=debug and watch for "
                    "clear errors. If this doesn't help, feel free to open an issue "
                    "with your debug logs on the Mephisto github."
                )
            try:
                self._send_alive(channel_id)
            except Exception:
                pass
            time.sleep(0.3)
        return channel_id

    def launch_channels(self) -> None:
        """Launch and register all of the channels for this live run to this IO handler"""
        live_run = self.get_live_run()

        channels = live_run.architect.get_channels(
            self._on_channel_open,
            self._on_catastrophic_disconnect,
            self._on_channel_message,
        )
        for channel in channels:
            self._register_channel(channel)

        async def launch_status_task():
            self._status_task = asyncio.create_task(self._ping_statuses_while_alive())

        live_run.loop_wrap.execute_coro(launch_status_task())

    def associate_agent_with_registration(
        self, agent_id: str, request_id: str, registration_id: str
    ) -> None:
        """
        Given an agent id and request id, registers the agent id to the channel
        that the request was made from
        """
        channel_id = self.request_id_to_channel_id[request_id]
        self.agent_id_to_channel_id[agent_id] = channel_id
        self.agents_by_registration_id[registration_id] = agent_id

    def _send_alive(self, channel_id: str) -> bool:
        logger.info("Sending alive")
        return self.channels[channel_id].enqueue_send(
            Packet(
                packet_type=PACKET_TYPE_ALIVE,
                subject_id=SYSTEM_CHANNEL_ID,
            )
        )

    def _log_frontend_error(self, packet: Packet):
        """Log to the local logger an error that occurred on the frontend"""
        error = packet.data
        if "error_type" in error and error["error_type"] == "version-mismatch":
            logger.warning(f"{format_loud('[Version Mismatch!!]')}: {error['text']}")
        else:
            logger.warning(f"[FRONT_END_ERROR]: {error}")

    def _on_live_update(self, packet: Packet, _channel_id: str):
        """Handle an action as sent from an agent, enqueuing to the agent"""
        live_run = self.get_live_run()
        agent = live_run.worker_pool.get_agent_for_id(packet.subject_id)
        assert agent is not None, f"Could not find given agent: {packet.subject_id}"

        agent.pending_actions.put(packet.data)
        agent.has_live_update.set()

    def _on_submit_unit(self, packet: Packet, _channel_id: str):
        """Handle an action as sent from an agent, enqueuing to the agent"""
        live_run = self.get_live_run()
        agent = live_run.worker_pool.get_agent_for_id(packet.subject_id)
        assert agent is not None, "Could not find given agent!"

        # Special handler for file downloads while we have architect access
        # NOTE: this is a leaky abstraction at the moment - only architects
        # know how to save files but "file saving" methods are defined by
        # AgentStates, which don't have architect access.
        if isinstance(packet.data, dict):
            data_files = packet.data.get("files")
            if data_files is not None:
                save_dir = agent.get_data_dir()
                architect = live_run.architect
                for f_obj in data_files:
                    # TODO(#649) this is incredibly blocking!
                    architect.download_file(f_obj["filename"], save_dir)

        agent.handle_submit(packet.data)

    def _on_submit_metadata(self, packet: Packet):
        live_run = self.get_live_run()
        agent = live_run.worker_pool.get_agent_for_id(packet.subject_id)
        assert agent is not None, "Could not find given agent!"
        agent.handle_metadata_submit(packet.data)

    def _on_submit_onboarding(self, packet: Packet, channel_id: str) -> None:
        """Handle the submission of onboarding data"""
        assert (
            "onboarding_data" in packet.data
        ), f"Onboarding packet {packet} submitted without data"
        agent: Optional["_AgentBase"]
        live_run = self.get_live_run()
        onboarding_id = packet.subject_id
        if onboarding_id not in live_run.worker_pool.onboarding_agents:
            logger.warning(
                f"Onboarding agent {onboarding_id} already submitted or disconnected, "
                f"but is calling _on_submit_onboarding again"
            )
            # On resubmit, ensure that the client has the same status
            agent = live_run.worker_pool.final_onboardings.get(onboarding_id)
            if agent is not None:
                live_run.loop_wrap.execute_coro(
                    live_run.worker_pool.push_status_update(agent)
                )
            return
        agent = live_run.worker_pool.get_agent_for_id(onboarding_id)
        assert agent is not None, f"Could not find given agent by id {onboarding_id}"
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id
        self.request_id_to_packet[request_id] = packet
        agent.update_status(AgentState.STATUS_WAITING)

        logger.debug(f"{agent} has submitted onboarding: {packet}")
        # Update the request id for the original packet (which has the required
        # registration data) to be the new submission packet (so that we answer
        # back properly under the new request)
        live_run.worker_pool.onboarding_infos[onboarding_id].request_id = request_id

        agent.handle_submit(packet.data["onboarding_data"])

    def _register_agent(self, packet: Packet, channel_id: str) -> None:
        """Read and forward a worker registration packet"""
        live_run = self.get_live_run()
        request_id = packet.data["request_id"]

        self.request_id_to_channel_id[request_id] = channel_id
        self.request_id_to_packet[request_id] = packet
        crowd_data = packet.data["provider_data"]

        # Check for reconnecting agent
        agent_registration_id = crowd_data["agent_registration_id"]
        if agent_registration_id in self.agents_by_registration_id:
            agent_id = self.agents_by_registration_id[agent_registration_id]
            live_run.loop_wrap.execute_coro(
                live_run.worker_pool.reconnect_agent(agent_id, request_id)
            )
            self.agent_id_to_channel_id[agent_id] = channel_id
            logger.debug(
                f"Found existing agent_registration_id {agent_registration_id}, "
                f"reconnecting to {agent_id}."
            )
            return

        # Handle regular agent
        live_run.loop_wrap.execute_coro(
            live_run.worker_pool.register_worker(crowd_data, request_id)
        )

    def enqueue_agent_details(self, request_id: str, additional_data: Dict[str, Any]):
        """
        Synchronous method to enqueue a message sending the given agent details
        """
        base_data = {"request_id": request_id}
        for key, val in additional_data.items():
            base_data[key] = val
        self.message_queue.put(
            Packet(
                packet_type=PACKET_TYPE_AGENT_DETAILS,
                subject_id=self.request_id_to_channel_id[request_id],
                data=base_data,
            )
        )
        self.process_outgoing_queue(self.message_queue)
        self.log_metrics_for_packet(self.request_id_to_packet[request_id])
        # TODO Sometimes this request ID is lost, and we don't quite know why
        del self.request_id_to_channel_id[request_id]
        del self.request_id_to_packet[request_id]

    def _on_message(self, packet: Packet, channel_id: str):
        """Handle incoming messages from the channel"""
        live_run = self.get_live_run()
        # TODO(#102) this method currently assumes that the packet's subject_id will
        # always be a valid agent in our list of agent_infos. This isn't always the case
        # when relaunching with the same URLs.
        with PACKET_PROCESSING_LATENCY.labels(packet_type=packet.type).time():
            if packet.type == PACKET_TYPE_SUBMIT_ONBOARDING:
                self._on_submit_onboarding(packet, channel_id)
            elif packet.type == PACKET_TYPE_SUBMIT_UNIT:
                self._on_submit_unit(packet, channel_id)
                self.log_metrics_for_packet(packet)
                self.last_submission_time = time.time()
            elif packet.type == PACKET_TYPE_SUBMIT_METADATA:
                self._on_submit_metadata(packet)
            elif packet.type == PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE:
                update_id = packet.data.get("update_id")
                if update_id is not None and update_id in self.seen_update_ids:
                    return  # Processing duplicated packet
                self._on_live_update(packet, channel_id)
                self.log_metrics_for_packet(packet)
                self.seen_update_ids.add(update_id)
            elif packet.type == PACKET_TYPE_REGISTER_AGENT:
                self._register_agent(packet, channel_id)
            elif packet.type == PACKET_TYPE_RETURN_STATUSES:
                # Record this status response
                live_run.worker_pool.handle_updated_agent_status(packet.data)
                self.log_metrics_for_packet(packet)
            elif packet.type == PACKET_TYPE_ERROR:
                self._log_frontend_error(packet)
                self.log_metrics_for_packet(packet)
            else:
                # PACKET_TYPE_REQUEST_STATUSES, PACKET_TYPE_ALIVE,
                # PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE, PACKET_TYPE_AGENT_DETAILS
                raise Exception(f"Unexpected packet type {packet.type}")

    def _request_status_update(self) -> None:
        """
        Check last round of statuses, then request
        an update from the server on all agent's current status
        """
        for channel_id, channel in self.channels.items():
            send_packet = Packet(
                packet_type=PACKET_TYPE_REQUEST_STATUSES,
                subject_id=SYSTEM_CHANNEL_ID,
                data={},
            )
            channel.enqueue_send(send_packet)

    async def _ping_statuses_while_alive(self) -> None:
        while not self.is_shutdown and len(self.channels) > 0:
            self._request_status_update()
            await asyncio.sleep(STATUS_CHECK_TIME)

    def send_live_update(self, agent_id: str, data: Dict[str, Any]):
        """Send a live data packet to the given agent id"""
        data_packet = Packet(
            packet_type=PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE,
            subject_id=agent_id,
            data=data,
        )
        self._get_channel_for_agent(agent_id).enqueue_send(data_packet)

    def send_status_update(self, agent_id: str, status: str):
        """Update the status for the given agent"""
        status_packet = Packet(
            packet_type=PACKET_TYPE_UPDATE_STATUS,
            subject_id=agent_id,
            data={
                "status": status,
            },
        )
        self._get_channel_for_agent(agent_id).enqueue_send(status_packet)

    def process_outgoing_queue(self, message_queue: "Queue[Packet]") -> None:
        """Sends messages from the given list until it is empty"""
        while not message_queue.empty() > 0:
            curr_obs = message_queue.get()
            try:
                channel = self._get_channel_for_agent(curr_obs.subject_id)
            except Exception:
                channel = self.channels[curr_obs.subject_id]
            channel.enqueue_send(curr_obs)

    def shutdown(self) -> None:
        """Close any channels related to a LiveTaskRun, clean up any resources"""
        while not self.message_queue.empty():
            self.message_queue.get()
        run_channels = list(self.channels.keys())
        logger.debug(f"Closing channels {run_channels}")
        for channel_id in run_channels:
            self.channels[channel_id].close()
            del self.channels[channel_id]
        self.is_shutdown = True

        logger.debug(f"Cancelling status ping task")
        try:
            if self._status_task is not None and not self._status_task.cancelled():
                self._status_task.cancel()

                async def await_status_task():
                    await self._status_task
                    self._live_run = None

                self.get_live_run().loop_wrap.execute_coro(await_status_task())
        except asyncio.CancelledError:
            pass

    def _get_channel_for_agent(self, agent_id: str) -> Channel:
        """Return the sending channel for a given agent"""
        channel_id = self.agent_id_to_channel_id.get(agent_id, None)
        if channel_id is None:
            raise Exception(f"No channel found for the given agent id {agent_id}!")
        return self.channels[channel_id]
