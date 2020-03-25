#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import threading

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.blueprint import AgentState
from mephisto.data_model.worker import Worker
from mephisto.data_model.exceptions import (
    AgentReturnedError,
    AgentDisconnectedError,
    AgentTimeoutError,
)
from mephisto.core.utils import get_crowd_provider_from_type

from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Unit, Assignment
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.task import Task, TaskRun


class Agent(ABC):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        self.db_id: str = db_id
        self.db: "MephistoDB" = db
        row = db.get_agent(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
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

        # Deferred loading of related entities
        self._worker: Optional["Worker"] = None
        self._unit: Optional["Unit"] = None
        self._assignment: Optional["Assignment"] = None
        self._task_run: Optional["TaskRun"] = None
        self._task: Optional["Task"] = None

        # Follow-up initialization
        self.state = AgentState(self)  # type: ignore

    def __new__(cls, db: "MephistoDB", db_id: str) -> "Agent":
        """
        The new method is overridden to be able to automatically generate
        the expected Agent class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Agent
        as you will instead be returned the correct Agent class according to
        the crowdprovider associated with this Agent.
        """
        if cls == Agent:
            # We are trying to construct a Agent, find what type to use and
            # create that instead
            row = db.get_agent(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).AgentClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    # TODO do we want to store task working time or completion time here?

    def get_worker(self) -> Worker:
        """
        Return the worker that is using this agent for a task
        """
        if self._worker is None:
            self._worker = Worker(self.db, self.worker_id)
        return self._worker

    def get_unit(self) -> "Unit":
        """
        Return the Unit that this agent is working on.
        """
        if self._unit is None:
            from mephisto.data_model.assignment import Unit

            self._unit = Unit(self.db, self.unit_id)
        return self._unit

    def get_assignment(self) -> "Assignment":
        """Return the assignment this agent is working on"""
        if self._assignment is None:
            if self._unit is not None:
                self._assignment = self._unit.get_assignment()
            else:
                from mephisto.data_model.assignment import Assignment

                self._assignment = Assignment(self.db, self.assignment_id)
        return self._assignment

    def get_task_run(self) -> "TaskRun":
        """Return the TaskRun this agent is working within"""
        if self._task_run is None:
            if self._unit is not None:
                self._task_run = self._unit.get_task_run()
            elif self._assignment is not None:
                self._task_run = self._assignment.get_task_run()
            else:
                from mephisto.data_model.task import TaskRun

                self._task_run = TaskRun(self.db, self.task_run_id)
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

                self._task = Task(self.db, self.task_id)
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
        assert (
            self.db_status not in AgentState.complete()
        ), f"Cannot update a final status, was {self.db_status} and want to set to {new_status}"
        self.db.update_agent(self.db_id, status=new_status)
        self.db_status = new_status
        self.has_updated_status.set()
        if new_status in [AgentState.STATUS_RETURNED, AgentState.STATUS_DISCONNECT]:
            # Disconnect statuses should free any pending acts
            self.has_action.set()
            self.did_submit.set()

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
        return Agent(db, db_id)

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
        return cls.new(db, worker, unit)

    def observe(self, packet: "Packet") -> None:
        """
        Pass the observed information to the AgentState, then
        queue the information to be pushed to the user
        """
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
            # various disconnect cases
            status = self.get_status()
            if status == AgentState.STATUS_DISCONNECT:
                raise AgentDisconnectedError(self.db_id)
            elif status == AgentState.STATUS_RETURNED:
                raise AgentReturnedError(self.db_id)
            self.update_status(AgentState.STATUS_TIMEOUT)
            raise AgentTimeoutError(timeout, self.db_id)
        # TODO the below needs to be considered an agent timeout
        assert len(self.pending_actions) > 0, "has_action released without an action!"

        act = self.pending_actions.pop(0)

        if "MEPHISTO_is_submit" in act.data and act.data["MEPHISTO_is_submit"]:
            self.did_submit.set()

        # TODO check to see if the act is one of the acts to ERROR on

        if len(self.pending_actions) == 0:
            self.has_action.clear()
        self.state.update_data(act)
        return act

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
        if self.db_status not in AgentState.complete():
            row = self.db.get_agent(self.db_id)
            if row["status"] != self.db_status:
                if row["status"] in [AgentState.STATUS_RETURNED, AgentState.STATUS_DISCONNECT]:
                    # Disconnect statuses should free any pending acts
                    self.has_action.set()
                self.has_updated_status.set()
            self.db_status = row["status"]
        return self.db_status

    # Children classes should implement the following methods

    def approve_work(self) -> None:
        """Approve the work done on this agent's specific Unit"""
        raise NotImplementedError()

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
