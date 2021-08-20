#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from mephisto.tools.misc import warn_once
from shutil import copytree

from mephisto.data_model.project import Project
from mephisto.data_model.db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.operations.utils import (
    get_dir_for_task,
    ensure_user_confirm,
)

from functools import reduce

from typing import List, Optional, Mapping, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.crowd_provider import CrowdProvider


# TODO(#98) pull from utils, these are blueprints
VALID_TASK_TYPES = ["legacy_parlai", "generic", "mock"]


def assert_task_is_valid(dir_name, task_type) -> None:
    """
    Go through the given task directory and ensure it is valid under the
    given task type
    """
    # TODO(#97) actually check to ensure all the expected files are there
    pass


# TODO(#102) find a way to repair the database if a user moves folders and files
# around in an unexpected way, primarily resulting in tasks no longer being
# executable and becoming just storage for other information.


class Task(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    """
    This class contains all of the required tidbits for launching a set of
    assignments, primarily by leveraging a blueprint. It also takes the
    project name if this task is to be associated with a specific project.
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
                "Direct Task and data model access via Task(db, id) is "
                "now deprecated in favor of calling Task.get(db, id). "
                "Please update callsites, as we'll remove this compatibility "
                "in the 1.0 release, targetting October 2021",
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_task(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["task_id"]
        self.task_name: str = row["task_name"]
        self.task_type: str = row["task_type"]
        self.project_id: Optional[str] = row["project_id"]
        self.parent_task_id: Optional[str] = row["parent_task_id"]

    def get_project(self) -> Optional[Project]:
        """
        Get the project for this task, if it exists
        """
        if self.project_id is not None:
            return Project.get(self.db, self.project_id)
        else:
            return None

    def set_project(self, project: Project) -> None:
        if self.project_id != project.db_id:
            # TODO(#101) this constitutes an update, must go back to the db
            raise NotImplementedError()

    def get_runs(self) -> List["TaskRun"]:
        """
        Return all of the runs of this task that have been launched
        """
        return self.db.find_task_runs(task_id=self.db_id)

    def get_assignments(self) -> List["Assignment"]:
        """
        Return all of the assignments for all runs of this task
        """
        return self.db.find_assignments(task_id=self.db_id)

    def get_task_source(self) -> str:
        """
        Return the path to the task content, such that the server architect
        can deploy the relevant frontend
        """
        # TODO(#101) do we need a task source anymore?
        task_dir = get_dir_for_task(self.task_name)
        assert task_dir is not None, f"Task dir for {self} no longer exists!"
        return task_dir

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent for this task.
        """
        total_spend = 0.0
        for task_run in self.get_runs():
            total_spend += task_run.get_total_spend()
        return total_spend

    @staticmethod
    def new(
        db: "MephistoDB",
        task_name: str,
        task_type: str,
        project: Optional[Project] = None,
        parent_task: Optional["Task"] = None,
        skip_input: bool = False,
    ) -> "Task":
        """
        Create a new task by the given name, ensure that the folder for this task
        exists and has the expected directories and files. If a project is
        specified, register the task underneath it
        """
        # TODO(#101) consider offloading this state management to the MephistoDB
        # as it is data handling and can theoretically be done differently
        # in different implementations
        assert (
            task_type in VALID_TASK_TYPES
        ), f"Given task type {task_type} is not recognized in {VALID_TASK_TYPES}"
        assert (
            len(db.find_tasks(task_name=task_name)) == 0
        ), f"A task named {task_name} already exists!"

        new_task_dir = get_dir_for_task(task_name, not_exists_ok=True)
        assert new_task_dir is not None, "Should always be able to make a new task dir"
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
                    skip_input=skip_input,
                )
                os.rmdir(new_task_dir)
            os.mkdir(new_task_dir)
            copytree(parent_task_dir, new_task_dir)

        project_id = None if project is None else project.db_id
        parent_task_id = None if parent_task is None else parent_task.db_id
        db_id = db.new_task(task_name, task_type, project_id, parent_task_id)
        return Task.get(db, db_id)

        def __repr__(self):
            return f"Task-{self.task_name} [{self.task_type}]"
