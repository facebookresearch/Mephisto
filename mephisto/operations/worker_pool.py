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
from mephisto.operations.task_launcher import (
    SCREENING_UNIT_INDEX,
    GOLD_UNIT_INDEX,
)
from mephisto.operations.datatypes import LiveTaskRun, AgentInfo

from typing import Dict, Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


class WorkerPool:
    """
    The WorkerPool is responsible for tracing the status and state of workers
    and agents that are actively engaged in Mephisto tasks for a given task run. It is
    responsible for delegating to other classes and controllers on particular status
    transitions.
    """

    def __init__(self, db: "MephistoDB"):
        self.db = db
        # Tracked worker state
        self.agents: Dict[str, AgentInfo] = {}
        # Agent status handling
        self.last_status_check = time.time()
        self.agent_status_thread: Optional[threading.Thread] = None

        self.is_shutdown = False

        # Deferred initializiation
        self._live_run: Optional["LiveTaskRun"] = None

    def register_run(self, live_run: "LiveTaskRun") -> None:
        """Register a live run for this worker pool"""
        assert (
            self._live_run is None
        ), "Cannot associate more than one live run to a worker pool at a time"
        self._live_run = live_run

    def register_worker(self, crowd_data: Dict[str, Any], request_id: str) -> None:
        """Process a worker registration to register a worker"""
        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
        crowd_provider = live_run.provider
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

        if not worker_is_qualified(worker, live_run.qualifications):
            live_run.client_io.send_provider_details(request_id, {"worker_id": None})
        else:
            live_run.client_io.send_provider_details(
                request_id, {"worker_id": worker.db_id}
            )

    def _assign_unit_to_agent(
        self, crowd_data: Dict[str, Any], request_id: str, units: List["Unit"]
    ):
        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
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
            agent.set_live_run(live_run)
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
                # TODO could this be moved to the task runner?
                def cleanup_after():
                    if unit.unit_index in [SCREENING_UNIT_INDEX, GOLD_UNIT_INDEX]:
                        if agent.get_status() != AgentState.STATUS_COMPLETED:
                            if unit.unit_index == SCREENING_UNIT_INDEX:
                                blueprint = live_run.task_run.get_blueprint(
                                    args=live_run.task_runner.args
                                )
                                assert isinstance(blueprint, ScreenTaskRequired)
                                blueprint.screening_units_launched -= 1
                            unit.expire()

                # Create an onboarding thread
                unit_thread = live_run.task_runner.execute_unit(
                    unit,
                    agent,
                    lambda: self._mark_agent_done(agent_info),
                    cleanup_after,
                )
                agent_info.assignment_thread = unit_thread
            else:
                # See if the concurrent unit is ready to launch
                assignment = unit.get_assignment()
                agents = assignment.get_agents()
                if None in agents:
                    agent.update_status(AgentState.STATUS_WAITING)
                    return  # need to wait for all agents to be here to launch

                non_null_agents = [a for a in agents if a is not None]
                # Launch the backend for this assignment
                agent_infos = [
                    self.agents[a.db_id] for a in non_null_agents if a is not None
                ]
                registered_agents = [
                    a.agent for a in agent_infos if isinstance(a.agent, Agent)
                ]

                def mark_agents_done():
                    for agent_info in agent_infos:
                        self._mark_agent_done(agent_info)

                assign_thread = live_run.task_runner.execute_assignment(
                    assignment, registered_agents, mark_agents_done
                )

                for agent_info in agent_infos:
                    agent_info.assignment_thread = assign_thread

    def register_agent_from_onboarding(self, onboarding_agent: "OnboardingAgent"):
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

        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
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
        self.send_status_update_deprecated(onboarding_agent_info)
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
                onboard_agent.set_live_run(live_run)
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

                def cleanup_onboarding():
                    del self.agents[onboard_id]
                    del live_run.client_io.onboarding_packets[onboard_id]

                # Create an onboarding thread
                onboard_thread = live_run.task_runner.execute_onboarding(
                    onboard_agent, cleanup_onboarding
                )
                agent_info.assignment_thread = onboard_thread
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
        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
        live_run.client_io.send_message_queue(agent_info.agent.pending_observations)

    def send_status_update_deprecated(self, agent_info: AgentInfo) -> None:
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

        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
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

        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
        live_run.client_io.send_done_message(agent_info.agent.db_id)

    def handle_updated_agent_status(self, status_map: Dict[str, str]):
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
                    self.send_status_update_deprecated(self.agents[agent_id])
                    continue  # Only DISCONNECT can be marked remotely, rest are mismatch (except STATUS_COMPLETED)
                agent.update_status(status)
        pass

    def _agent_status_handling_thread(self) -> None:
        """Thread for polling and pushing agent statuses"""
        # TODO rather than polling repeatedly for these, can we use
        # awaits and only trigger this loop when something is ready?
        live_run = self._live_run
        assert live_run is not None, "Must have registered a live run first"
        while not self.is_shutdown:
            current_agents = list(self.agents.values())
            for agent_info in current_agents:
                # Send requests for action
                if agent_info.agent.wants_action.is_set():
                    live_run.client_io.request_action(agent_info.agent.get_agent_id())
                    agent_info.agent.wants_action.clear()
                # Pass updated statuses
                if agent_info.agent.has_updated_status.is_set():
                    self.send_status_update_deprecated(agent_info)
                    agent_info.agent.has_updated_status.clear()
                # clear the message queue for this agent
                self._try_send_agent_messages(agent_info)
            time.sleep(0.1)

    def launch_sending_thread_deprecated(self) -> None:
        """Launch the status sending thread for this pool"""
        # TODO deprecate when status is push based
        self.agent_status_thread = threading.Thread(
            target=self._agent_status_handling_thread, name=f"agent-status-thread"
        )
        self.agent_status_thread.start()

    def shutdown(self) -> None:
        """Close all of the channels, join threads"""
        # Prepopulate agents and channels to close, as
        # these may change during iteration
        # Closing IO handling state
        self.is_shutdown = True

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
