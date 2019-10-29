#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.agent_state import AgentState
from mephisto.data_model.worker import Worker
from mephisto.core.utils import get_crowd_provider_from_type, get_task_runner_from_type

from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.database import MephistoDB


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
        self.task_type = row["task_type"]
        self.provider_type = row["provider_type"]
        self.state = AgentState(self)

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

    @staticmethod
    def _register_agent(db: "MephistoDB", worker: Worker, unit: "Unit") -> "Agent":
        """
        Create this agent in the mephisto db with the correct setup
        """
        task = unit.get_assignment().get_task_run().get_task()
        db_id = db.new_agent(
            worker.db_id, unit.db_id, task.task_type, worker.provider_type
        )
        return Agent(db, db_id)

    # Children classes should implement the following methods

    def observe(self, action: Dict[str, Any]) -> None:
        """
        Pass the observed information to the AgentState, then
        push that information to the user
        """
        # TODO maybe formalize the contents of what an Action are?
        raise NotImplementedError()

    def act(self, blocking=False) -> Optional[Dict[str, Any]]:
        """
        Request information from the Agent's frontend. If non-blocking,
        should return None if no actions are ready to be returned.
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
