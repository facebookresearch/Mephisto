#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.task import Task, TaskRun
from mephisto.data_model.worker import Worker, Agent
from mephisto.core.utils import get_dir_for_run
from typing import List, Optional, Tuple, Dict
import os

ASSIGNMENT_STATUSES = [
    # TODO put all the valid assignment statuses here
]

ASSIGNMENT_DATA_FILE = 'assign_data.json'


class Assignment:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of assignments within via abstracted database helpers
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database

    def get_assignment_data(self) -> Optional[str]:
        """Return the specific assignment data for this assignment"""
        # TODO pull from the assignment directory if it exists
        raise NotImplementedError()

    def get_status(self) -> str:
        """
        Get the status of this assignment, as determined by the status of
        the sub-assignments
        """
        subassignments = self.get_subassignments()
        # TODO parse subassignments and return a computed status
        raise NotImplementedError()

    def get_subassignments(self, status: Optional[str]):
        """
        Get subassignments for this assignment, optionally
        constrained by the specific status.
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
    def new(db: MephistoDB, task_run: TaskRun, assignment_json: Optional[str]) -> Assignment:
        """
        Create an assignment for the given task. Initialize the folders for storing
        the results for this assignment.
        """
        db_id = db.new_assignment(task_run.db_id)
        run_dir = task_run.get_run_dir()
        assign_dir = os.path.join(run_dir, db_id)
        os.makedirs(assign_dir)
        if assignment_json is not None:
            with open(os.path.join(assign_dir, ASSIGNMENT_DATA_FILE)):
                # TODO write this assignment data to a file
                pass
        # TODO make the database entry, then return the new Assignment
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
