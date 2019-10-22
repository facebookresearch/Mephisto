#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.assignment import Unit
from mephisto.data_model.database import MephistoDB
from mephisto.data_model.worker import Worker
from mephisto.core.utils import get_crowd_provider_from_type, get_task_runner_from_type
from typing import List, Optional, Tuple, Dict, Any


# TODO what is the best method for creating new ones of these for different task types
# in ways that are supported by different backends? Perhaps abstract additional
# methods into the required db interface? Move any file manipulations into a
# extra_data_handler subcomponent of the MephistoDB class?
# Can handle doing this split after getting the first round of tests done because
# otherwise it's a lot of written but untestable code.
class AgentState(ABC):
    """
    Class for holding state information about work by an Agent on a Unit, currently
    stored as current task work into a json file.

    Specific state implementations will need to be created for different Task Types,
    as different tasks store and load differing data.
    """

    # Possible Agent Status Values
    STATUS_NONE = "none"
    STATUS_ACCEPTED = "accepted"
    STATUS_ONBOARDING = "onboarding"
    STATUS_WAITING = "waiting"
    STATUS_IN_TASK = "in task"
    STATUS_COMPLETED = "completed"
    STATUS_DISCONNECT = "disconnect"
    STATUS_PARTNER_DISCONNECT = "partner disconnect"
    STATUS_EXPIRED = "expired"
    STATUS_RETURNED = "returned"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    @abstractmethod
    def __init__(self, agent: Agent):
        """
        Create an AgentState to track the state of an agent's work on a Unit

        Implementations should initialize any required files for saving and
        loading state data somewhere.

        If said file already exists based on the given agent, load that data
        instead.
        """
        raise NotImplementedError()

    def __new__(cls, agent: Agent) -> AgentState:
        """
        The new method is overridden to be able to automatically generate
        the expected Requester class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Requester
        as you will instead be returned the correct Requester class according to
        the crowdprovider associated with this Requester.
        """
        if cls == AgentState:
            # We are trying to construct an AgentState, find what type to use and
            # create that instead
            correct_class = get_task_runner_from_type(agent.task_type).AgentStateClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    @abstractmethod
    def load_data(self) -> None:
        """
        Load stored data from a file to this object
        """
        raise NotImplementedError()

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Return the currently stored data for this task in the dict format
        expected by any frontend displays
        """
        raise NotImplementedError()

    @abstractmethod
    def save_data(self) -> None:
        """
        Save the relevant data from this Unit to a file in the expected location
        """
        raise NotImplementedError()

    @abstractmethod
    def update_data(self, *args) -> None:
        """
        Put new current Unit data into this AgentState
        """
        # TODO maybe refine the signature for this function once use cases
        # are fully scoped

        # Some use cases might just be appending new data, some
        # might instead prefer to maintain a final state.

        # Maybe the correct storage is of a series of actions taken
        # on this Unit? Static tasks only have 2 turns max, dynamic
        # ones may have multiple turns or steps.
        raise NotImplementedError()

    @staticmethod
    def valid() -> List[str]:
        """Return all valid Agent statuses"""
        # TODO write a test that ensures all AgentState statuses are here
        return [
            AgentState.STATUS_NONE,
            AgentState.STATUS_ONBOARDING,
            AgentState.STATUS_WAITING,
            AgentState.STATUS_IN_TASK,
            AgentState.STATUS_DONE,
            AgentState.STATUS_DISCONNECT,
            AgentState.STATUS_PARTNER_DISCONNECT,
            AgentState.STATUS_EXPIRED,
            AgentState.STATUS_RETURNED,
        ]


class Agent(ABC):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        row = db.get_agent(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_status = row["status"]
        self.worker_id = row["worker_id"]
        self.task_type = row["task_type"]
        self.provider_type = row["provider_type"]
        self.state = AgentState(self)

    def __new__(cls, db: MephistoDB, db_id: str) -> Unit:
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

    def get_worker(self) -> Worker:
        """
        Return the worker that is using this agent for a task
        """
        return Worker(self.db, self.worker_id)

    @staticmethod
    def _register_agent(db: MephistoDB, worker: Worker, unit: Unit) -> Agent:
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
    def new(db: MephistoDB, worker: Worker, unit: Unit) -> Agent:
        """
        Create an agent for this worker to be used for work on the given Unit.

        Implementation should return the result of _register_agent when sure the agent
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()
