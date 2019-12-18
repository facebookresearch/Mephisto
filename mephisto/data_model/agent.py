#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import threading

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.blueprint import AgentState
from mephisto.data_model.worker import Worker
from mephisto.core.utils import get_crowd_provider_from_type

from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.packet import Packet


# types of exceptions thrown when an agent exits the chat. These are thrown
# on a failed act call call. If one of these is thrown and not handled,
# the world should die and enter cleanup.
class AbsentAgentError(Exception):
    """Exceptions for when an agent leaves a task"""

    def __init__(self, message, worker_id, assignment_id):
        self.message = message
        self.worker_id = worker_id
        self.assignment_id = assignment_id


class AgentDisconnectedError(AbsentAgentError):
    """Exception for a real disconnect event (no signal)"""

    def __init__(self, worker_id, assignment_id):
        super().__init__(f"Agent disconnected", worker_id, assignment_id)


class AgentTimeoutError(AbsentAgentError):
    """Exception for when a worker doesn't respond in time"""

    def __init__(self, timeout, worker_id, assignment_id):
        super().__init__(f"Agent exceeded {timeout}", worker_id, assignment_id)


class AgentReturnedError(AbsentAgentError):
    """Exception for an explicit return event (worker returns task)"""

    def __init__(self, worker_id, assignment_id):
        super().__init__(f"Agent returned HIT", worker_id, assignment_id)


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
        self.state = AgentState(self)
        self.pending_observations: List["Packet"] = []
        self.pending_actions: List["Packet"] = []
        self.has_action = threading.Event()
        self.has_action.clear()

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
        return Worker(self.db, self.worker_id)

    def get_unit(self) -> "Unit":
        """
        Return the Unit that this agent is working on.
        """
        from mephisto.data_model.assignment import Unit

        return Unit(self.db, self.unit_id)

    def get_data_dir(self) -> str:
        """
        Return the directory to be storing any agent state for
        this agent into
        """
        assignment_dir = self.get_unit().get_assignment().get_data_dir()
        return os.path.join(assignment_dir, self.db_id)

    @staticmethod
    def _register_agent(
        db: "MephistoDB", worker: Worker, unit: "Unit", provider_type: str
    ) -> "Agent":
        """
        Create this agent in the mephisto db with the correct setup
        """
        task = unit.get_assignment().get_task_run().get_task()
        db_id = db.new_agent(worker.db_id, unit.db_id, task.task_type, provider_type)
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
        assert (
            packet.receiver_id == self.db_id
        ), f"Unintended packet receiving: {self.db_id} {packet}"
        self.state.update_data(packet)
        self.pending_observations.append(packet)

    def act(self, timeout: Optional[int] = None) -> Optional["Packet"]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        if len(self.pending_actions) == 0:
            if timeout is None:
                return None
            self.has_action.wait(timeout)
        assert len(self.pending_actions) > 0, "has_action released without an action!"

        act = self.pending_actions.pop(0)

        # TODO check to see if the act is one of the acts to ERROR on

        if len(self.pending_actions) == 0:
            self.has_action.clear()
        self.state.update_data(act)
        return act

    # Children classes should implement the following methods

    def approve_work(self) -> None:
        """Approve the work done on this agent's specific Unit"""
        raise NotImplementedError()

    def reject_work(self, reason) -> None:
        """Reject the work done on this agent's specific Unit"""
        raise NotImplementedError()

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
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
