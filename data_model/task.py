#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.assignment import Assignment, ASSIGNMENT_STATUSES
from mephisto.core.utils import (
    get_tasks_dir,
    get_dir_for_task,
    ensure_user_confirm,
    get_dir_for_run,
)
from typing import List, Optional, Tuple, Dict, cast
import os
from shutil import copytree


VALID_TASK_TYPES = ["legacy_parlai", "generic"]


def assert_task_is_valid(dir_name, task_type) -> None:
    """
    Go through the given task directory and ensure it is valid under the
    given task type
    """
    # TODO actually check to ensure all the expected files are there
    pass


# TODO find a way to repair the database if a user moves folders and files around
# in an unexpected way, primarily resulting in tasks no longer being executable
# and becoming just storage for other information.


class TaskParams:
    """
    This class operates in a way to collect all task-related parameters. Specific tasks
    should extend the TaskParam class and add additional fields to the argparser.
    """

    def __init__(self, task_dir, arg_string: Optional[str] = None):
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

    def parse(self, parse_args=None):
        pass

    def get_param_string(self):
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
        task_row = db.get_task(db_id)
        self.task_name: str = task_row["task_name"]
        self.task_type: str = task_row["task_type"]
        self.project_id: Optional[str] = task_row["project_id"]
        self.parent_task_type: Optional[str] = task_row["parent_task_id"]

    def get_project(self) -> Optional[Project]:
        """
        Get the project for this task, if it exists
        """
        if self.project_id is not None:
            return Project(self.db, self.project_id)
        else:
            return None

    def set_project(self, project: Project):
        if self.project_id != project.db_id:
            # TODO this constitutes an update, must go back to the db
            raise NotImplementedError()

    def get_runs(self) -> List[TaskRun]:
        """
        Return all of the runs of this task that have been launched
        """
        return self.db.find_task_runs(task_id=self.db_id)

    def get_assignments(self) -> List[Assignment]:
        """
        Return all of the assignments for all runs of this task
        """
        assigns = []
        for task_run in self.get_runs():
            assigns += task_run.get_assignments()
        return assigns

    def get_task_params(self) -> TaskParams:
        """
        Return the task parameters associated with this task
        """
        task_dir = self.get_task_source()
        # TODO load the TaskParams module for the given task
        raise NotImplementedError()

    def get_task_source(self) -> str:
        """
        Return the path to the task content, such that the server architect
        can deploy the relevant frontend
        """
        # FIXME will this ever be invalid? Must have tests
        return get_dir_for_task(self.task_name)

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent for this task.
        """
        total_spend = 0
        for task_run in self.get_runs():
            total_spend += task_run.get_total_spend()
        return total_spend

    @staticmethod
    def new(
        task_name: str,
        db: MephistoDB,
        task_type: str,
        project: Optional[Project] = None,
        parent_task: Optional[Task] = None,
        skip_inputs: bool = False,
    ) -> Task:
        """
        Create a new task by the given name, ensure that the folder for this task
        exists and has the expected directories and files. If a project is
        specified, register the task underneath it
        """
        assert (
            task_type in VALID_TASK_TYPES
        ), f"Given task type {task_type} is not recognized in {VALID_TASK_TYPES}"
        assert (
            len(db.find_tasks(task_name=task_name)) == 0
        ), f"A task named {task_name} already exists!"

        new_task_dir = get_dir_for_task(task_name, not_exists_ok=True)
        if parent_task is None:
            # Assume we already have an existing task dir for the given task,
            # complain if it doesn't exist or isn't configured properly
            assert os.path.exists(
                new_task_dir
            ), f"No such task path {new_task_dir} exists yet, and as such the task cannot be officially created without using a parent task."
            assert_task_is_valid(new_task_dir, task_type)
        else:
            # The user intends to create a task by copying something from
            # the gallery or local task directory and then modifying it.
            # Ensure the parent task exists before starting
            parent_task_dir = parent_task.get_task_source()
            assert (
                parent_task_dir is not None
            ), f"No such task {parent_task} exists in your local task directory or the gallery, but was specified as a parent task. Perhaps this directory was deleted?"

            # If the new directory already exists, complain, as we are going to delete it.
            if os.path.exists(new_task_dir):
                ensure_user_confirm(
                    f"The task directory {new_task_dir} already exists, and the contents "
                    f"within will be deleted and replaced with the starter code for {parent_task}.",
                    skip_inputs=skip_inputs,
                )
                os.rmdir(new_task_dir)
            os.mkdir(new_task_dir)
            copytree(parent_task_dir, new_task_dir)

        db_id = db.new_task(task_name, task_type, project.db_id, parent_task.db_id)
        return Task(db, db_id)

        def __repr__(self):
            return f"Task-{self.task_name} [{self.task_type}]"


class TaskRun:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of assignments within
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        row = db.get_task_run(db_id)
        self.task_id = row["task_id"]
        self.requester_id = row["requester_id"]
        task = Task(db, self.task_id)
        self.task_params = task.get_task_params()
        self.param_string = row["init_params"]

    def get_used_params(self) -> TaskParams:
        """Return the parameters used to launch this task"""
        # TODO investigae this once TaskParams is implemented
        # > self.task_params.parse(self.param_string)?
        raise NotImplementedError()

    def get_requester(self) -> Requester:
        """
        Return the requester that started this task.
        """
        return Requester(self.db, self.db_id)

    def get_assignments(self, status: Optional[str] = None) -> List[Assignments]:
        """
        Get assignments for this run, optionally filtering by their
        current status
        """
        assert (
            status is None or status in ASSIGNMENT_STATUSES
        ), "Invalid assignment status"
        assignments = self.db.find_assignments(task_run_id=self.db_id)
        if status is not None:
            assignments = [a for a in assignments if a.get_status() == status]
        return assignments

    def get_assignment_statuses(self) -> Dict[str, int]:
        """
        Get the statistics for all of the assignments for this run.
        """
        assigns = self.get_assignments()
        return {
            status: len([x for x in assigns if x.get_status() == status])
            for status in ASSIGNMENT_STATUSES
        }

    def get_run_dir(self) -> str:
        """
        Return the directory where the data from this run is stored
        """
        # TODO this step should go into the TaskLauncher
        # run_dir = self.get_run_dir()
        # os.makedirs(run_dir, exist_ok=True)
        task = Task(self.task_id)
        return get_dir_for_run(self.db_id, task.get_project())

    @staticmethod
    def new(
        db: MephistoDB, task: Task, requester: Requester, params: TaskParams
    ) -> TaskRun:
        """
        Create a new run for the given task with the given params
        """
        db_id = db.new_task_run(task.db_id, requester.db_id, params.get_param_string())
        return TaskRun(db, db_id)
