#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.assignment import SubAssignment
from typing import List, Optional, Tuple, Dict

AGENT_STATUSES = [
    # TODO pull from MTurk Assign State
]


class Worker:
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database

    # TODO make getters for helpful worker statistics

    # TODO make helpers for bonusing? and blocking

    def get_agents(self, status: Optional[str] = None) -> List[Agent]:
        """
        Get the list of agents that this worker was responsible for, by the given status
        if needed
        """
        assert status is None or status in AGENT_STATUSES, "Invalid agent status"
        # TODO query for agents associated with this worker by the provided status
        pass

    @staticmethod
    def new(worker_id: str, crowd_provider: str) -> Worker:
        """
        Create a new worker attached to the given identifier, assuming it doesn't already
        exist in the data Takes in a crowd_provider
        """
        # TODO Create a worker and initialize any expected stats for them
        #
        # TODO make crowd_provider be the class that provided this worker
        pass


class Agent:
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database

    # TODO pull content from MTurk AssignState and MTurkAgent

    @staticmethod
    def new(worker: Worker) -> Agent:
        """
        Create an agent for this worker to be used in a task.
        """
        # TODO Create the agent
        pass
