#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.task import Task, TaskRun
from mephisto.data_model.worker import Worker, Agent
from typing import List, Optional, Tuple, Dict


ASSIGNMENT_STATUSES = [
    # TODO put all the valid assignment statuses here
]


class Assignment:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of assignments within
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database

    def get_assignment_data(self) -> Optional[str]:
        """Return the specific assignment data for this assignment"""
        pass

    def get_status(self) -> str:
        """
        Get the status of this assignment, as determined by the status of
        the sub-assignments
        """
        assert (
            status is None or status in ASSIGNMENT_STATUSES
        ), "Invalid assignment status"
        # TODO query the database for all assignments of the given status if supplied
        pass

    def get_workers(self) -> List[Worker]:
        """
        Get the list of workers that have worked on this specific assignment
        """
        # TODO query the agents from the subassignments, then get their workers
        # if set. This can be used to ensure no worker gets paired with an assignment more than once
        pass

    @staticmethod
    def new(task_run: TaskRun, assignment_data: Optional[str] = None) -> Assignment:
        """
        Create an assignment for the given task. Can take optional assignment_data
        that specifies what the content of this specific task is supposed to be
        """
        # TODO Create an individual assignment, and the related subassignment
        # for the given task run
        pass


class SubAssignment:
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database

    def get_assignment_data(self) -> Optional[str]:
        """Return the specific assignment data for this assignment"""
        pass

    def get_status(self) -> str:
        """
        Get the status of this subassignment, as determined by whether there's
        a worker working on it at the moment.
        """
        # TODO get the current status of this sub-assignment
        pass

    def get_assigned_agent(self, agent: Agent) -> Optional[Agent]:
        """
        Get the agent assigned to this SubAssignment if there is one, else return None
        """
        pass

    def assign_agent(self, agent: Agent) -> None:
        """
        Assign this subassignment to the given agent.
        """
        # TODO actually come up with the proper pairing logic
        pass

    @staticmethod
    def new(assignment: Assignment) -> SubAssignment:
        """
        Create a subassignment for the given assignment.
        """
        # TODO Create the subassignment
        pass
