#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import threading
from queue import PriorityQueue, Empty
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
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import worker_is_qualified
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.abstractions.blueprint import OnboardingRequired, AgentState
from mephisto.operations.registry import get_crowd_provider_from_type
from mephisto.abstractions.channel import Channel, STATUS_CHECK_TIME

from dataclasses import dataclass

from typing import Dict, Set, Optional, List, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import TaskRunner
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.abstractions.architect import Architect

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)

# This class manages communications between the server
# and workers, ensures that their status is properly tracked,
# and also provides some helping utility functions for
# groups of workers or worker/agent compatibility.

# Mostly, the supervisor oversees the communications
# between jobs and workers over the channels

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

# State storage
@dataclass
class Job:
    architect: "Architect"
    task_runner: "TaskRunner"
    provider: "CrowdProvider"
    qualifications: List[Dict[str, Any]]
    registered_channel_ids: List[str]


@dataclass
class ChannelInfo:
    channel_id: str
    job: "Job"
    channel: Channel


@dataclass
class AgentInfo:
    agent: Union["Agent", "OnboardingAgent"]
    used_channel_id: str
    assignment_thread: Optional[threading.Thread] = None


class Supervisor:
    def __init__(self, db: "MephistoDB"):
        self.db = db
        # Tracked state
        self.agents: Dict[str, AgentInfo] = {}
        self.agents_by_registration_id: Dict[str, AgentInfo] = {}
        self.channels: Dict[str, ChannelInfo] = {}
        # Map from onboarding id to agent request packet
        self.onboarding_packets: Dict[str, Packet] = {}

        # Agent status handling
        self.last_status_check = time.time()

        # Message handling
        self.message_queue: List[Packet] = []
        self.sending_thread: Optional[threading.Thread] = None

    def _on_channel_open(self, channel_id: str):
        """Handler for what to do when a socket opens, we send an alive"""
        channel_info = self.channels[channel_id]
        self._send_alive(channel_info)

    def _on_catastrophic_disconnect(self, channel_id):
        # TODO(#102) Catastrophic disconnect needs to trigger cleanup
        logger.error(f"Channel {channel_id} called on_catastrophic_disconnect")

    def _on_channel_message(self, channel_id: str, packet: Packet):
        """Incoming message handler defers to the internal handler"""
        try:
            channel_info = self.channels[channel_id]
            self._on_message(packet, channel_info)
        except Exception as e:
            # TODO(#93) better error handling about failed messages
            logger.exception(
                f"Channel {channel_id} encountered error on packet {packet}",
                exc_info=True,
            )
            raise

    def register_job(
        self,
        architect: "Architect",
        task_runner: "TaskRunner",
        provider: "CrowdProvider",
        qualifications: Optional[List[Dict[str, Any]]] = None,
    ):
        if qualifications is None:
            qualifications = []
        task_run = task_runner.task_run
        channels = architect.get_channels(
            self._on_channel_open,
            self._on_catastrophic_disconnect,
            self._on_channel_message,
        )
        job = Job(
            architect=architect,
            task_runner=task_runner,
            provider=provider,
            qualifications=qualifications,
            registered_channel_ids=[],
        )
        for channel in channels:
            channel_id = self.register_channel(channel, job)
            job.registered_channel_ids.append(channel_id)
        return job

    def register_channel(self, channel: Channel, job: "Job") -> str:
        """Register the channel to the specific job"""
        channel_id = channel.channel_id

        channel_info = ChannelInfo(channel_id=channel_id, channel=channel, job=job)
        self.channels[channel_id] = channel_info

        channel.open()
        self._send_alive(channel_info)
        start_time = time.time()
        while not channel.is_alive():
            if time.time() - start_time > START_DEATH_TIME:
                # TODO(OWN) Ask channel why it might have failed to connect?
                self.channels[channel_id].channel.close()
                raise ConnectionRefusedError(  # noqa F821 we only support py3
                    "Was not able to establish a connection with the server, "
                    "please try to run again. If that fails,"
                    "please ensure that your local device has the correct SSL "
                    "certs installed."
                )
            try:
                self._send_alive(channel_info)
            except Exception:
                pass
            time.sleep(0.3)
        return channel_id

    def close_channel(self, channel_id: str):
        """Close the given channel by id"""
        self.channels[channel_id].channel.close()
        del self.channels[channel_id]

    def shutdown_job(self, job: Job):
        """Close any channels related to a job"""
        job_channels = job.registered_channel_ids
        for channel_id in job_channels:
            self.close_channel(channel_id)

    def shutdown(self):
        """Close all of the channels, join threads"""
        # Prepopulate agents and channels to close, as
        # these may change during iteration
        channels_to_close = list(self.channels.keys())
        logger.debug(f"Closing channels {channels_to_close}")
        for channel_id in channels_to_close:
            channel_info = self.channels[channel_id]
            channel_info.job.task_runner.shutdown()
            self.close_channel(channel_id)
        logger.debug(f"Joining send thread")
        if self.sending_thread is not None:
            self.sending_thread.join()
        logger.debug(f"Joining agents {self.agents}")
        agents_to_close = list(self.agents.values())
        for agent_info in agents_to_close:
            assign_thread = agent_info.assignment_thread
            if assign_thread is not None:
                assign_thread.join()

    def _send_alive(self, channel_info: ChannelInfo) -> bool:
        logger.info("Sending alive")
        return channel_info.channel.send(
            Packet(
                packet_type=PACKET_TYPE_ALIVE,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=channel_info.channel_id,
            )
        )

    def _on_act(self, packet: Packet, channel_info: ChannelInfo):
        """Handle an action as sent from an agent"""
        agent = self.agents[packet.sender_id].agent

        # If the packet is_submit, and has files, we need to
        # process downloading those files first
        if packet.data.get("MEPHISTO_is_submit") is True:
            data_files = packet.data.get("files")
            if data_files is not None:
                save_dir = agent.get_data_dir()
                architect = channel_info.job.architect
                for f_obj in data_files:
                    architect.download_file(f_obj["filename"], save_dir)

        # TODO(OWN) Packets stored as info from workers can also be
        # saved somewhere locally just in case the world dies, and
        # then cleaned up once the world completes successfully
        agent.pending_actions.append(packet)
        agent.has_action.set()

    def _on_submit_onboarding(self, packet: Packet, channel_info: ChannelInfo):
        """Handle the submission of onboarding data"""
        onboarding_id = packet.sender_id
        if onboarding_id not in self.agents:
            logger.warning(
                f"Onboarding agent {onboarding_id} already submitted or disconnected, "
                f"but is calling _on_submit_onboarding again"
            )
            return
        agent_info = self.agents[onboarding_id]
        agent = agent_info.agent

        logger.debug(f"{agent} has submitted onboarding: {packet}")
        # Update the request id for the original packet (which has the required
        # registration data) to be the new submission packet (so that we answer
        # back properly under the new request)
        self.onboarding_packets[onboarding_id].data["request_id"] = packet.data[
            "request_id"
        ]
        del packet.data["request_id"]
        agent.pending_actions.append(packet)
        agent.has_action.set()

    def _register_worker(self, packet: Packet, channel_info: ChannelInfo):
        """Process a worker registration packet to register a worker"""
        crowd_data = packet.data["provider_data"]
        crowd_provider = channel_info.job.provider
        worker_name = crowd_data["worker_name"]
        workers = self.db.find_workers(worker_name=worker_name)
        if len(workers) == 0:
            # TODO(WISH) get rid of sandbox designation
            workers = self.db.find_workers(worker_name=worker_name + "_sandbox")
        if len(workers) == 0:
            worker = crowd_provider.WorkerClass.new_from_provider_data(
                self.db, crowd_data
            )
        else:
            worker = workers[0]

        if not worker_is_qualified(worker, channel_info.job.qualifications):
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_CHANNEL_ID,
                    receiver_id=channel_info.channel_id,
                    data={"request_id": packet.data["request_id"], "worker_id": None},
                )
            )
        else:
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_CHANNEL_ID,
                    receiver_id=channel_info.channel_id,
                    data={
                        "request_id": packet.data["request_id"],
                        "worker_id": worker.db_id,
                    },
                )
            )

    def _launch_and_run_onboarding(
        self, agent_info: "AgentInfo", task_runner: "TaskRunner"
    ):
        """Launch a thread to supervise the completion of onboarding for a task"""
        tracked_agent = agent_info.agent
        onboarding_id = tracked_agent.get_agent_id()
        assert isinstance(tracked_agent, OnboardingAgent), (
            "Can launch onboarding for OnboardingAgents, not Agents"
            f", got {tracked_agent}"
        )
        try:
            logger.debug(f"Launching onboarding for {tracked_agent}")
            task_runner.launch_onboarding(tracked_agent)
            if tracked_agent.get_status() == AgentState.STATUS_WAITING:
                # The agent completed the onboarding task
                self._register_agent_from_onboarding(tracked_agent)
            else:
                logger.info(
                    f"Onboarding agent {onboarding_id} disconnected or errored, "
                    f"final status {tracked_agent.get_status()}."
                )
                self._send_status_update(agent_info)
        except Exception as e:
            logger.warning(f"Onboarding for {tracked_agent} failed with exception {e}")
            import traceback

            traceback.print_exc()
            task_runner.cleanup_onboarding(tracked_agent)
        finally:
            del self.agents[onboarding_id]
            del self.onboarding_packets[onboarding_id]

    def _launch_and_run_assignment(
        self,
        assignment: "Assignment",
        agent_infos: List["AgentInfo"],
        task_runner: "TaskRunner",
    ):
        """Launch a thread to supervise the completion of an assignment"""
        try:
            tracked_agents: List["Agent"] = []
            for a in agent_infos:
                assert isinstance(
                    a.agent, Agent
                ), f"Can launch assignments for Agents, not OnboardingAgents, got {a.agent}"
                tracked_agents.append(a.agent)
            task_runner.launch_assignment(assignment, tracked_agents)
            for agent_info in agent_infos:
                self._mark_agent_done(agent_info)
            # Wait for agents to be complete
            for agent_info in agent_infos:
                agent = agent_info.agent
                if agent.get_status() not in AgentState.complete():
                    if not agent.did_submit.is_set():
                        # Wait for a submit to occur
                        # TODO(#94) make submit timeout configurable
                        agent.has_action.wait(timeout=300)
                        agent.act()
                    agent.mark_done()
        except Exception as e:
            logger.exception(f"Cleaning up assignment: {e}", exc_info=True)
            task_runner.cleanup_assignment(assignment)
        finally:
            task_run = task_runner.task_run
            for unit in assignment.get_units():
                task_run.clear_reservation(unit)

    def _launch_and_run_unit(
        self, unit: "Unit", agent_info: "AgentInfo", task_runner: "TaskRunner"
    ):
        """Launch a thread to supervise the completion of an assignment"""
        try:
            agent = agent_info.agent
            assert isinstance(
                agent, Agent
            ), f"Can launch units for Agents, not OnboardingAgents, got {agent}"
            task_runner.launch_unit(unit, agent)
            if agent.get_status() not in AgentState.complete():
                self._mark_agent_done(agent_info)
                if not agent.did_submit.is_set():
                    # Wait for a submit to occur
                    # TODO(#94) make submit timeout configurable
                    agent.has_action.wait(timeout=300)
                    agent.act()
                agent.mark_done()
        except Exception as e:
            logger.exception(f"Cleaning up unit: {e}", exc_info=True)
            task_runner.cleanup_unit(unit)
        finally:
            task_runner.task_run.clear_reservation(unit)

    def _assign_unit_to_agent(
        self, packet: Packet, channel_info: ChannelInfo, units: List["Unit"]
    ):
        """Handle creating an agent for the specific worker to register an agent"""

        crowd_data = packet.data["provider_data"]
        task_run = channel_info.job.task_runner.task_run
        crowd_provider = channel_info.job.provider
        worker_id = crowd_data["worker_id"]
        worker = Worker.get(self.db, worker_id)

        logger.debug(
            f"Worker {worker_id} is being assigned one of " f"{len(units)} units."
        )

        reserved_unit = None
        while len(units) > 0 and reserved_unit is None:
            unit = units.pop(0)
            reserved_unit = task_run.reserve_unit(unit)
        if reserved_unit is None:
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_CHANNEL_ID,
                    receiver_id=channel_info.channel_id,
                    data={"request_id": packet.data["request_id"], "agent_id": None},
                )
            )
        else:
            agent = crowd_provider.AgentClass.new_from_provider_data(
                self.db, worker, unit, crowd_data
            )
            logger.debug(f"Created agent {agent}, {agent.db_id}.")
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_CHANNEL_ID,
                    receiver_id=channel_info.channel_id,
                    data={
                        "request_id": packet.data["request_id"],
                        "agent_id": agent.get_agent_id(),
                    },
                )
            )
            agent_info = AgentInfo(agent=agent, used_channel_id=channel_info.channel_id)
            self.agents[agent.get_agent_id()] = agent_info
            self.agents_by_registration_id[
                crowd_data["agent_registration_id"]
            ] = agent_info

            # Launch individual tasks
            if not channel_info.job.task_runner.is_concurrent:
                unit_thread = threading.Thread(
                    target=self._launch_and_run_unit,
                    args=(unit, agent_info, channel_info.job.task_runner),
                    name=f"Unit-thread-{unit.db_id}",
                )
                agent_info.assignment_thread = unit_thread
                unit_thread.start()
            else:
                # See if the concurrent unit is ready to launch
                assignment = unit.get_assignment()
                agents = assignment.get_agents()
                if None in agents:
                    agent.update_status(AgentState.STATUS_WAITING)
                    return  # need to wait for all agents to be here to launch

                # Launch the backend for this assignment
                agent_infos = [self.agents[a.db_id] for a in agents if a is not None]

                assign_thread = threading.Thread(
                    target=self._launch_and_run_assignment,
                    args=(assignment, agent_infos, channel_info.job.task_runner),
                    name=f"Assignment-thread-{assignment.db_id}",
                )

                for agent_info in agent_infos:
                    agent_info.agent.update_status(AgentState.STATUS_IN_TASK)
                    agent_info.assignment_thread = assign_thread

                assign_thread.start()

    def _register_agent_from_onboarding(self, onboarding_agent: "OnboardingAgent"):
        """
        Convert the onboarding agent to a full agent
        """
        logger.info(f"Registering onboarding agent {onboarding_agent}")
        onboarding_id = onboarding_agent.get_agent_id()
        onboarding_agent_info = self.agents.get(onboarding_id)

        if onboarding_agent_info is None:
            logger.warning(
                f"Could not find info for onboarding agent {onboarding_id}, "
                "but they submitted onboarding"
            )
            return

        current_status = onboarding_agent.get_status()
        channel_id = onboarding_agent_info.used_channel_id
        channel_info = self.channels[channel_id]
        task_runner = channel_info.job.task_runner
        task_run = task_runner.task_run
        blueprint = task_run.get_blueprint(args=task_runner.args)
        worker = onboarding_agent.get_worker()

        assert (
            isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding
        ), "Should only be registering from onboarding if onboarding is required and set"
        worker_passed = blueprint.validate_onboarding(worker, onboarding_agent)
        worker.grant_qualification(
            blueprint.onboarding_qualification_name, int(worker_passed)
        )
        if not worker_passed:
            worker.grant_qualification(
                blueprint.onboarding_failed_name, int(worker_passed)
            )
            onboarding_agent.update_status(AgentState.STATUS_REJECTED)
            logger.info(f"Onboarding agent {onboarding_id} failed onboarding")
        else:
            onboarding_agent.update_status(AgentState.STATUS_APPROVED)
            logger.info(
                f"Onboarding agent {onboarding_id} registered out from onboarding"
            )

        # get the list of tentatively valid units
        units = task_run.get_valid_units_for_worker(worker)
        usable_units = channel_info.job.task_runner.filter_units_for_worker(
            units, worker
        )

        if not worker_passed:
            # TODO(WISH) it may be worth investigating launching a dummy task for these
            # instances where a worker has failed onboarding, but the onboarding
            # task still allowed submission of the failed data (no front-end validation)
            # units = [self.dummy_launcher.launch_dummy()]
            # self._assign_unit_to_agent(packet, channel_info, units)
            usable_units = []

        packet = self.onboarding_packets[onboarding_agent.get_agent_id()]
        self._try_send_agent_messages(onboarding_agent_info)
        self._send_status_update(onboarding_agent_info)
        self._assign_unit_to_agent(packet, channel_info, usable_units)

    def _register_agent(self, packet: Packet, channel_info: ChannelInfo):
        """Process an agent registration packet to register an agent"""
        # First see if this is a reconnection
        crowd_data = packet.data["provider_data"]
        agent_registration_id = crowd_data["agent_registration_id"]
        logger.debug(f"Incoming request to register agent {agent_registration_id}.")
        if agent_registration_id in self.agents_by_registration_id:
            agent = self.agents_by_registration_id[agent_registration_id].agent
            # Update the source channel, in case it has changed
            self.agents[agent.get_agent_id()].used_channel_id = channel_info.channel_id
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_CHANNEL_ID,
                    receiver_id=channel_info.channel_id,
                    data={
                        "request_id": packet.data["request_id"],
                        "agent_id": agent.get_agent_id(),
                    },
                )
            )
            logger.debug(
                f"Found existing agent_registration_id {agent_registration_id}, "
                f"reconnecting to {agent}."
            )
            return

        # Process a new agent
        task_runner = channel_info.job.task_runner
        task_run = task_runner.task_run
        worker_id = crowd_data["worker_id"]
        worker = Worker.get(self.db, worker_id)

        # get the list of tentatively valid units
        units = task_run.get_valid_units_for_worker(worker)
        if len(units) == 0:
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_CHANNEL_ID,
                    receiver_id=channel_info.channel_id,
                    data={"request_id": packet.data["request_id"], "agent_id": None},
                )
            )
            logger.debug(
                f"Found existing agent_registration_id {agent_registration_id}, "
                f"had no valid units."
            )
            return

        # If there's onboarding, see if this worker has already been disqualified
        worker_id = crowd_data["worker_id"]
        worker = Worker.get(self.db, worker_id)
        blueprint = task_run.get_blueprint(args=task_runner.args)
        if isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding:
            if worker.is_disqualified(blueprint.onboarding_qualification_name):
                self.message_queue.append(
                    Packet(
                        packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                        sender_id=SYSTEM_CHANNEL_ID,
                        receiver_id=channel_info.channel_id,
                        data={
                            "request_id": packet.data["request_id"],
                            "agent_id": None,
                        },
                    )
                )
                logger.debug(
                    f"Worker {worker_id} is already disqualified by onboarding "
                    f"qual {blueprint.onboarding_qualification_name}."
                )
                return
            elif not worker.is_qualified(blueprint.onboarding_qualification_name):
                # Send a packet with onboarding information
                onboard_data = blueprint.get_onboarding_data(worker.db_id)
                onboard_agent = OnboardingAgent.new(self.db, worker, task_run)
                onboard_agent.state.set_init_state(onboard_data)
                agent_info = AgentInfo(
                    agent=onboard_agent, used_channel_id=channel_info.channel_id
                )
                onboard_id = onboard_agent.get_agent_id()
                # register onboarding agent
                self.agents[onboard_id] = agent_info
                self.onboarding_packets[onboard_id] = packet
                self.message_queue.append(
                    Packet(
                        packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                        sender_id=SYSTEM_CHANNEL_ID,
                        receiver_id=channel_info.channel_id,
                        data={
                            "request_id": packet.data["request_id"],
                            "agent_id": onboard_id,
                            "onboard_data": onboard_data,
                        },
                    )
                )

                logger.debug(
                    f"{worker} is starting onboarding thread with "
                    f"onboarding {onboard_agent}."
                )

                # Create an onboarding thread
                onboard_thread = threading.Thread(
                    target=self._launch_and_run_onboarding,
                    args=(agent_info, channel_info.job.task_runner),
                    name=f"Onboard-thread-{onboard_id}",
                )

                onboard_agent.update_status(AgentState.STATUS_ONBOARDING)
                agent_info.assignment_thread = onboard_thread
                onboard_thread.start()
                return

        # Not onboarding, so just register directly
        self._assign_unit_to_agent(packet, channel_info, units)

    def _get_init_data(self, packet, channel_info: ChannelInfo):
        """Get the initialization data for the assigned agent's task"""
        task_runner = channel_info.job.task_runner
        agent_id = packet.data["provider_data"]["agent_id"]
        agent_info = self.agents[agent_id]
        assert isinstance(
            agent_info.agent, Agent
        ), f"Can only get init unit data for Agents, not OnboardingAgents, got {agent_info}"
        unit_data = task_runner.get_init_data_for_agent(agent_info.agent)

        agent_data_packet = Packet(
            packet_type=PACKET_TYPE_INIT_DATA,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=channel_info.channel_id,
            data={"request_id": packet.data["request_id"], "init_data": unit_data},
        )

        self.message_queue.append(agent_data_packet)

        if isinstance(unit_data, dict) and unit_data.get("raw_messages") is not None:
            # TODO bring these into constants somehow
            for message in unit_data["raw_messages"]:
                packet = Packet.from_dict(message)
                packet.receiver_id = agent_id
                agent_info.agent.pending_observations.append(packet)

    @staticmethod
    def _log_frontend_error(packet):
        error = packet.data["final_data"]
        logger.info(f"[FRONT_END_ERROR]: {error}")

    def _on_message(self, packet: Packet, channel_info: ChannelInfo):
        """Handle incoming messages from the channel"""
        # TODO(#102) this method currently assumes that the packet's sender_id will
        # always be a valid agent in our list of agent_infos. At the moment this
        # is a valid assumption, but will not be on recovery from catastrophic failure.
        if packet.type == PACKET_TYPE_AGENT_ACTION:
            self._on_act(packet, channel_info)
        elif packet.type == PACKET_TYPE_NEW_AGENT:
            self._register_agent(packet, channel_info)
        elif packet.type == PACKET_TYPE_SUBMIT_ONBOARDING:
            self._on_submit_onboarding(packet, channel_info)
        elif packet.type == PACKET_TYPE_NEW_WORKER:
            self._register_worker(packet, channel_info)
        elif packet.type == PACKET_TYPE_GET_INIT_DATA:
            self._get_init_data(packet, channel_info)
        elif packet.type == PACKET_TYPE_RETURN_AGENT_STATUS:
            # Record this status response
            self._handle_updated_agent_status(packet.data)
        elif packet.type == PACKET_TYPE_ERROR_LOG:
            self._log_frontend_error(packet)
        else:
            # PACKET_TYPE_REQUEST_AGENT_STATUS, PACKET_TYPE_ALIVE,
            # PACKET_TYPE_INIT_DATA
            raise Exception(f"Unexpected packet type {packet.type}")

    # TODO(#103) maybe batching these is better?
    def _try_send_agent_messages(self, agent_info: AgentInfo):
        """Handle sending any possible messages for a specific agent"""
        channel_info = self.channels[agent_info.used_channel_id]
        agent = agent_info.agent
        while len(agent.pending_observations) > 0:
            curr_obs = agent.pending_observations.pop(0)
            did_send = channel_info.channel.send(curr_obs)
            if not did_send:
                logger.error(f"Failed to send packet {curr_obs} to {channel_info}")
                agent.pending_observations.insert(0, curr_obs)
                return  # something up with the channel, try later

    def _send_message_queue(self) -> None:
        """Send all of the messages in the system queue"""
        while len(self.message_queue) > 0:
            curr_obs = self.message_queue.pop(0)
            channel = self.channels[curr_obs.receiver_id].channel
            did_send = channel.send(curr_obs)
            if not did_send:
                logger.error(
                    f"Failed to send packet {curr_obs} to server {curr_obs.receiver_id}"
                )
                self.message_queue.insert(0, curr_obs)
                return  # something up with the channel, try later

    def _send_status_update(self, agent_info: AgentInfo) -> None:
        """
        Handle telling the frontend agent about a change in their
        active status. (Pushing a change in AgentState)
        """
        status = agent_info.agent.db_status
        if isinstance(agent_info.agent, OnboardingAgent):
            if status in [AgentState.STATUS_APPROVED, AgentState.STATUS_REJECTED]:
                # We don't expose the updated status directly to the frontend here
                # Can be simplified if we improve how bootstrap-chat handles
                # the transition of onboarding states
                status = AgentState.STATUS_WAITING
        send_packet = Packet(
            packet_type=PACKET_TYPE_UPDATE_AGENT_STATUS,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=agent_info.agent.get_agent_id(),
            data={
                "status": status,
                "state": {
                    "done_text": STATUS_TO_TEXT_MAP.get(status),
                    "task_done": status == AgentState.STATUS_PARTNER_DISCONNECT,
                },
            },
        )
        channel_info = self.channels[agent_info.used_channel_id]
        channel_info.channel.send(send_packet)

    def _mark_agent_done(self, agent_info: AgentInfo) -> None:
        """
        Handle marking an agent as done, and telling the frontend agent
        that they have successfully completed their task.

        If the agent is in a final non-successful status, or already
        told of partner disconnect, skip
        """
        if agent_info.agent.db_status in AgentState.complete() + [
            AgentState.STATUS_PARTNER_DISCONNECT
        ]:
            return
        send_packet = Packet(
            packet_type=PACKET_TYPE_UPDATE_AGENT_STATUS,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=agent_info.agent.get_agent_id(),
            data={
                "status": "completed",
                "state": {
                    "done_text": "You have completed this task. Please submit.",
                    "task_done": True,
                },
            },
        )
        channel_info = self.channels[agent_info.used_channel_id]
        channel_info.channel.send(send_packet)

    def _handle_updated_agent_status(self, status_map: Dict[str, str]):
        """
        Handle updating the local statuses for agents based on
        the previously reported agent statuses.

        Takes as input a mapping from agent_id to server-side status
        """
        for agent_id, status in status_map.items():
            if status not in AgentState.valid():
                logger.warning(f"Invalid status for agent {agent_id}: {status}")
                continue
            if agent_id not in self.agents:
                # no longer tracking agent
                continue
            agent = self.agents[agent_id].agent
            db_status = agent.get_status()
            if agent.has_updated_status.is_set():
                continue  # Incoming info may be stale if we have new info to send
            if status != db_status:
                if status == AgentState.STATUS_COMPLETED:
                    # Frontend agent completed but hasn't confirmed yet
                    continue
                if status != AgentState.STATUS_DISCONNECT:
                    # Stale or reconnect, send a status update
                    self._send_status_update(self.agents[agent_id])
                    continue  # Only DISCONNECT can be marked remotely, rest are mismatch (except STATUS_COMPLETED)
                agent.update_status(status)
        pass

    def _request_action(self, agent_info: AgentInfo) -> None:
        """
        Request an act from the agent targetted here. If the
        agent is found by the server, this request will be
        forwarded.
        """
        send_packet = Packet(
            packet_type=PACKET_TYPE_REQUEST_ACTION,
            sender_id=SYSTEM_CHANNEL_ID,
            receiver_id=agent_info.agent.get_agent_id(),
            data={},
        )
        channel_info = self.channels[agent_info.used_channel_id]
        channel_info.channel.send(send_packet)

    def _request_status_update(self) -> None:
        """
        Check last round of statuses, then request
        an update from the server on all agent's current status
        """
        if time.time() - self.last_status_check < STATUS_CHECK_TIME:
            return

        self.last_status_check = time.time()

        for channel_id, channel_info in self.channels.items():
            send_packet = Packet(
                packet_type=PACKET_TYPE_REQUEST_AGENT_STATUS,
                sender_id=SYSTEM_CHANNEL_ID,
                receiver_id=channel_id,
                data={},
            )
            channel_info.channel.send(send_packet)

    def _channel_handling_thread(self) -> None:
        """Thread for handling outgoing messages through the channels"""
        while len(self.channels) > 0:
            current_agents = list(self.agents.values())
            for agent_info in current_agents:
                # Send requests for action
                if agent_info.agent.wants_action.is_set():
                    self._request_action(agent_info)
                    agent_info.agent.wants_action.clear()
                # Pass updated statuses
                if agent_info.agent.has_updated_status.is_set():
                    self._send_status_update(agent_info)
                    agent_info.agent.has_updated_status.clear()
                # clear the message queue for this agent
                self._try_send_agent_messages(agent_info)
            # Send all messages from the system
            self._send_message_queue()
            self._request_status_update()
            # TODO(#103) is there a way we can trigger this when
            # agents observe instead?
            time.sleep(0.1)

    def launch_sending_thread(self) -> None:
        """Launch the sending thread for this supervisor"""
        self.sending_thread = threading.Thread(
            target=self._channel_handling_thread, name=f"channel-sending-thread"
        )
        self.sending_thread.start()
