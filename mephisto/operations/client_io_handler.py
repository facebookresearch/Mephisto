#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import threading
import weakref
import time

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
from mephisto.operations.datatypes import LiveTaskRun, ChannelInfo, AgentInfo
from mephisto.abstractions.channel import Channel, STATUS_CHECK_TIME
from typing import Dict, Set, Tuple, Optional, List, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.operations.supervisor import Supervisor

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

SYSTEM_CHANNEL_ID = "mephisto"  # TODO pull from somewhere
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
        self.last_status_check = time.time()
        # Message handling
        # TODO can replace with a real Queue
        self.message_queue: List[Packet] = []
        self.agent_id_to_channel_id: Dict[str, str] = {}
        # Map from a request id to the channel that issued it
        self.request_id_to_channel_id: Dict[str, str] = {}
        # TODO this should be in an asyncio coroutine
        self.sending_thread: Optional[threading.Thread] = None

        # Deferred initializiation
        self._live_run: Optional["LiveTaskRun"] = None
        self._REPLACE_SUPERVISOR: Optional["Supervisor"] = None

    def _on_channel_open(self, channel_id: str) -> None:
        """Handler for what to do when a socket opens, we send an alive"""
        self._send_alive(channel_id)

    def _on_catastrophic_disconnect(self, channel_id: str) -> None:
        # TODO(#102) Catastrophic disconnect needs to trigger cleanup
        logger.error(f"Channel {channel_id} called on_catastrophic_disconnect")

    def _on_channel_message(self, channel_id: str, packet: Packet) -> None:
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

    def _register_channel(self, channel: Channel, live_run: "LiveTaskRun") -> str:
        """Register the channel to the specific live run"""
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
                    "please ensure that your local device has the correct SSL "
                    "certs installed."
                )
            try:
                self._send_alive(channel_id)
            except Exception:
                pass
            time.sleep(0.3)
        return channel_id

    def launch_channels(
        self, live_run: "LiveTaskRun", supervisor: "Supervisor"
    ) -> None:
        """Launch and register all of the channels for this live run to this IO handler"""
        assert (
            self._live_run is None
        ), "Cannot launch channels for a live run more than once!"
        self._live_run = live_run
        # TODO we'll eventually get the agent handler from the live run
        self._REPLACE_SUPERVISOR = supervisor

        channels = live_run.architect.get_channels(
            self._on_channel_open,
            self._on_catastrophic_disconnect,
            self._on_channel_message,
        )
        for channel in channels:
            self._register_channel(channel, live_run)
        self.launch_sending_thread()

    def register_agent_from_request_id(
        self, agent_id: str, request_id: str, registration_id: str
    ):
        """
        Given an agent id and request id, registers the agent id to the channel
        that the request was made from
        """
        channel_id = self.request_id_to_channel_id[request_id]
        self.agent_id_to_channel_id[agent_id] = channel_id
        self.agents_by_registration_id[registration_id] = agent_id

    def _send_alive(self, channel_id: str) -> bool:
        logger.info("Sending alive")
        return self.channels[channel_id].send(
            Packet(
                packet_type=PACKET_TYPE_ALIVE,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=channel_id,
            )
        )

    def _log_frontend_error(self, packet: Packet):
        error = packet.data["final_data"]
        logger.info(f"[FRONT_END_ERROR]: {error}")

    def _on_act(self, packet: Packet, _channel_id: str):
        """Handle an action as sent from an agent, enqueuing to the agent"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
        agent = self._get_agent_for_id(packet.sender_id)

        # If the packet is_submit, and has files, we need to
        # process downloading those files first
        if packet.data.get("MEPHISTO_is_submit") is True:
            data_files = packet.data.get("files")
            if data_files is not None:
                save_dir = agent.get_data_dir()
                architect = live_run.architect
                for f_obj in data_files:
                    architect.download_file(f_obj["filename"], save_dir)

        agent.pending_actions.append(packet)
        agent.has_action.set()

    def _register_agent(self, packet: Packet, channel_id: str) -> None:
        """process the packet, then delegate to the worker pool appropriate registration"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id
        crowd_data = packet.data["provider_data"]
        agent_registration_id = crowd_data["agent_registration_id"]
        logger.debug(f"Incoming request to register agent {agent_registration_id}.")
        if agent_registration_id in self.agents_by_registration_id:
            agent_id = self.agents_by_registration_id[agent_registration_id]
            self.agent_id_to_channel_id[agent_id] = channel_id
            self.send_provider_details(request_id, {"agent_id": agent_id})
            logger.debug(
                f"Found existing agent_registration_id {agent_registration_id}, "
                f"reconnecting to {agent_id}."
            )
            return

        live_run.worker_pool.register_agent(crowd_data, request_id, self._live_run)

    def _register_worker(self, packet: Packet, channel_id: str) -> None:
        """Read and forward a worker registration packet"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id
        crowd_data = packet.data["provider_data"]
        live_run.worker_pool.register_worker(crowd_data, request_id)

    def send_provider_details(self, request_id: str, additional_data: Dict[str, Any]):
        base_data = {"request_id": request_id}
        for key, val in additional_data.items():
            base_data[key] = val
        self.message_queue.append(
            Packet(
                packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=self.request_id_to_channel_id[request_id],
                data=base_data,
            )
        )
        del self.request_id_to_channel_id[request_id]

    def _get_init_data(self, packet, channel_id: str):
        """Get the initialization data for the assigned agent's task"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
        task_runner = live_run.task_runner
        agent_id = packet.data["provider_data"]["agent_id"]
        agent = self._get_agent_for_id(agent_id)
        assert isinstance(
            agent, Agent
        ), f"Can only get init unit data for Agents, not OnboardingAgents, got {agent}"
        unit_data = task_runner.get_init_data_for_agent(agent)

        agent_data_packet = Packet(
            packet_type=PACKET_TYPE_INIT_DATA,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=channel_id,
            data={"request_id": packet.data["request_id"], "init_data": unit_data},
        )

        self.message_queue.append(agent_data_packet)

        if isinstance(unit_data, dict) and unit_data.get("raw_messages") is not None:
            # TODO clarify how raw messages are sent
            for message in unit_data["raw_messages"]:
                packet = Packet.from_dict(message)
                packet.receiver_id = agent_id
                agent.pending_observations.append(packet)

    def _on_submit_onboarding(self, packet: Packet, channel_id: str) -> None:
        """Handle the submission of onboarding data"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
        onboarding_id = packet.sender_id
        if onboarding_id not in live_run.worker_pool.agents:
            logger.warning(
                f"Onboarding agent {onboarding_id} already submitted or disconnected, "
                f"but is calling _on_submit_onboarding again"
            )
            return
        agent = self._get_agent_for_id(onboarding_id)
        request_id = packet.data["request_id"]
        self.request_id_to_channel_id[request_id] = channel_id

        logger.debug(f"{agent} has submitted onboarding: {packet}")
        # Update the request id for the original packet (which has the required
        # registration data) to be the new submission packet (so that we answer
        # back properly under the new request)
        onboarding_tuple = self.onboarding_packets[onboarding_id]
        self.onboarding_packets[onboarding_id] = (onboarding_tuple[0], request_id)

        del packet.data["request_id"]
        agent.pending_actions.append(packet)
        agent.has_action.set()

    def _on_message(self, packet: Packet, channel_id: str):
        """Handle incoming messages from the channel"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
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
        self._get_channel_for_agent(agent_id).send(send_packet)

    def _request_status_update(self) -> None:
        """
        Check last round of statuses, then request
        an update from the server on all agent's current status
        """
        if time.time() - self.last_status_check < STATUS_CHECK_TIME:
            return

        self.last_status_check = time.time()
        for channel_id, channel in self.channels.items():
            send_packet = Packet(
                packet_type=PACKET_TYPE_REQUEST_AGENT_STATUS,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=channel_id,
                data={},
            )
            channel.send(send_packet)

    def _channel_handling_thread(self) -> None:
        """Thread for handling outgoing messages through the channels"""
        while len(self.channels) > 0:
            # Send all messages from the system
            self._send_handler_message_queue()
            self._request_status_update()
            # TODO(#103) is there a way we can trigger this when
            # agents observe instead?
            time.sleep(0.3)

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
        self._get_channel_for_agent(agent_id).send(status_packet)

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
        self._get_channel_for_agent(agent_id).send(done_packet)

    def _send_handler_message_queue(self) -> None:
        """Send all of the messages in the system queue"""
        self.send_message_queue(self.message_queue)

    def send_message_queue(self, message_queue: List[Packet]) -> None:
        """Sends messages from the given list until it is empty"""
        # TODO can we batch all of these?
        while len(message_queue) > 0:
            curr_obs = message_queue.pop(0)
            try:
                channel = self._get_channel_for_agent(curr_obs.receiver_id)
            except Exception:
                channel = self.channels[curr_obs.receiver_id]
            did_send = channel.send(curr_obs)
            if not did_send:
                logger.error(
                    f"Failed to send packet {curr_obs} to server {curr_obs.receiver_id}"
                )
                message_queue.insert(0, curr_obs)
                return  # something up with the channel, try later

    def launch_sending_thread(self) -> None:
        """Launch the sending thread for this IO handler"""
        self.sending_thread = threading.Thread(
            target=self._channel_handling_thread, name=f"channel-sending-thread"
        )
        self.sending_thread.start()

    def shutdown(self) -> None:
        """Close any channels related to a LiveTaskRun, clean up any resources"""
        self.message_queue = []
        run_channels = list(self.channels.keys())
        logger.debug(f"Closing channels {run_channels}")
        for channel_id in run_channels:
            self.channels[channel_id].close()
            del self.channels[channel_id]
        logger.debug(f"Joining send thread")
        if self.sending_thread is not None:
            self.sending_thread.join()
        self._live_run = None

    def _get_agent_for_id(self, agent_id: str):
        """Temporary method to get an agent, while API is figured out"""
        live_run = self._live_run
        assert live_run is not None, "Must have initialized a live run first"
        return live_run.worker_pool.agents[agent_id].agent

    def _get_channel_for_agent(self, agent_id: str) -> Channel:
        """Return the sending channel for a given agent"""
        channel_id = self.agent_id_to_channel_id.get(agent_id, None)
        if channel_id is None:
            raise Exception(f"No channel found for the given agent id {agent_id}!")
        return self.channels[channel_id]
