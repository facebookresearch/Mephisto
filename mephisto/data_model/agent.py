#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import threading
from mephisto.tools.misc import warn_once
from uuid import uuid4

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.worker import Worker
from mephisto.data_model.db_backed_meta import (
    MephistoDBBackedABCMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.data_model.exceptions import (
    AgentReturnedError,
    AgentDisconnectedError,
    AgentTimeoutError,
    AgentShutdownError,
)

from typing import List, Optional, Tuple, Mapping, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.assignment import Assignment
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.task import Task
    from mephisto.data_model.task_run import TaskRun

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


class Agent(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            warn_once(
                "Direct Agent and data model access via ...Agent(db, id) is "
                "now deprecated in favor of calling Agent.get(db, id). "
                "Please update callsites, as we'll remove this compatibility "
                "in the 1.0 release, targetting October 2021",
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_agent(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["agent_id"]
        self.db_status = row["status"]
        self.worker_id = row["worker_id"]
        self.unit_id = row["unit_id"]
        self.task_type = row["task_type"]
        self.provider_type = row["provider_type"]
        self.pending_observations: List["Packet"] = []
        self.pending_actions: List["Packet"] = []
        self.has_action = threading.Event()
        self.has_action.clear()
        self.wants_action = threading.Event()
        self.wants_action.clear()
        self.has_updated_status = threading.Event()
        self.assignment_id = row["assignment_id"]
        self.task_run_id = row["task_run_id"]
        self.task_id = row["task_id"]
        self.did_submit = threading.Event()
        self.is_shutdown = False

        # Deferred loading of related entities
        self._worker: Optional["Worker"] = None
        self._unit: Optional["Unit"] = None
        self._assignment: Optional["Assignment"] = None
        self._task_run: Optional["TaskRun"] = None
        self._task: Optional["Task"] = None

        # Follow-up initialization is deferred
        self._state = None  # type: ignore

    @property
    def state(self) -> "AgentState":
        if self._state is None:
            self._state = AgentState(self)
        return self._state

    def __new__(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ) -> "Agent":
        """
        The new method is overridden to be able to automatically generate
        the expected Agent class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Agent
        as you will instead be returned the correct Agent class according to
        the crowdprovider associated with this Agent.
        """
        from mephisto.operations.registry import get_crowd_provider_from_type

        if cls == Agent:
            # We are trying to construct a Agent, find what type to use and
            # create that instead
            if row is None:
                row = db.get_agent(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).AgentClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def get_agent_id(self) -> str:
        """Return this agent's id"""
        return self.db_id

    def get_worker(self) -> Worker:
        """
        Return the worker that is using this agent for a task
        """
        if self._worker is None:
            self._worker = Worker.get(self.db, self.worker_id)
        return self._worker

    def get_unit(self) -> "Unit":
        """
        Return the Unit that this agent is working on.
        """
        if self._unit is None:
            from mephisto.data_model.unit import Unit

            self._unit = Unit.get(self.db, self.unit_id)
        return self._unit

    def get_assignment(self) -> "Assignment":
        """Return the assignment this agent is working on"""
        if self._assignment is None:
            if self._unit is not None:
                self._assignment = self._unit.get_assignment()
            else:
                from mephisto.data_model.assignment import Assignment

                self._assignment = Assignment.get(self.db, self.assignment_id)
        return self._assignment

    def get_task_run(self) -> "TaskRun":
        """Return the TaskRun this agent is working within"""
        if self._task_run is None:
            if self._unit is not None:
                self._task_run = self._unit.get_task_run()
            elif self._assignment is not None:
                self._task_run = self._assignment.get_task_run()
            else:
                from mephisto.data_model.task_run import TaskRun

                self._task_run = TaskRun.get(self.db, self.task_run_id)
        return self._task_run

    def get_task(self) -> "Task":
        """Return the Task this agent is working within"""
        if self._task is None:
            if self._unit is not None:
                self._task = self._unit.get_task()
            elif self._assignment is not None:
                self._task = self._assignment.get_task()
            elif self._task_run is not None:
                self._task = self._task_run.get_task()
            else:
                from mephisto.data_model.task import Task

                self._task = Task.get(self.db, self.task_id)
        return self._task

    def get_data_dir(self) -> str:
        """
        Return the directory to be storing any agent state for
        this agent into
        """
        assignment_dir = self.get_assignment().get_data_dir()
        return os.path.join(assignment_dir, self.db_id)

    def update_status(self, new_status: str) -> None:
        """Update the database status of this agent, and
        possibly send a message to the frontend agent informing
        them of this update"""
        if self.db_status == new_status:
            return  # Noop, this is already the case
        logger.debug(f"Updating {self} to {new_status}")
        if self.db_status in AgentState.complete():
            logger.info(f"Updating {self} from final status to {new_status}")

        old_status = self.db_status
        self.db.update_agent(self.db_id, status=new_status)
        self.db_status = new_status
        self.has_updated_status.set()
        if new_status in [
            AgentState.STATUS_RETURNED,
            AgentState.STATUS_DISCONNECT,
            AgentState.STATUS_TIMEOUT,
        ]:
            # Disconnect statuses should free any pending acts
            self.has_action.set()
            self.did_submit.set()
            if old_status == AgentState.STATUS_WAITING:
                # Waiting agents' unit can be reassigned, as no work
                # has been done yet.
                unit = self.get_unit()
                logger.debug(f"Clearing {self} from {unit} for update to {new_status}")
                unit.clear_assigned_agent()

    @staticmethod
    def _register_agent(
        db: "MephistoDB", worker: Worker, unit: "Unit", provider_type: str
    ) -> "Agent":
        """
        Create this agent in the mephisto db with the correct setup
        """
        db_id = db.new_agent(
            worker.db_id,
            unit.db_id,
            unit.task_id,
            unit.task_run_id,
            unit.assignment_id,
            unit.task_type,
            provider_type,
        )
        a = Agent.get(db, db_id)
        logger.debug(f"Registered new agent {a} for {unit}.")
        a.update_status(AgentState.STATUS_ACCEPTED)
        return a

    # Specialized child cases may need to implement the following

    @classmethod
    def new_from_provider_data(
        cls,
        db: "MephistoDB",
        worker: Worker,
        unit: "Unit",
        provider_data: Dict[str, Any],
    ) -> "Agent":
        """
        Wrapper around the new method that allows registering additional
        bookkeeping information from a crowd provider for this agent
        """
        agent = cls.new(db, worker, unit)
        unit.worker_id = worker.db_id
        agent._unit = unit
        return agent

    def observe(self, packet: "Packet") -> None:
        """
        Pass the observed information to the AgentState, then
        queue the information to be pushed to the user
        """
        if packet.data.get("message_id") is None:
            packet.data["message_id"] = str(uuid4())
        sending_packet = packet.copy()
        sending_packet.receiver_id = self.db_id
        self.state.update_data(sending_packet)
        self.pending_observations.append(sending_packet)

    def act(self, timeout: Optional[int] = None) -> Optional["Packet"]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        if len(self.pending_actions) == 0:
            self.wants_action.set()
            if timeout is None or timeout == 0:
                return None
            self.has_action.wait(timeout)

        if len(self.pending_actions) == 0:
            if self.is_shutdown:
                raise AgentShutdownError(self.db_id)
            # various disconnect cases
            status = self.get_status()
            if status == AgentState.STATUS_DISCONNECT:
                raise AgentDisconnectedError(self.db_id)
            elif status == AgentState.STATUS_RETURNED:
                raise AgentReturnedError(self.db_id)
            self.update_status(AgentState.STATUS_TIMEOUT)
            raise AgentTimeoutError(timeout, self.db_id)
        assert len(self.pending_actions) > 0, "has_action released without an action!"

        act = self.pending_actions.pop(0)

        if "MEPHISTO_is_submit" in act.data and act.data["MEPHISTO_is_submit"]:
            self.did_submit.set()

        if len(self.pending_actions) == 0:
            self.has_action.clear()
        self.state.update_data(act)
        return act

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
        if self.db_status not in AgentState.complete():
            row = self.db.get_agent(self.db_id)
            if row["status"] != self.db_status:
                if row["status"] in [
                    AgentState.STATUS_RETURNED,
                    AgentState.STATUS_DISCONNECT,
                ]:
                    # Disconnect statuses should free any pending acts
                    self.has_action.set()
                self.has_updated_status.set()
            self.db_status = row["status"]
        return self.db_status

    def shutdown(self) -> None:
        """
        Force the given agent to end any polling threads and throw an AgentShutdownError
        from any acts called on it, ensuring tasks using this agent can be cleaned up.
        """
        logger.debug(f"{self} is shutting down")
        self.has_action.set()
        self.is_shutdown = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id}, {self.db_status})"

    # Children classes should implement the following methods

    def approve_work(self) -> None:
        """Approve the work done on this agent's specific Unit"""
        raise NotImplementedError()

    def soft_reject_work(self) -> None:
        """
        Pay a worker for attempted work, but mark it as below the
        quality bar for this assignment
        """
        # TODO(OWN) extend this method to assign a soft block
        # qualification automatically if a threshold of
        # soft rejects as a proportion of total accepts
        # is exceeded
        self.approve_work()
        self.update_status(AgentState.STATUS_SOFT_REJECTED)

    def reject_work(self, reason) -> None:
        """Reject the work done on this agent's specific Unit"""
        raise NotImplementedError()

    def mark_done(self) -> None:
        """
        Take any required step with the crowd_provider to ensure that
        the worker can submit their work and be marked as complete via
        a call to get_status
        """
        raise NotImplementedError()

    @staticmethod
    def new(db: "MephistoDB", worker: Worker, unit: "Unit") -> "Agent":
        """
        Create an agent for this worker to be used for work on the given Unit.

        Implementation should return the result of _register_agent when sure the agent
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()


class OnboardingAgent(
    MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta
):
    """
    Onboarding agents are a special extension of agents used
    in tasks that have a separate onboarding step. These agents
    are designed to work without being linked to an explicit
    unit, and instead are tied to the task run and task name.


    Blueprints that require OnboardingAgents should implement an
    OnboardingAgentState (to process the special task), and their
    TaskRunners should have a run_onboarding and cleanup_onboarding
    method.
    """

    DISPLAY_PREFIX = "onboarding_"

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            warn_once(
                "Direct OnboardingAgent and data model access via OnboardingAgent(db, id) is "
                "now deprecated in favor of calling OnboardingAgent.get(db, id). "
                "Please update callsites, as we'll remove this compatibility "
                "in the 1.0 release, targetting October 2021",
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_onboarding_agent(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["onboarding_agent_id"]
        self.db_status = row["status"]
        self.worker_id = row["worker_id"]
        self.task_type = row["task_type"]
        self.pending_observations: List["Packet"] = []
        self.pending_actions: List["Packet"] = []
        self.has_action = threading.Event()
        self.has_action.clear()
        self.wants_action = threading.Event()
        self.wants_action.clear()
        self.has_updated_status = threading.Event()
        self.task_run_id = row["task_run_id"]
        self.task_id = row["task_id"]
        self.did_submit = threading.Event()
        self.is_shutdown = False

        # Deferred loading of related entities
        self._worker: Optional["Worker"] = None
        self._task_run: Optional["TaskRun"] = None
        self._task: Optional["Task"] = None

        # Follow-up initialization
        self.state = AgentState(self)  # type: ignore

    def get_agent_id(self) -> str:
        """Return an id to use for onboarding agent requests"""
        return f"{self.DISPLAY_PREFIX}{self.db_id}"

    @classmethod
    def is_onboarding_id(cls, agent_id: str) -> bool:
        """return if the given id is for an onboarding agent"""
        return agent_id.startswith(cls.DISPLAY_PREFIX)

    @classmethod
    def get_db_id_from_agent_id(cls, agent_id: str) -> str:
        """Extract the db_id for an onboarding_agent"""
        assert agent_id.startswith(
            cls.DISPLAY_PREFIX
        ), f"Provided id {agent_id} is not an onboarding_id"
        return agent_id[len(cls.DISPLAY_PREFIX) :]

    def get_worker(self) -> Worker:
        """
        Return the worker that is using this agent for a task
        """
        if self._worker is None:
            self._worker = Worker.get(self.db, self.worker_id)
        return self._worker

    def get_task_run(self) -> "TaskRun":
        """Return the TaskRun this agent is working within"""
        if self._task_run is None:
            from mephisto.data_model.task_run import TaskRun

            self._task_run = TaskRun.get(self.db, self.task_run_id)
        return self._task_run

    def get_task(self) -> "Task":
        """Return the Task this agent is working within"""
        if self._task is None:
            if self._task_run is not None:
                self._task = self._task_run.get_task()
            else:
                from mephisto.data_model.task import Task

                self._task = Task.get(self.db, self.task_id)
        return self._task

    def get_data_dir(self) -> str:
        """
        Return the directory to be storing any agent state for
        this agent into
        """
        task_run_dir = self.get_task_run().get_run_dir()
        return os.path.join(task_run_dir, "onboarding", self.get_agent_id())

    def update_status(self, new_status: str) -> None:
        """Update the database status of this agent, and
        possibly send a message to the frontend agent informing
        them of this update"""
        if self.db_status == new_status:
            return  # Noop, this is already the case

        logger.debug(f"Updating {self} to {new_status}")
        if self.db_status in AgentState.complete():
            logger.info(f"Updating {self} from final status to {new_status}")

        self.db.update_onboarding_agent(self.db_id, status=new_status)
        self.db_status = new_status
        self.has_updated_status.set()
        if new_status in [AgentState.STATUS_RETURNED, AgentState.STATUS_DISCONNECT]:
            # Disconnect statuses should free any pending acts
            self.has_action.set()
            self.did_submit.set()

    def observe(self, packet: "Packet") -> None:
        """
        Pass the observed information to the AgentState, then
        queue the information to be pushed to the user
        """
        sending_packet = packet.copy()
        sending_packet.receiver_id = self.get_agent_id()
        self.state.update_data(sending_packet)
        self.pending_observations.append(sending_packet)

    def act(self, timeout: Optional[int] = None) -> Optional["Packet"]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        if len(self.pending_actions) == 0:
            self.wants_action.set()
            if timeout is None or timeout == 0:
                return None
            self.has_action.wait(timeout)

        if len(self.pending_actions) == 0:
            # various disconnect cases
            if self.is_shutdown:
                raise AgentShutdownError(self.db_id)
            status = self.get_status()
            if status == AgentState.STATUS_DISCONNECT:
                raise AgentDisconnectedError(self.db_id)
            elif status == AgentState.STATUS_RETURNED:
                raise AgentReturnedError(self.db_id)
            self.update_status(AgentState.STATUS_TIMEOUT)
            raise AgentTimeoutError(timeout, self.db_id)
        assert len(self.pending_actions) > 0, "has_action released without an action!"

        act = self.pending_actions.pop(0)

        if "MEPHISTO_is_submit" in act.data and act.data["MEPHISTO_is_submit"]:
            self.did_submit.set()

        if len(self.pending_actions) == 0:
            self.has_action.clear()
        self.state.update_data(act)
        return act

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
        if self.db_status not in AgentState.complete():
            row = self.db.get_onboarding_agent(self.db_id)
            if row["status"] != self.db_status:
                if row["status"] in [
                    AgentState.STATUS_RETURNED,
                    AgentState.STATUS_DISCONNECT,
                ]:
                    # Disconnect statuses should free any pending acts
                    self.has_action.set()
                self.has_updated_status.set()
            self.db_status = row["status"]
        return self.db_status

    def mark_done(self) -> None:
        """Mark this agent as done by setting the status to a terminal onboarding state"""
        # TODO the logic for when onboarding gets marked as waiting or approved/rejected
        # should likely be cleaned up to remove these conditionals.
        if self.get_status not in [
            AgentState.STATUS_APPROVED,
            AgentState.STATUS_REJECTED,
        ]:
            self.update_status(AgentState.STATUS_WAITING)

    def shutdown(self) -> None:
        """
        Force the given agent to end any polling threads and throw an AgentShutdownError
        from any acts called on it, ensuring tasks using this agent can be cleaned up.
        """
        logger.debug(f"{self} is shutting down")
        self.has_action.set()
        self.is_shutdown = True

    @staticmethod
    def new(db: "MephistoDB", worker: Worker, task_run: "TaskRun") -> "OnboardingAgent":
        """
        Create an OnboardingAgent for a worker to use as part of a task run
        """
        db_id = db.new_onboarding_agent(
            worker.db_id, task_run.task_id, task_run.db_id, task_run.task_type
        )
        a = OnboardingAgent.get(db, db_id)
        logger.debug(f"Registered new {a} for worker {worker}.")
        return a

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id})"
