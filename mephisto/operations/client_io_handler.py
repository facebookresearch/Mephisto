#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import weakref
import time
import asyncio
from queue import Queue

from mephisto.data_model.packet import (
    Packet,
    PACKET_TYPE_ALIVE,
    PACKET_TYPE_AGENT_ACTION,
    PACKET_TYPE_NEW_AGENT,
    PACKET_TYPE_NEW_WORKER,
    PACKET_TYPE_REQUEST_AGENT_STATUS,
    PACKET_TYPE_RETURN_AGENT_STATUS,
    PACKET_TYPE_INIT_DATA,
    PACKET_TYPE_GET_INIT_DATA,
    PACKET_TYPE_PROVIDER_DETAILS,
    PACKET_TYPE_SUBMIT_ONBOARDING,
    PACKET_TYPE_REQUEST_ACTION,
    PACKET_TYPE_UPDATE_AGENT_STATUS,
    PACKET_TYPE_ERROR_LOG,
)
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.operations.datatypes import LiveTaskRun
from mephisto.abstractions._subcomponents.channel import Channel, STATUS_CHECK_TIME
from typing import Dict, Tuple, Union, Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


STATUS_TO_TEXT_MAP = {
    AgentState.STATUS_EXPIRED: "This task is no longer available to be completed. "
    "Please return it and try a different task",
    AgentState.STATUS_TIMEOUT: "You took to long to respond to this task, and have timed out. "
    "The task is no longer available, please return it.",
    AgentState.STATUS_DISCONNECT: "You have disconnected from our server during the duration of the task. "
    "If you have done substantial work, please reach out to see if we can recover it. ",
    AgentState.STATUS_PARTNER_DISCONNECT: "One of your partners has disconnected while working on this task. We won't penalize "
    "you for them leaving, so please submit this task as is.",
}

SYSTEM_CHANNEL_ID = "mephisto"
SERVER_CHANNEL_ID = "mephisto_server"
START_DEATH_TIME = 10


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

        self.is_shutdown = False

        # Deferred initializiation
        self._live_run: Optional["LiveTaskRun"] = None

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
            # TODO(#93) better error handling about failed messages
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
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=channel_id,
            )
        )

    def _log_frontend_error(self, packet: Packet):
        """Log to the local logger an error that occurred on the frontend"""
        error = packet.data["final_data"]
        logger.warning(f"[FRONT_END_ERROR]: {error}")

    def _on_act(self, packet: Packet, _channel_id: str):
        """Handle an action as sent from an agent, enqueuing to the agent"""
        live_run = self.get_live_run()
        agent = live_run.worker_pool.get_agent_for_id(packet.sender_id)
        assert agent is not None, "Could not find given agent!"

        # If the packet is_submit, and has files, we need to
        # process downloading those files first
        if packet.data.get("MEPHISTO_is_submit") is True:
            data_files = packet.data.get("files")
            if data_files is not None:
                save_dir = agent.get_data_dir()
                architect = live_run.architect
                for f_obj in data_files:
                    # TODO(#649) this is incredibly blocking!
                    architect.download_file(f_obj["filename"], save_dir)

        agent.pending_actions.put(packet)
        agent.has_action.set()

    def _register_agent(self, packet: Packet, channel_id: str) -> None:
        """process the packet, then delegate to the worker pool appropriate registration"""
        live_run = self.get_live_run()
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id
        crowd_data = packet.data["provider_data"]
        agent_registration_id = crowd_data["agent_registration_id"]
        logger.debug(f"Incoming request to register agent {agent_registration_id}.")
        if agent_registration_id in self.agents_by_registration_id:
            agent_id = self.agents_by_registration_id[agent_registration_id]
            self.agent_id_to_channel_id[agent_id] = channel_id
            self.enqueue_provider_details(request_id, {"agent_id": agent_id})
            logger.debug(
                f"Found existing agent_registration_id {agent_registration_id}, "
                f"reconnecting to {agent_id}."
            )
            return

        live_run.loop_wrap.execute_coro(
            live_run.worker_pool.register_agent(crowd_data, request_id)
        )

    def _register_worker(self, packet: Packet, channel_id: str) -> None:
        """Read and forward a worker registration packet"""
        live_run = self.get_live_run()
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id
        crowd_data = packet.data["provider_data"]
        live_run.loop_wrap.execute_coro(
            live_run.worker_pool.register_worker(crowd_data, request_id)
        )

    def enqueue_provider_details(
        self, request_id: str, additional_data: Dict[str, Any]
    ):
        """
        Synchronous method to enqueue a message sending the given provider details
        """
        base_data = {"request_id": request_id}
        for key, val in additional_data.items():
            base_data[key] = val
        self.message_queue.put(
            Packet(
                packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=self.request_id_to_channel_id[request_id],
                data=base_data,
            )
        )
        self.process_outgoing_queue(self.message_queue)
        del self.request_id_to_channel_id[request_id]

    def _get_init_data(self, packet, channel_id: str):
        """Get the initialization data for the assigned agent's task"""
        live_run = self.get_live_run()
        task_runner = live_run.task_runner
        agent_id = packet.data["provider_data"]["agent_id"]
        agent = live_run.worker_pool.get_agent_for_id(agent_id)
        assert isinstance(
            agent, Agent
        ), f"Can only get init unit data for Agents, not OnboardingAgents, got {agent}"
        # TODO(#649) this is IO bound
        unit_data = task_runner.get_init_data_for_agent(agent)

        agent_data_packet = Packet(
            packet_type=PACKET_TYPE_INIT_DATA,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=channel_id,
            data={"request_id": packet.data["request_id"], "init_data": unit_data},
        )

        self.message_queue.put(agent_data_packet)
        self.process_outgoing_queue(self.message_queue)

        if isinstance(unit_data, dict) and unit_data.get("raw_messages") is not None:
            # TODO(#651) clarify how raw messages are sent
            for message in unit_data["raw_messages"]:
                packet = Packet.from_dict(message)
                packet.receiver_id = agent_id
                agent.pending_observations.put(packet)

    def _on_submit_onboarding(self, packet: Packet, channel_id: str) -> None:
        """Handle the submission of onboarding data"""
        live_run = self.get_live_run()
        onboarding_id = packet.sender_id
        if onboarding_id not in live_run.worker_pool.onboarding_agents:
            logger.warning(
                f"Onboarding agent {onboarding_id} already submitted or disconnected, "
                f"but is calling _on_submit_onboarding again"
            )
            return
        agent = live_run.worker_pool.get_agent_for_id(onboarding_id)
        assert agent is not None, f"Could not find given agent by id {onboarding_id}"
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id

        logger.debug(f"{agent} has submitted onboarding: {packet}")
        # Update the request id for the original packet (which has the required
        # registration data) to be the new submission packet (so that we answer
        # back properly under the new request)
        live_run.worker_pool.onboarding_infos[onboarding_id].request_id = request_id

        del packet.data["request_id"]
        agent.pending_actions.put(packet)
        agent.has_action.set()

    def _on_message(self, packet: Packet, channel_id: str):
        """Handle incoming messages from the channel"""
        live_run = self.get_live_run()
        # TODO(#102) this method currently assumes that the packet's sender_id will
        # always be a valid agent in our list of agent_infos. At the moment this
        # is a valid assumption, but will not be on recovery from catastrophic failure.
        if packet.type == PACKET_TYPE_AGENT_ACTION:
            self._on_act(packet, channel_id)
        elif packet.type == PACKET_TYPE_NEW_AGENT:
            self._register_agent(packet, channel_id)
        elif packet.type == PACKET_TYPE_SUBMIT_ONBOARDING:
            self._on_submit_onboarding(packet, channel_id)
        elif packet.type == PACKET_TYPE_NEW_WORKER:
            self._register_worker(packet, channel_id)
        elif packet.type == PACKET_TYPE_GET_INIT_DATA:
            self._get_init_data(packet, channel_id)
        elif packet.type == PACKET_TYPE_RETURN_AGENT_STATUS:
            # Record this status response
            live_run.worker_pool.handle_updated_agent_status(packet.data)
        elif packet.type == PACKET_TYPE_ERROR_LOG:
            self._log_frontend_error(packet)
        else:
            # PACKET_TYPE_REQUEST_AGENT_STATUS, PACKET_TYPE_ALIVE,
            # PACKET_TYPE_INIT_DATA
            raise Exception(f"Unexpected packet type {packet.type}")

    def request_action(self, agent_id: str) -> None:
        """
        Request an act from the agent targetted here. If the
        agent is found by the server, this request will be
        forwarded.
        """
        send_packet = Packet(
            packet_type=PACKET_TYPE_REQUEST_ACTION,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=agent_id,
            data={},
        )
        self._get_channel_for_agent(agent_id).enqueue_send(send_packet)

    def _request_status_update(self) -> None:
        """
        Check last round of statuses, then request
        an update from the server on all agent's current status
        """
        for channel_id, channel in self.channels.items():
            send_packet = Packet(
                packet_type=PACKET_TYPE_REQUEST_AGENT_STATUS,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=channel_id,
                data={},
            )
            channel.enqueue_send(send_packet)

    async def _ping_statuses_while_alive(self) -> None:
        while not self.is_shutdown and len(self.channels) > 0:
            self._request_status_update()
            await asyncio.sleep(STATUS_CHECK_TIME)

    def send_status_update(self, agent_id: str, status: str):
        status_packet = Packet(
            packet_type=PACKET_TYPE_UPDATE_AGENT_STATUS,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=agent_id,
            data={
                "status": status,
                "state": {
                    # Any non-final status receives None and False for this
                    "done_text": STATUS_TO_TEXT_MAP.get(status),
                    "task_done": status == AgentState.STATUS_PARTNER_DISCONNECT,
                },
            },
        )
        self._get_channel_for_agent(agent_id).enqueue_send(status_packet)

    def send_done_message(self, agent_id: str):
        """Compose and send a done message to the given agent. This allows submission"""
        done_packet = Packet(
            packet_type=PACKET_TYPE_UPDATE_AGENT_STATUS,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=agent_id,
            data={
                "status": "completed",
                "state": {
                    "done_text": "You have completed this task. Please submit.",
                    "task_done": True,
                },
            },
        )
        self._get_channel_for_agent(agent_id).enqueue_send(done_packet)

    def process_outgoing_queue(self, message_queue: "Queue[Packet]") -> None:
        """Sends messages from the given list until it is empty"""
        while not message_queue.empty() > 0:
            curr_obs = message_queue.get()
            try:
                channel = self._get_channel_for_agent(curr_obs.receiver_id)
            except Exception:
                channel = self.channels[curr_obs.receiver_id]
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
