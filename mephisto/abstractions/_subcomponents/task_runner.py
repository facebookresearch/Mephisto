#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from mephisto.operations.utils import find_or_create_qualification
from typing import (
    List,
    Dict,
    Callable,
    Tuple,
    TYPE_CHECKING,
)

from omegaconf import DictConfig

from dataclasses import dataclass
from mephisto.data_model.exceptions import (
    AgentReturnedError,
    AgentDisconnectedError,
    AgentTimeoutError,
    AgentShutdownError,
)
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.abstractions._subcomponents.agent_state import AgentState
import threading

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.assignment import Assignment, InitializationData
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.abstractions.blueprint import SharedTaskState

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


@dataclass
class RunningUnit:
    unit: "Unit"
    agent: "Agent"
    thread: threading.Thread


@dataclass
class RunningAssignment:
    assignment: "Assignment"
    agents: List["Agent"]
    thread: threading.Thread


@dataclass
class RunningOnboarding:
    onboarding_agent: "OnboardingAgent"
    thread: threading.Thread


class TaskRunner(ABC):
    """
    Class to manage running a task of a specific type. Includes
    building the dependencies to a directory to be deployed to
    the server, and spawning threads that manage the process of
    passing agents through a task.
    """

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        self.args = args
        self.shared_state = shared_state
        self.task_run = task_run
        self.running_assignments: Dict[str, RunningAssignment] = {}
        self.running_units: Dict[str, RunningUnit] = {}
        self.running_onboardings: Dict[str, RunningOnboarding] = {}
        self.is_concurrent = False
        # TODO(102) populate some kind of local state for tasks that are being run
        # by this runner from the database.

        self.block_qualification = args.blueprint.get("block_qualification", None)
        if self.block_qualification is not None:
            find_or_create_qualification(task_run.db, self.block_qualification)

    def __new__(
        cls, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ) -> "TaskRunner":
        """Get the correct TaskRunner for this task run"""
        if cls == TaskRunner:
            from mephisto.operations.registry import get_blueprint_from_type

            # We are trying to construct an AgentState, find what type to use and
            # create that instead
            correct_class = get_blueprint_from_type(task_run.task_type).TaskRunnerClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def execute_onboarding(
        self, onboarding_agent: "OnboardingAgent", cleanup_after: Callable[[], None]
    ) -> None:
        """Execute onboarding in a background thread"""
        onboarding_id = onboarding_agent.get_agent_id()
        if onboarding_id in self.running_onboardings:
            logger.debug(f"Onboarding {onboarding_id} is already running")
            return

        onboard_thread = threading.Thread(
            target=self._launch_and_run_onboarding,
            args=(onboarding_agent, cleanup_after),
            name=f"Onboard-thread-{onboarding_id}",
        )

        self.running_onboardings[onboarding_id] = RunningOnboarding(
            onboarding_agent=onboarding_agent,
            thread=onboard_thread,
        )

        onboarding_agent.update_status(AgentState.STATUS_ONBOARDING)
        onboard_thread.start()
        return

    def _launch_and_run_onboarding(
        self,
        onboarding_agent: "OnboardingAgent",
        cleanup_after: Callable[[], None],
    ) -> None:
        """Supervise the completion of an onboarding"""
        live_run = onboarding_agent.get_live_run()
        onboarding_id = onboarding_agent.get_agent_id()
        logger.debug(f"Launching onboarding for {onboarding_agent}")
        try:
            self.run_onboarding(onboarding_agent)
            onboarding_agent.mark_done()
        except (
            AgentReturnedError,
            AgentTimeoutError,
            AgentDisconnectedError,
            AgentShutdownError,
        ):
            self.cleanup_onboarding(onboarding_agent)
        except Exception as e:
            logger.exception(
                f"Unhandled exception in onboarding {onboarding_agent}",
                exc_info=True,
            )
            self.cleanup_onboarding(onboarding_agent)
        del self.running_onboardings[onboarding_id]

        # Onboarding now complete
        if onboarding_agent.get_status() == AgentState.STATUS_WAITING:
            # The agent completed the onboarding task
            live_run.loop_wrap.execute_coro(
                live_run.worker_pool.register_agent_from_onboarding(onboarding_agent)
            )
        else:
            logger.info(
                f"Onboarding agent {onboarding_id} disconnected or errored, "
                f"final status {onboarding_agent.get_status()}."
            )
            # TODO is disconnect already being sent?
            # live_run.worker_pool.send_status_update_deprecated(agent_info)

        cleanup_after()

    def execute_unit(
        self,
        unit: "Unit",
        agent: "Agent",
        do_mark_done: Callable[[], None],
    ) -> None:
        """Execute unit in a background thread"""
        if unit.db_id in self.running_units:
            logger.debug(f"{unit} is already running")
            return
        unit_thread = threading.Thread(
            target=self._launch_and_run_unit,
            args=(unit, agent, do_mark_done),
            name=f"Unit-thread-{unit.db_id}",
        )
        self.running_units[unit.db_id] = RunningUnit(
            unit=unit,
            agent=agent,
            thread=unit_thread,
        )
        unit_thread.start()
        return

    def _cleanup_special_units(self, unit: "Unit", agent: "Agent") -> None:
        """
        Checks to see if the specified unit is a quality control unit
        and runs appropriate cleanup if it is
        """
        from mephisto.abstractions.blueprints.mixins.screen_task_required import (
            ScreenTaskRequired,
        )
        from mephisto.operations.task_launcher import (
            SCREENING_UNIT_INDEX,
            GOLD_UNIT_INDEX,
        )

        if unit.unit_index in [SCREENING_UNIT_INDEX, GOLD_UNIT_INDEX]:
            if agent.get_status() != AgentState.STATUS_COMPLETED:
                if unit.unit_index == SCREENING_UNIT_INDEX:
                    blueprint = self.task_run.get_blueprint(args=self.args)
                    assert isinstance(blueprint, ScreenTaskRequired)
                    blueprint.screening_units_launched -= 1
                unit.expire()

    def _launch_and_run_unit(
        self,
        unit: "Unit",
        agent: "Agent",
        do_mark_done: Callable[[], None],
    ) -> None:
        """Supervise the completion of a unit thread"""
        try:
            self.run_unit(unit, agent)
        except (
            AgentReturnedError,
            AgentTimeoutError,
            AgentDisconnectedError,
            AgentShutdownError,
        ) as e:
            # A returned Unit can be worked on again by someone else.
            if unit.get_status() != AssignmentState.EXPIRED:
                unit_agent = unit.get_assigned_agent()
                if unit_agent is not None and unit_agent.db_id == agent.db_id:
                    logger.debug(f"Clearing {agent} from {unit} due to {e}")
                    unit.clear_assigned_agent()
            self.cleanup_unit(unit)
        except Exception as e:
            logger.exception(f"Unhandled exception in unit {unit}", exc_info=True)
            self.cleanup_unit(unit)
        self.shared_state.on_unit_submitted(unit)
        del self.running_units[unit.db_id]

        # Unit run now complete
        if agent.get_status() not in AgentState.complete():
            do_mark_done()
            if not agent.did_submit.is_set():
                # Wait for a submit to occur
                # TODO(#94) make submit timeout configurable
                agent.has_action.wait(timeout=300)
                agent.act()
            agent.mark_done()
        self._cleanup_special_units(unit, agent)
        self.task_run.clear_reservation(unit)

    def execute_assignment(
        self,
        assignment: "Assignment",
        agents: List["Agent"],
        do_mark_done: Callable[[], None],
    ) -> None:
        """Execute assignment in a background thread"""
        if assignment.db_id in self.running_assignments:
            logger.debug(f"Assignment {assignment} is already running")
            return
        assign_thread = threading.Thread(
            target=self._launch_and_run_assignment,
            args=(assignment, agents, do_mark_done),
            name=f"Assignment-thread-{assignment.db_id}",
        )
        for agent in agents:
            agent.update_status(AgentState.STATUS_IN_TASK)

        self.running_assignments[assignment.db_id] = RunningAssignment(
            assignment=assignment,
            agents=agents,
            thread=assign_thread,
        )
        assign_thread.start()
        return

    def _launch_and_run_assignment(
        self,
        assignment: "Assignment",
        agents: List["Agent"],
        do_mark_done: Callable[[], None],
    ) -> None:
        """Supervise the completion of an assignment thread"""
        try:
            self.run_assignment(assignment, agents)
        except (
            AgentReturnedError,
            AgentTimeoutError,
            AgentDisconnectedError,
            AgentShutdownError,
        ) as e:
            # TODO(OWN) implement counting complete tasks, launching a
            # new assignment copied from the parameters of this one
            disconnected_agent_id = e.agent_id
            for agent in agents:
                if agent.db_id != e.agent_id:
                    agent.update_status(AgentState.STATUS_PARTNER_DISCONNECT)
                else:
                    # Must expire the disconnected unit so that
                    # new workers aren't shown it
                    agent.get_unit().expire()
            self.cleanup_assignment(assignment)
        except Exception as e:
            logger.exception(
                f"Unhandled exception in assignment {assignment}",
                exc_info=True,
            )
            self.cleanup_assignment(assignment)
        for unit in assignment.get_units():
            self.shared_state.on_unit_submitted(unit)
        del self.running_assignments[assignment.db_id]

        # Assignment run now complete
        do_mark_done()
        # Wait for agents to be complete
        for agent in agents:
            if agent.get_status() not in AgentState.complete():
                if not agent.did_submit.is_set():
                    # Wait for a submit to occur
                    # TODO(#94) make submit timeout configurable
                    agent.has_action.wait(timeout=300)
                    agent.act()
                agent.mark_done()

        # Clear reservations
        task_run = self.task_run
        for unit in assignment.get_units():
            task_run.clear_reservation(unit)

    @staticmethod
    def get_data_for_assignment(assignment: "Assignment") -> "InitializationData":
        """
        Finds the right data to get for the given assignment.
        """
        return assignment.get_assignment_data()

    @abstractmethod
    def get_init_data_for_agent(self, agent: "Agent"):
        """
        Return the data that an agent will need for their task.
        """
        raise NotImplementedError()

    def filter_units_for_worker(self, units: List["Unit"], worker: "Worker"):
        """
        Returns the list of Units that the given worker is eligible to work on.

        Some tasks may want more direct control of what units a worker is
        allowed to work on, so this method should be overridden by children
        classes.
        """
        return units

    def shutdown(self):
        """
        Updates the status of all agents tracked by this runner to throw a ShutdownException,
        ensuring that all the threads exit correctly and we can cleanup properly.
        """
        # For each type of running task, shut down the agents, then join the threads
        running_units = list(self.running_units.values())
        running_assignments = list(self.running_assignments.values())
        running_onboardings = list(self.running_onboardings.values())

        # Shut down the agents
        for running_unit in running_units:
            running_unit.agent.shutdown()
        for running_assignment in running_assignments:
            for agent in running_assignment.agents:
                agent.shutdown()
        for running_onboarding in running_onboardings:
            running_onboarding.onboarding_agent.shutdown()

        # Join the threads
        for running_unit in running_units:
            running_unit.thread.join()
        for running_assignment in running_assignments:
            running_assignment.thread.join()
        for running_onboarding in running_onboardings:
            running_onboarding.thread.join()

    # TaskRunners must implement either the unit or assignment versions of the
    # run and cleanup functions, depending on if the task is run at the assignment
    # level rather than on the the unit level.

    def run_onboarding(self, agent: "OnboardingAgent"):
        """
        Handle setup for any resources to run an onboarding task. This
        will be run in a background thread, and should be tolerant to being
        interrupted by cleanup_onboarding.

        Only required by tasks that want to implement onboarding
        """
        raise NotImplementedError()

    def cleanup_onboarding(self, agent: "OnboardingAgent"):
        """
        Handle cleaning up the resources that were being used to onboard
        the given agent.
        """
        raise NotImplementedError()

    def run_unit(self, unit: "Unit", agent: "Agent"):
        """
        Handle setup for any resources required to get this unit running.
        This will be run in a background thread, and should be tolerant to
        being interrupted by cleanup_unit.

        Only needs to be implemented by non-concurrent tasks
        """
        raise NotImplementedError()

    def cleanup_unit(self, unit: "Unit"):
        """
        Handle ensuring resources for a given assignment are cleaned up following
        a disconnect or other crash event

        Does not need to be implemented if the run_unit method is
        already error catching and handles its own cleanup
        """
        raise NotImplementedError()

    def run_assignment(self, assignment: "Assignment", agents: List["Agent"]):
        """
        Handle setup for any resources required to get this assignment running.
        This will be run in a background thread, and should be tolerant to
        being interrupted by cleanup_assignment.

        Only needs to be implemented by concurrent tasks
        """
        raise NotImplementedError()

    def cleanup_assignment(self, assignment: "Assignment"):
        """
        Handle ensuring resources for a given assignment are cleaned up following
        a disconnect or other crash event

        Does not need to be implemented if the run_assignment method is
        already error catching and handles its own cleanup
        """
        raise NotImplementedError()
