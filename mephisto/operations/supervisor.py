#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import threading
import time
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import worker_is_qualified
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.abstractions.blueprints.mixins.use_gold_unit import UseGoldUnit
from mephisto.operations.registry import get_crowd_provider_from_type
from mephisto.operations.task_launcher import (
    TaskLauncher,
    SCREENING_UNIT_INDEX,
    GOLD_UNIT_INDEX,
)
from mephisto.operations.datatypes import LiveTaskRun, ChannelInfo, AgentInfo
from mephisto.abstractions.channel import Channel, STATUS_CHECK_TIME

from typing import Dict, Set, Optional, List, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import TaskRunner

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)

# This class manages communications between the server
# and workers, ensures that their status is properly tracked,
# and also provides some helping utility functions for
# groups of workers or worker/agent compatibility.

# Mostly, the supervisor oversees the communications
# between LiveTaskRuns and workers over the channels


class Supervisor:
    def __init__(self, db: "MephistoDB"):
        self.db = db
        # Tracked worker state
        self.agents: Dict[str, AgentInfo] = {}
        # Agent status handling
        self.last_status_check = time.time()
        self.live_runs: Dict[str, "LiveTaskRun"] = {}
        # TODO this should be in the part tracking agent status
        self.agent_status_thread: Optional[threading.Thread] = None
        self.is_shutdown = False

    def register_run(self, live_run: "LiveTaskRun") -> "LiveTaskRun":
        """Register the channels for a LiveTaskRun with this supervisor"""
        task_run = live_run.task_run
        self.live_runs[task_run.db_id] = live_run
        live_run.client_io.launch_channels(live_run, self)
        return live_run

    def shutdown(self) -> None:
        """Close all of the channels, join threads"""
        # Prepopulate agents and channels to close, as
        # these may change during iteration
        # Closing IO handling state
        self.is_shutdown = True
        runs_to_close = list(self.live_runs.keys())
        logger.debug(f"Ending runs {runs_to_close}")
        # TODO runs are started in operator, and should be closed there
        for run_id in runs_to_close:
            self.live_runs[run_id].task_runner.shutdown()
            self.live_runs[run_id].client_io.shutdown()

        logger.debug(f"Joining send thread")
        if self.agent_status_thread is not None:
            self.agent_status_thread.join()
        # Closing unit executions
        logger.debug(f"Joining agents {self.agents}")
        agents_to_close = list(self.agents.values())
        for agent_info in agents_to_close:
            assign_thread = agent_info.assignment_thread
            if assign_thread is not None:
                assign_thread.join()

    def register_worker(
        self, crowd_data: Dict[str, Any], request_id: str, temp_live_run
    ) -> None:
        """Process a worker registration to register a worker"""
        # TODO remove temp_live_run when this is in the worker pool, which is registered to a run
        crowd_provider = temp_live_run.provider
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

        if not worker_is_qualified(worker, temp_live_run.qualifications):
            temp_live_run.client_io.send_provider_details(
                request_id, {"worker_id": None}
            )
        else:
            temp_live_run.client_io.send_provider_details(
                request_id, {"worker_id": worker.db_id}
            )

    def _launch_and_run_onboarding(
        self, agent_info: "AgentInfo", task_runner: "TaskRunner"
    ) -> None:
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

            # TODO clean this up when splitting out unit executor
            live_run = self.agent_info_to_live_run(agent_info)
            del live_run.client_io.onboarding_packets[onboarding_id]

    def _launch_and_run_assignment(
        self,
        assignment: "Assignment",
        agent_infos: List["AgentInfo"],
        task_runner: "TaskRunner",
    ) -> None:
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
    ) -> None:
        """Launch a thread to supervise the completion of an assignment"""
        agent = agent_info.agent
        try:
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
            if unit.unit_index in [SCREENING_UNIT_INDEX, GOLD_UNIT_INDEX]:
                if agent.get_status() != AgentState.STATUS_COMPLETED:
                    if unit.unit_index == SCREENING_UNIT_INDEX:
                        blueprint = task_runner.task_run.get_blueprint(
                            args=task_runner.args
                        )
                        assert isinstance(blueprint, ScreenTaskRequired)
                        blueprint.screening_units_launched -= 1
                    unit.expire()
            task_runner.task_run.clear_reservation(unit)
        return None

    def _assign_unit_to_agent(
        self, crowd_data: Dict[str, Any], request_id: str, units: List["Unit"]
    ):
        # TODO ew this needs a fix once this is in the worker_pool
        live_run = self.live_runs[units[0].get_task_run().db_id]
        task_run = live_run.task_run
        crowd_provider = live_run.provider
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
            live_run.client_io.send_provider_details(request_id, {"agent_id": None})
        else:
            agent = crowd_provider.AgentClass.new_from_provider_data(
                self.db, worker, unit, crowd_data
            )
            live_run.client_io.register_agent_from_request_id(
                agent.get_agent_id(),
                request_id,
                crowd_data["agent_registration_id"],
            )
            logger.debug(f"Created agent {agent}, {agent.db_id}.")
            live_run.client_io.send_provider_details(
                request_id, {"agent_id": agent.get_agent_id()}
            )
            agent_info = AgentInfo(agent=agent)
            self.agents[agent.get_agent_id()] = agent_info

            # Launch individual tasks
            if unit.unit_index < 0 or not live_run.task_runner.is_concurrent:
                unit_thread = threading.Thread(
                    target=self._launch_and_run_unit,
                    args=(unit, agent_info, live_run.task_runner),
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

                # Launch the backend for this assignment
                agent_infos = [self.agents[a.db_id] for a in agents if a is not None]

                assign_thread = threading.Thread(
                    target=self._launch_and_run_assignment,
                    args=(assignment, agent_infos, live_run.task_runner),
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

        live_run = self.agent_info_to_live_run(onboarding_agent_info)
        blueprint = live_run.blueprint
        worker = onboarding_agent.get_worker()

        assert (
            isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding
        ), "Should only be registering from onboarding if onboarding is required and set"
        worker_passed = blueprint.validate_onboarding(worker, onboarding_agent)
        assert blueprint.onboarding_qualification_name is not None
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
        units = live_run.task_run.get_valid_units_for_worker(worker)
        usable_units = live_run.task_runner.filter_units_for_worker(units, worker)

        if not worker_passed:
            # TODO(WISH) it may be worth investigating launching a dummy task for these
            # instances where a worker has failed onboarding, but the onboarding
            # task still allowed submission of the failed data (no front-end validation)
            # units = [self.dummy_launcher.launch_dummy()]
            # self._assign_unit_to_agent(..., units)
            usable_units = []

        # TODO refactor with worker pool
        crowd_data, request_id = live_run.client_io.onboarding_packets[
            onboarding_agent.get_agent_id()
        ]
        self._try_send_agent_messages(onboarding_agent_info)
        # TODO is this status update necessary?
        self._send_status_update(onboarding_agent_info)
        if len(usable_units) == 0:
            live_run.client_io.send_provider_details(request_id, {"agent_id": None})
        else:
            self._assign_unit_to_agent(crowd_data, request_id, usable_units)

    def register_agent(
        self, crowd_data: Dict[str, Any], request_id: str, temp_live_run
    ):
        """Process an agent registration packet to register an agent, returning the agent_id"""
        # Process a new agent
        live_run = temp_live_run
        task_run = live_run.task_run
        agent_registration_id = crowd_data["agent_registration_id"]
        worker_id = crowd_data["worker_id"]
        worker = Worker.get(self.db, worker_id)

        # get the list of tentatively valid units
        units = task_run.get_valid_units_for_worker(worker)
        if len(units) == 0:
            live_run.client_io.send_provider_details(request_id, {"agent_id": None})
            logger.debug(
                f"agent_registration_id {agent_registration_id}, had no valid units."
            )
            return

        # If there's onboarding, see if this worker has already been disqualified
        worker = Worker.get(self.db, worker_id)
        blueprint = live_run.blueprint
        if isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding:
            print(
                "Disqualified?",
                worker.is_disqualified(blueprint.onboarding_qualification_name),
            )
            if worker.is_disqualified(blueprint.onboarding_qualification_name):
                live_run.client_io.send_provider_details(request_id, {"agent_id": None})
                logger.debug(
                    f"Worker {worker_id} is already disqualified by onboarding "
                    f"qual {blueprint.onboarding_qualification_name}."
                )
                return
            elif not worker.is_qualified(blueprint.onboarding_qualification_name):
                # Send a packet with onboarding information
                onboard_data = blueprint.get_onboarding_data(worker.db_id)
                onboard_agent = OnboardingAgent.new(self.db, worker, task_run)
                live_run.client_io.register_agent_from_request_id(
                    onboard_agent.get_agent_id(),
                    request_id,
                    crowd_data["agent_registration_id"],
                )
                onboard_agent.state.set_init_state(onboard_data)
                agent_info = AgentInfo(agent=onboard_agent)
                onboard_id = onboard_agent.get_agent_id()
                # register onboarding agent
                self.agents[onboard_id] = agent_info

                # TODO move when worker_pool is done
                live_run.client_io.onboarding_packets[onboard_id] = (
                    crowd_data,
                    request_id,
                )
                live_run.client_io.send_provider_details(
                    request_id,
                    {
                        "agent_id": onboard_id,
                        "onboard_data": onboard_data,
                    },
                )
                logger.debug(
                    f"{worker} is starting onboarding thread with "
                    f"onboarding {onboard_agent}."
                )

                # Create an onboarding thread
                onboard_thread = threading.Thread(
                    target=self._launch_and_run_onboarding,
                    args=(agent_info, live_run.task_runner),
                    name=f"Onboard-thread-{onboard_id}",
                )

                onboard_agent.update_status(AgentState.STATUS_ONBOARDING)
                agent_info.assignment_thread = onboard_thread
                onboard_thread.start()
                return
        if isinstance(blueprint, ScreenTaskRequired) and blueprint.use_screening_task:
            if (
                blueprint.worker_needs_screening(worker)
                and blueprint.should_generate_unit()
            ):
                screening_data = blueprint.get_screening_unit_data()
                if screening_data is not None:
                    launcher = live_run.task_launcher
                    assert (
                        launcher is not None
                    ), "LiveTaskRun must have launcher to use screening tasks"
                    units = [launcher.launch_screening_unit(screening_data)]
                else:
                    live_run.client_io.send_provider_details(
                        request_id, {"agent_id": None}
                    )
                    logger.debug(
                        f"No screening units left for {agent_registration_id}."
                    )
                    return
        if isinstance(blueprint, UseGoldUnit) and blueprint.use_golds:
            if blueprint.should_produce_gold_for_worker(worker):
                gold_data = blueprint.get_gold_unit_data_for_worker(worker)
                if gold_data is not None:
                    launcher = live_run.task_launcher
                    units = [launcher.launch_gold_unit(gold_data)]
                else:
                    live_run.client_io.send_provider_details(
                        request_id, {"agent_id": None}
                    )
                    logger.debug(f"No gold units left for {agent_registration_id}...")
                    return

        # Not onboarding, so just register directly
        self._assign_unit_to_agent(crowd_data, request_id, units)

    def _try_send_agent_messages(self, agent_info: AgentInfo):
        """Handle sending any possible messages for a specific agent"""
        live_run = self.agent_info_to_live_run(agent_info)
        live_run.client_io.send_message_queue(agent_info.agent.pending_observations)

    def _send_status_update(self, agent_info: AgentInfo) -> None:
        """
        Handle telling the frontend agent about a change in their
        active status. (Pushing a change in AgentState)
        """
        # TODO deprecate, have status updates trigger sends automatically
        status = agent_info.agent.db_status
        if isinstance(agent_info.agent, OnboardingAgent):
            if status in [AgentState.STATUS_APPROVED, AgentState.STATUS_REJECTED]:
                # We don't expose the updated status directly to the frontend here
                # Can be simplified if we improve how bootstrap-chat handles
                # the transition of onboarding states
                status = AgentState.STATUS_WAITING

        live_run = self.agent_info_to_live_run(agent_info)
        live_run.client_io.send_status_update(agent_info.agent.get_agent_id(), status)

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
            return  # Don't send done messages to agents that are already completed

        live_run = self.agent_info_to_live_run(agent_info)
        live_run.client_io.send_done_message(agent_info.agent.db_id)

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

    def _agent_status_handling_thread(self) -> None:
        """Thread for polling and pushing agent statuses"""
        # TODO rather than polling repeatedly for these, can we use
        # awaits and only trigger this loop when something is ready?
        while not self.is_shutdown:
            current_agents = list(self.agents.values())
            for agent_info in current_agents:
                live_run = self.agent_info_to_live_run(agent_info)
                # Send requests for action
                if agent_info.agent.wants_action.is_set():
                    live_run.client_io.request_action(agent_info.agent.get_agent_id())
                    agent_info.agent.wants_action.clear()
                # Pass updated statuses
                if agent_info.agent.has_updated_status.is_set():
                    self._send_status_update(agent_info)
                    agent_info.agent.has_updated_status.clear()
                # clear the message queue for this agent
                self._try_send_agent_messages(agent_info)
            time.sleep(0.1)

    def launch_sending_thread_deprecated(self) -> None:
        """Launch the sending thread for this supervisor"""
        # TODO move to agent handler
        self.agent_status_thread = threading.Thread(
            target=self._agent_status_handling_thread, name=f"agent-status-thread"
        )
        self.agent_status_thread.start()

    def agent_info_to_live_run(self, agent_info: AgentInfo) -> LiveTaskRun:
        """Temporary helper to extract the live run for an agent info"""
        # This should be replaced by having the separate agents aware of the
        # live run they belong to
        task_run = agent_info.agent.get_task_run()
        return self.live_runs[task_run.db_id]
