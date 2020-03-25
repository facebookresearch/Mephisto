#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import errno
import logging
import json
import threading
import time
from queue import PriorityQueue, Empty
import websocket
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
)
from mephisto.data_model.worker import Worker
from mephisto.data_model.blueprint import OnboardingRequired, AgentState
from mephisto.core.utils import get_crowd_provider_from_type

from recordclass import RecordClass

from typing import Dict, Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent, Unit
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import TaskRunner
    from mephisto.data_model.crowd_provider import CrowdProvider
    from mephisto.data_model.architect import Architect

# This class manages communications between the server
# and workers, ensures that their status is properly tracked,
# and also provides some helping utility functions for
# groups of workers or worker/agent compatibility.

# Mostly, the supervisor babysits the socket and the workers

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

SYSTEM_SOCKET_ID = "mephisto"  # TODO pull from somewhere
STATUS_CHECK_TIME = 4
START_DEATH_TIME = 10

# State storage
class Job(RecordClass):
    architect: "Architect"
    task_runner: "TaskRunner"
    provider: "CrowdProvider"
    registered_socket_ids: List[str]


class SocketInfo(RecordClass):
    socket_id: str
    url: str
    job: "Job"
    is_closed: bool = False
    is_alive: bool = False
    socket: Optional[websocket.WebSocketApp] = None
    thread: Optional[threading.Thread] = None


class AgentInfo(RecordClass):
    agent: "Agent"
    used_socket_id: str
    assignment_thread: Optional[threading.Thread] = None


class Supervisor:
    def __init__(self, db: "MephistoDB"):
        self.db = db
        # Tracked state
        self.agents: Dict[str, AgentInfo] = {}
        self.agents_by_registration_id: Dict[str, AgentInfo] = {}
        self.sockets: Dict[str, SocketInfo] = {}
        self.socket_count = 0

        # Agent status handling
        self.status_responses: Dict[str, Dict[str, Any]] = {}
        self.last_status_check = time.time()

        # Message handling
        self.message_queue: List[Packet] = []
        self.sending_thread: Optional[threading.Thread] = None

    def register_job(
        self,
        architect: "Architect",
        task_runner: "TaskRunner",
        provider: "CrowdProvider",
    ):
        task_run = task_runner.task_run
        urls = architect.get_socket_urls()
        job = Job(
            architect=architect,
            task_runner=task_runner,
            provider=provider,
            registered_socket_ids=[],
        )
        for url in urls:
            socket_id = self.setup_socket(url, job)
            job.registered_socket_ids.append(socket_id)
        return job

    def setup_socket(self, url: str, job: "Job") -> str:
        """Set up a socket communicating with the server at the given url"""
        # Clear status_responses, as we won't have one for this server
        self.status_responses = {}

        socket_name = f"socket_{self.socket_count}"
        self.socket_count += 1

        socket_info = SocketInfo(socket_id=socket_name, url=url, job=job)
        self.sockets[socket_name] = socket_info

        def on_socket_open(*args):
            socket_info.is_alive = True
            self._send_alive(socket_info)
            # TODO use logger?
            print(f"socket open {args}")

        def on_error(ws, error):
            if hasattr(error, "errno"):
                if error.errno == errno.ECONNREFUSED:
                    raise Exception(f"Socket {url} refused connection, cancelling")
            else:
                print(f"Socket logged error: {error}")
                try:
                    ws.close()
                except Exception:
                    # Already closed
                    pass

        def on_disconnect(*args):
            """Disconnect event is a no-op for us, as the server reconnects
            automatically on a retry.
            """
            # TODO we need to set a timeout for reconnecting to the server
            pass

        def on_message(*args):
            """Incoming message handler defers to the internal handler
            """
            try:
                packet_dict = json.loads(args[1])
                packet = Packet.from_dict(packet_dict)
                self._on_message(packet, socket_info)
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(repr(e))
                raise

        def run_socket(*args):
            while (
                socket_name in self.sockets and not self.sockets[socket_name].is_closed
            ):
                try:
                    socket = websocket.WebSocketApp(
                        url,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_disconnect,
                    )
                    self.sockets[socket_name].socket = socket
                    socket.on_open = on_socket_open
                    socket.run_forever(ping_interval=8 * STATUS_CHECK_TIME)
                except Exception as e:
                    print(f"Socket error {repr(e)}, attempting restart")
                time.sleep(0.2)

        # Start listening thread
        socket_info.thread = threading.Thread(
            target=run_socket, name=f"socket-thread-{url}"
        )
        socket_info.thread.start()
        start_time = time.time()
        while not socket_info.is_alive:
            if time.time() - start_time > START_DEATH_TIME:
                # TODO better handle failing to connect with the server
                self.sockets[socket_name].is_closed = True
                raise ConnectionRefusedError(  # noqa F821 we only support py3
                    "Was not able to establish a connection with the server, "
                    "please try to run again. If that fails,"
                    "please ensure that your local device has the correct SSL "
                    "certs installed."
                )
            try:
                self._send_alive(socket_info)
            except Exception:
                pass
            time.sleep(0.3)
        return socket_name

    def close_socket(self, socket_id: str):
        """Close the given socket by id"""
        socket_info = self.sockets[socket_id]
        socket_info.is_closed = True
        if socket_info.socket is not None:
            socket_info.socket.close()
        socket_info.is_alive = False
        if socket_info.thread is not None:
            socket_info.thread.join()
        del self.sockets[socket_id]

    def shutdown_job(self, job: Job):
        """Close any sockets related to a job"""
        job_sockets = job.registered_socket_ids
        for socket_id in job_sockets:
            self.close_socket(socket_id)

    def shutdown(self):
        """Close all of the sockets, join their threads"""
        sockets_to_close = list(self.sockets.keys())
        for socket_id in sockets_to_close:
            self.close_socket(socket_id)
        if self.sending_thread is not None:
            self.sending_thread.join()

    def _send_through_socket(
        self, socket: websocket.WebSocketApp, packet: Packet
    ) -> bool:
        """Send a packet through the socket, handle any errors"""
        if socket is None:
            return False
        try:
            data = packet.to_sendable_dict()
            socket.send(json.dumps(data))
        except websocket.WebSocketConnectionClosedException:
            # The channel died mid-send, wait for it to come back up
            return False
        except BrokenPipeError:
            # The channel died mid-send, wait for it to come back up
            return False
        except Exception as e:
            import traceback

            traceback.print_exc()
            print("Unexpected socket error occured: {}".format(repr(e)))
            return False
        return True

    def _send_alive(self, socket_info: SocketInfo) -> bool:
        print("sending alive")
        return self._send_through_socket(
            socket_info.socket,
            Packet(
                packet_type=PACKET_TYPE_ALIVE,
                sender_id=SYSTEM_SOCKET_ID,
                receiver_id=socket_info.socket_id,
            ),
        )

    def _on_act(self, packet: Packet, socket_info: SocketInfo):
        """Handle an action as sent from an agent"""
        agent = self.agents[packet.sender_id].agent

        # If the packet is_submit, and has files, we need to
        # process downloading those files first
        if packet.data.get("MEPHISTO_is_submit") is True:
            data_files = packet.data.get("files")
            if data_files is not None:
                save_dir = agent.get_data_dir()
                architect = socket_info.job.architect
                for f_obj in data_files:
                    architect.download_file(f_obj["filename"], save_dir)

        agent.pending_actions.append(packet)
        agent.has_action.set()

    def _register_worker(self, packet: Packet, socket_info: SocketInfo):
        """Process a worker registration packet to register a worker"""
        crowd_data = packet.data["provider_data"]
        crowd_provider = socket_info.job.provider
        worker_name = crowd_data["worker_name"]
        workers = self.db.find_workers(worker_name=worker_name)
        if len(workers) == 0:
            # TODO get rid of sandbox designation
            workers = self.db.find_workers(worker_name=worker_name + "_sandbox")
        if len(workers) == 0:
            worker = crowd_provider.WorkerClass.new_from_provider_data(
                self.db, crowd_data
            )
        else:
            worker = workers[0]
        # TODO any sort of processing to see if this worker is blocked from the provider side?
        self.message_queue.append(
            Packet(
                packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                sender_id=SYSTEM_SOCKET_ID,
                receiver_id=socket_info.socket_id,
                data={
                    "request_id": packet.data["request_id"],
                    "worker_id": worker.db_id,
                },
            )
        )

    def _launch_and_run_assignment(
        self,
        assignment: "Assignment",
        agent_infos: List["AgentInfo"],
        task_runner: "TaskRunner",
    ):
        """Launch a thread to supervise the completion of an assignment"""
        try:
            tracked_agents = [a.agent for a in agent_infos]
            task_runner.launch_assignment(assignment, tracked_agents)
            for agent_info in agent_infos:
                self._mark_agent_done(agent_info)
            # Wait for agents to be complete
            for agent_info in agent_infos:
                agent = agent_info.agent
                if not agent.did_submit.is_set():
                    # Wait for a submit to occur
                    # TODO make submit timeout configurable
                    agent.has_action.wait(timeout=300)
                    agent.act()
                agent.mark_done()
        except Exception as e:
            import traceback

            traceback.print_exc()
            # TODO handle runtime exceptions for assignments
            task_runner.cleanup_assignment(assignment)

    def _launch_and_run_unit(
        self, unit: "Unit", agent_info: "AgentInfo", task_runner: "TaskRunner"
    ):
        """Launch a thread to supervise the completion of an assignment"""
        try:
            agent = agent_info.agent
            task_runner.launch_unit(unit, agent)
            self._mark_agent_done(agent_info)
            if not agent.did_submit.is_set():
                # Wait for a submit to occur
                # TODO make submit timeout configurable
                agent.has_action.wait(timeout=300)
                agent.act()
            agent.mark_done()
        except Exception as e:
            import traceback

            traceback.print_exc()
            # TODO handle runtime exceptions for assignments
            task_runner.cleanup_unit(unit)

    def _assign_unit_to_agent(
        self, packet: Packet, socket_info: SocketInfo, units: List["Unit"]
    ):
        """Handle creating an agent for the specific worker to register an agent"""
        crowd_data = packet.data["provider_data"]
        task_run = socket_info.job.task_runner.task_run
        crowd_provider = socket_info.job.provider
        worker_id = crowd_data["worker_id"]
        worker = Worker(self.db, worker_id)

        reserved_unit = None
        while len(units) > 0 and reserved_unit is None:
            unit = units.pop(0)
            reserved_unit = task_run.reserve_unit(unit)
        if reserved_unit is None:
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_SOCKET_ID,
                    receiver_id=socket_info.socket_id,
                    data={"request_id": packet.data["request_id"], "agent_id": None},
                )
            )
        else:
            agent = crowd_provider.AgentClass.new_from_provider_data(
                self.db, worker, unit, crowd_data
            )
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_SOCKET_ID,
                    receiver_id=socket_info.socket_id,
                    data={
                        "request_id": packet.data["request_id"],
                        "agent_id": agent.db_id,
                    },
                )
            )
            agent_info = AgentInfo(agent=agent, used_socket_id=socket_info.socket_id)
            self.agents[agent.db_id] = agent_info
            self.agents_by_registration_id[
                crowd_data["agent_registration_id"]
            ] = agent_info

            # TODO is this a safe enough place to un-reserve?
            task_run.clear_reservation(unit)

            # Launch individual tasks
            if not socket_info.job.task_runner.is_concurrent:
                unit_thread = threading.Thread(
                    target=self._launch_and_run_unit,
                    args=(unit, agent_info, socket_info.job.task_runner),
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
                    args=(assignment, agent_infos, socket_info.job.task_runner),
                    name=f"Assignment-thread-{assignment.db_id}",
                )

                for agent_info in agent_infos:
                    agent_info.agent.update_status(AgentState.STATUS_IN_TASK)
                    agent_info.assignment_thread = assign_thread

                assign_thread.start()

    def _register_agent_from_onboarding(self, packet: Packet, socket_info: SocketInfo):
        """Register an agent that has finished onboarding"""
        task_runner = socket_info.job.task_runner
        task_run = task_runner.task_run
        blueprint = task_run.get_blueprint()
        crowd_data = packet.data["provider_data"]
        worker_id = crowd_data["worker_id"]
        worker = Worker(self.db, worker_id)

        assert (
            isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding
        ), "Should only be registering from onboarding if onboarding is required and set"
        worker_passed = blueprint.validate_onboarding(
            worker, packet.data["onboard_data"]
        )
        worker.qualify(blueprint.onboarding_qualification_name, int(worker_passed))
        # TODO we should save the onboarding data to be able to review later?

        if not worker_passed:
            # TODO it may be worth investigating launching a dummy task for these
            # instances where a worker has failed onboarding, but the onboarding
            # task still allowed submission of the failed data (no front-end validation)
            # units = [self.dummy_launcher.launch_dummy()]
            # self._assign_unit_to_agent(packet, socket_info, units)
            pass

        # get the list of tentatively valid units
        units = task_run.get_valid_units_for_worker(worker)
        self._assign_unit_to_agent(packet, socket_info, units)

    def _register_agent(self, packet: Packet, socket_info: SocketInfo):
        """Process an agent registration packet to register an agent"""
        # First see if this is a reconnection
        crowd_data = packet.data["provider_data"]
        agent_registration_id = crowd_data["agent_registration_id"]
        if agent_registration_id in self.agents_by_registration_id:
            agent = self.agents_by_registration_id[agent_registration_id].agent
            # Update the source socket, in case it has changed
            self.agents[agent.db_id].used_socket_id = socket_info.socket_id
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_SOCKET_ID,
                    receiver_id=socket_info.socket_id,
                    data={
                        "request_id": packet.data["request_id"],
                        "agent_id": agent.db_id,
                    },
                )
            )
            return

        # Process a new agent
        task_run = socket_info.job.task_runner.task_run
        worker_id = crowd_data["worker_id"]
        worker = Worker(self.db, worker_id)

        # get the list of tentatively valid units
        # TODO handle any extra qualifications filtering
        units = task_run.get_valid_units_for_worker(worker)
        if len(units) == 0:
            self.message_queue.append(
                Packet(
                    packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                    sender_id=SYSTEM_SOCKET_ID,
                    receiver_id=socket_info.socket_id,
                    data={"request_id": packet.data["request_id"], "agent_id": None},
                )
            )

        # If there's onboarding, see if this worker has already been disqualified
        worker_id = crowd_data["worker_id"]
        worker = Worker(self.db, worker_id)
        blueprint = task_run.get_blueprint()
        if isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding:
            if worker.is_disqualified(blueprint.onboarding_qualification_name):
                self.message_queue.append(
                    Packet(
                        packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                        sender_id=SYSTEM_SOCKET_ID,
                        receiver_id=socket_info.socket_id,
                        data={
                            "request_id": packet.data["request_id"],
                            "agent_id": None,
                        },
                    )
                )
                return
            elif not worker.is_qualified(blueprint.onboarding_qualification_name):
                # Send a packet with onboarding information
                # TODO use the agent id request as the agent_id?
                onboard_data = blueprint.get_onboarding_data()
                self.message_queue.append(
                    Packet(
                        packet_type=PACKET_TYPE_PROVIDER_DETAILS,
                        sender_id=SYSTEM_SOCKET_ID,
                        receiver_id=socket_info.socket_id,
                        data={
                            "request_id": packet.data["request_id"],
                            "agent_id": "onboarding",
                            "onboard_data": onboard_data,
                        },
                    )
                )
                return

        # Not onboarding, so just register directly
        self._assign_unit_to_agent(packet, socket_info, units)

    def _get_init_data(self, packet, socket_info: SocketInfo):
        """Get the initialization data for the assigned agent's task"""
        task_runner = socket_info.job.task_runner
        agent_id = packet.data["provider_data"]["agent_id"]
        agent_info = self.agents[agent_id]
        unit_data = task_runner.get_init_data_for_agent(agent_info.agent)

        agent_data_packet = Packet(
            packet_type=PACKET_TYPE_INIT_DATA,
            sender_id=SYSTEM_SOCKET_ID,
            receiver_id=socket_info.socket_id,
            data={"request_id": packet.data["request_id"], "init_data": unit_data},
        )
        self.message_queue.append(agent_data_packet)

    def _on_message(self, packet: Packet, socket_info: SocketInfo):
        """Handle incoming messages from the socket"""
        if packet.type == PACKET_TYPE_AGENT_ACTION:
            self._on_act(packet, socket_info)
        elif packet.type == PACKET_TYPE_NEW_AGENT:
            self._register_agent(packet, socket_info)
        elif packet.type == PACKET_TYPE_SUBMIT_ONBOARDING:
            self._register_agent_from_onboarding(packet, socket_info)
        elif packet.type == PACKET_TYPE_NEW_WORKER:
            self._register_worker(packet, socket_info)
        elif packet.type == PACKET_TYPE_GET_INIT_DATA:
            self._get_init_data(packet, socket_info)
        elif packet.type == PACKET_TYPE_RETURN_AGENT_STATUS:
            # Record this status response
            self._handle_updated_agent_status(packet.data)
        else:
            # PACKET_TYPE_REQUEST_AGENT_STATUS, PACKET_TYPE_ALIVE,
            # PACKET_TYPE_INIT_DATA
            raise Exception(f"Unexpected packet type {packet.type}")

    # TODO maybe batching these is better?
    def _try_send_agent_messages(self, agent_info: AgentInfo):
        """Handle sending any possible messages for a specific agent"""
        socket_info = self.sockets[agent_info.used_socket_id]
        agent = agent_info.agent
        while len(agent.pending_observations) > 0:
            curr_obs = agent.pending_observations.pop(0)
            did_send = self._send_through_socket(socket_info.socket, curr_obs)
            if not did_send:
                print(f"Failed to send packet {curr_obs} to {socket_info.url}")
                agent.pending_observations.insert(0, curr_obs)
                return  # something up with the socket, try later

    def _send_message_queue(self) -> None:
        """Send all of the messages in the system queue"""
        while len(self.message_queue) > 0:
            curr_obs = self.message_queue.pop(0)
            socket = self.sockets[curr_obs.receiver_id].socket
            did_send = self._send_through_socket(socket, curr_obs)
            if not did_send:
                print(
                    f"Failed to send packet {curr_obs} to server {curr_obs.receiver_id}"
                )
                self.message_queue.insert(0, curr_obs)
                return  # something up with the socket, try later

    def _send_status_update(self, agent_info: AgentInfo) -> None:
        """
        Handle telling the frontend agent about a change in their
        active status. (Pushing a change in AgentState)
        """
        # TODO call this method on reconnect
        send_packet = Packet(
            packet_type=PACKET_TYPE_UPDATE_AGENT_STATUS,
            sender_id=SYSTEM_SOCKET_ID,
            receiver_id=agent_info.agent.db_id,
            data={
                "agent_status": agent_info.agent.db_status,
                "done_text": STATUS_TO_TEXT_MAP.get(agent_info.agent.db_status),
            },
        )
        socket_info = self.sockets[agent_info.used_socket_id]
        self._send_through_socket(socket_info.socket, send_packet)

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
            sender_id=SYSTEM_SOCKET_ID,
            receiver_id=agent_info.agent.db_id,
            data={
                "agent_status": "completed",
                "done_text": "You have completed this task. Please submit.",
            },
        )
        socket_info = self.sockets[agent_info.used_socket_id]
        self._send_through_socket(socket_info.socket, send_packet)

    def _handle_updated_agent_status(self, status_map: Dict[str, str]):
        """
        Handle updating the local statuses for agents based on
        the previously reported agent statuses.

        Takes as input a mapping from agent_id to server-side status
        """
        for agent_id, status in status_map.items():
            if status not in AgentState.valid():
                # TODO update with logging
                print(f"Invalid status for agent {agent_id}: {status}")
                continue
            if agent_id not in self.agents:
                # no longer tracking agent
                continue
            agent = self.agents[agent_id].agent
            db_status = agent.get_status()
            if agent.has_updated_status.is_set():
                continue  # Incoming info may be stale if we have new info to send
            if status == AgentState.STATUS_NONE:
                # Stale or reconnect, send a status update
                self._send_status_update(self.agents[agent_id])
                continue
            if status != db_status:
                if db_status in AgentState.complete():
                    print(
                        f"Got updated status {status} when already final: {agent.db_status}"
                    )
                    continue
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
            sender_id=SYSTEM_SOCKET_ID,
            receiver_id=agent_info.agent.db_id,
            data={},
        )
        socket_info = self.sockets[agent_info.used_socket_id]
        self._send_through_socket(socket_info.socket, send_packet)

    def _request_status_update(self) -> None:
        """
        Check last round of statuses, then request
        an update from the server on all agent's current status
        """
        if time.time() - self.last_status_check < STATUS_CHECK_TIME:
            return

        self.last_status_check = time.time()

        for socket_id, socket_info in self.sockets.items():
            send_packet = Packet(
                packet_type=PACKET_TYPE_REQUEST_AGENT_STATUS,
                sender_id=SYSTEM_SOCKET_ID,
                receiver_id=socket_id,
                data={},
            )
            self._send_through_socket(socket_info.socket, send_packet)

    def _socket_handling_thread(self) -> None:
        """Thread for handling outgoing messages through the socket"""
        while len(self.sockets) > 0:
            for agent_info in self.agents.values():
                if agent_info.agent.wants_action.is_set():
                    self._request_action(agent_info)
                    agent_info.agent.wants_action.clear()
                if agent_info.agent.has_updated_status.is_set():
                    self._send_status_update(agent_info)
                    agent_info.agent.has_updated_status.clear()
                self._try_send_agent_messages(agent_info)
            self._send_message_queue()
            self._request_status_update()
            # TODO is there a way we can trigger this when
            # agents observe instead?
            time.sleep(0.1)

    def launch_sending_thread(self) -> None:
        """Launch the sending thread for this supervisor"""
        self.sending_thread = threading.Thread(
            target=self._socket_handling_thread, name=f"socket-sending-thread"
        )
        self.sending_thread.start()
