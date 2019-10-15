#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.project import Project
from mephisto.data_model.assignment import Assignment, ASSIGNMENT_STATUSES
from typing import List, Optional, Tuple, Dict


class TaskParams:
    """
    This class operates in a way to collect all task-related parameters. Specific tasks
    should extend the TaskParam class and add additional fields to the argparser.
    """

    def __init__(self, arg_string: Optional[str] = None):
        """
        Load up a new set of task parameters from either command line arguments
        or from the provided arguments
        """
        # TODO figure out what command line arguments are available by default
        # and make it possible to extend with additional arguments.
        #
        # Ideally the command line arguments should be displayable to the
        # frontend in some kind of managable way
        #
        # THis class is likely to leverage argparse in a significant way
        pass

    # TODO write functions for retrieving arguments


class Task:
    """
    This class contains all of the required tidbits for launching a set of
    assignments, including the place to find the frontend files (based on the
    task name), task parameters. It also takes the project name if this
    task is to be associated with a specific project.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database,
        # then check the task directory to be sure that
        # it is well-formed and nothing is missing.
        self.project_name: str = None

    def get_runs(self) -> List["TaskRun"]:
        """
        Return all of the runs of this task that have been launched
        """
        # TODO query the database for runs of this specific task_id
        pass

    def get_assignments(self) -> List[Assignment]:
        """
        Return all of the assignments for all runs of this task
        """
        # TODO return the union of all of the assignments for all of the TaskRuns
        pass

    def get_task_params(self) -> TaskParams:
        """
        Return the task parameters associated with this task
        """
        # TODO search into the directory to find the correct TaskParams, return those
        pass

    def get_task_source(self) -> str:
        """
        Return the path to the task content, such that the server architect
        can deploy the relevant frontend
        """
        # TODO this is going to be in a standard folder of one of a few types
        pass

    @staticmethod
    def new(
        task_name: str,
        db: MephistoDB,
        task_type: str,
        project: Optional[Project] = None,
    ) -> Task:
        """
        Create a new task by the given name, ensure that the folder for this task
        exists and has the expected directories and files. If a project is
        specified, register the task underneath it
        """
        # TODO parse for the task directory by the given name, if
        # the folder doesn't exist, make a new folder entirely and populate
        # with some skeleton code?
        #
        # then make a new entry in the database for this task
        pass


class TaskRun:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of assignments within
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database
        self.project_name: str = None

    def get_used_params(self) -> TaskParams:
        """Return the parameters used to launch this task"""
        # TODO get the correct params, and initialize them using the
        # saved startup string
        pass

    def get_assignments(self, status: Optional[str] = None) -> List[Assignments]:
        """
        Get assignments for this run, optionally filtering by their
        current status
        """
        assert (
            status is None or status in ASSIGNMENT_STATUSES
        ), "Invalid assignment status"
        # TODO query the database for all assignments of the given status if supplied
        pass

    def get_assignment_statuses(self) -> Dict[str, int]:
        """
        Get the statistics for all of the assignments for this run.
        """
        # TODO query all the assignments, then bundle them by status
        pass

    @staticmethod
    def new(task: Task, params: TaskParams) -> TaskRun:
        """
        Create a new run for the given task with the given params
        """
        # TODO create the task and hook the specific params into it.
        pass
