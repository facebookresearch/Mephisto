#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from shutil import copytree

from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.task_config import TaskConfig
from mephisto.core.utils import (
    get_tasks_dir,
    get_dir_for_task,
    ensure_user_confirm,
    get_dir_for_run,
)
from mephisto.core.registry import get_blueprint_from_type, get_crowd_provider_from_type

from functools import reduce

from typing import List, Optional, Tuple, Dict, cast, Mapping, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.blueprint import Blueprint
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.crowd_provider import CrowdProvider


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


class Task:
    """
    This class contains all of the required tidbits for launching a set of
    assignments, primarily by leveraging a blueprint. It also takes the 
    project name if this task is to be associated with a specific project.
    """

    def __init__(
        self, db: "MephistoDB", db_id: str, row: Optional[Mapping[str, Any]] = None
    ):
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
            return Project(self.db, self.project_id)
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
        return Task(db, db_id)

        def __repr__(self):
            return f"Task-{self.task_name} [{self.task_type}]"


class TaskRun:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of assignments within
    """

    def __init__(
        self, db: "MephistoDB", db_id: str, row: Optional[Mapping[str, Any]] = None
    ):
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_task_run(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["task_run_id"]
        self.task_id = row["task_id"]
        self.requester_id = row["requester_id"]
        self.param_string = row["init_params"]
        self.start_time = row["creation_date"]
        self.provider_type = row["provider_type"]
        self.task_type = row["task_type"]
        self.sandbox = row["sandbox"]
        self.assignments_generator_done: bool = None

        # properties with deferred loading
        self.__is_completed = row["is_completed"]
        self.__has_assignments = False
        self.__task_config: Optional["TaskConfig"] = None
        self.__task: Optional["Task"] = None
        self.__requester: Optional["Requester"] = None
        self.__run_dir: Optional[str] = None
        self.__blueprint: Optional["Blueprint"] = None
        self.__crowd_provider: Optional["CrowdProvider"] = None

    def get_units(self) -> List["Unit"]:
        """
        Return the units associated with this task run.
        """
        return self.db.find_units(task_run_id=self.db_id)

    def get_valid_units_for_worker(self, worker: "Worker") -> List["Unit"]:
        """
        Get any units that the given worker could work on in this
        task run
        """
        config = self.get_task_config()

        if config.allowed_concurrent != 0 or config.maximum_units_per_worker:
            current_units = self.db.find_units(
                task_run_id=self.db_id,
                worker_id=worker.db_id,
                status=AssignmentState.ASSIGNED,
            )
            currently_active = len(current_units)
            if config.allowed_concurrent != 0:
                if currently_active >= config.allowed_concurrent:
                    return []  # currently at the maximum number of concurrent units
            if config.maximum_units_per_worker != 0:
                currently_completed = len(
                    self.db.find_units(
                        task_id=self.task_id,
                        worker_id=worker.db_id,
                        status=AssignmentState.COMPLETED,
                    )
                )
                if (
                    currently_active + currently_completed
                    >= config.maximum_units_per_worker
                ):
                    return []  # Currently at the maximum number of units for this task

        task_units: List["Unit"] = self.get_units()
        unit_assigns: Dict[str, List["Unit"]] = {}
        for unit in task_units:
            assignment_id = unit.assignment_id
            if assignment_id not in unit_assigns:
                unit_assigns[assignment_id] = []
            unit_assigns[assignment_id].append(unit)

        # Cannot pair with self
        units: List["Unit"] = []
        for unit_set in unit_assigns.values():
            is_self_set = map(lambda u: u.worker_id == worker.db_id, unit_set)
            if not any(is_self_set):
                units += unit_set
        valid_units = [u for u in units if u.get_status() == AssignmentState.LAUNCHED]
        return valid_units

    def clear_reservation(self, unit: "Unit") -> None:
        """
        Remove the holder used to reserve a unit
        """
        file_name = f"unit_res_{unit.db_id}"
        write_dir = os.path.join(self.get_run_dir(), "reservations")
        if os.path.exists(os.path.join(write_dir, file_name)):
            os.unlink(os.path.join(write_dir, file_name))

    def reserve_unit(self, unit: "Unit") -> Optional["Unit"]:
        """
        'Atomically' reserve a unit by writing to the filesystem. If
        the file creation fails, return none
        """
        file_name = f"unit_res_{unit.db_id}"
        write_dir = os.path.join(self.get_run_dir(), "reservations")
        os.makedirs(write_dir, exist_ok=True)
        try:
            with open(os.path.join(write_dir, file_name), "x") as res_file:
                pass  # Creating the file is sufficient
        except FileExistsError:
            print(os.path.join(write_dir, file_name), " existed")
            return None
        return unit

    def get_blueprint(self, opts: Optional[Dict[str, Any]] = None) -> "Blueprint":
        """Return the runner associated with this task run"""
        if self.__blueprint is None:
            cache = False
            task_args = self.get_task_config().args
            if opts is not None:
                task_args.update(opts)
                cache = True
            BlueprintClass = get_blueprint_from_type(self.task_type)
            if not cache:
                return BlueprintClass(self, task_args)
            self.__blueprint = BlueprintClass(self, task_args)
        return self.__blueprint

    def get_provider(self) -> "CrowdProvider":
        """Return the crowd provider used to launch this task"""
        if self.__crowd_provider is None:
            CrowdProviderClass = get_crowd_provider_from_type(self.provider_type)
            self.__crowd_provider = CrowdProviderClass(self.db)
        return self.__crowd_provider

    def get_task(self) -> "Task":
        """Return the task used to initialize this run"""
        if self.__task is None:
            self.__task = Task(self.db, self.task_id)
        return self.__task

    def get_task_config(self) -> "TaskConfig":
        if self.__task_config is None:
            self.__task_config = TaskConfig(self)
        return self.__task_config

    def get_requester(self) -> Requester:
        """
        Return the requester that started this task.
        """
        if self.__requester is None:
            self.__requester = Requester(self.db, self.requester_id)
        return self.__requester

    def get_has_assignments(self) -> bool:
        """See if this task run has any assignments launched yet"""
        if not self.__has_assignments:
            if len(self.get_assignments()) > 0:
                self.__has_assignments = True
        return self.__has_assignments

    def get_assignments(self, status: Optional[str] = None) -> List["Assignment"]:
        """
        Get assignments for this run, optionally filtering by their
        current status
        """
        assert (
            status is None or status in AssignmentState.valid()
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
        assigns_with_status = [(x, x.get_status()) for x in assigns]
        return {
            status: len(
                [x for x, had_status in assigns_with_status if had_status == status]
            )
            for status in AssignmentState.valid()
        }

    def update_completion_progress(self, task_launcher=None, status=None) -> None:
        """ Flag the task run that the assignments' generator has finished """
        if task_launcher:
            if task_launcher.get_assignments_are_all_created():
                self.assignments_generator_done = True
        if status:
            self.assignments_generator_done = status

    def get_is_completed(self) -> bool:
        """get the completion status of this task"""
        self.sync_completion_status()
        return self.__is_completed

    def sync_completion_status(self) -> None:
        """
        Update the is_complete status for this task run based on completion
        of subassignments. If this task run has no subassignments yet, it
        is not complete
        """
        # TODO(#99) revisit when/if it's possible to add tasks to a completed run
        if not self.__is_completed and self.get_has_assignments():
            statuses = self.get_assignment_statuses()
            has_incomplete = False
            for status in AssignmentState.incomplete():
                if statuses[status] > 0:
                    has_incomplete = True
            if not has_incomplete and self.assignments_generator_done is not False:
                self.db.update_task_run(self.db_id, is_completed=True)
                self.__is_completed = True

    def get_run_dir(self) -> str:
        """
        Return the directory where the data from this run is stored
        """
        if self.__run_dir is None:
            task = self.get_task()
            project = task.get_project()
            if project is None:
                self.__run_dir = get_dir_for_run(self)
            else:
                self.__run_dir = get_dir_for_run(self, project.project_name)
            os.makedirs(self.__run_dir, exist_ok=True)
        return self.__run_dir

    def get_total_spend(self) -> float:
        """
        Return the total amount spent on this run, based on any assignments
        that are still in a payable state.
        """
        assigns = self.get_assignments()
        total_amount = 0.0
        for assign in assigns:
            total_amount += assign.get_cost_of_statuses(AssignmentState.payable())
        return total_amount

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict containing any important information about this task run"""
        return {
            "task_run_id": self.db_id,
            "task_id": self.task_id,
            "task_name": self.get_task().task_name,
            "task_type": self.task_type,
            "start_time": self.start_time,
            "params": self.get_task_config().args,
            "param_string": self.param_string,
            "task_status": self.get_assignment_statuses(),
            "sandbox": self.get_requester().is_sandbox(),
        }

    @staticmethod
    def new(
        db: "MephistoDB", task: Task, requester: Requester, param_string: str
    ) -> "TaskRun":
        """
        Create a new run for the given task with the given params
        """
        db_id = db.new_task_run(
            task.db_id,
            requester.db_id,
            param_string,
            requester.provider_type,
            task.task_type,
        )
        return TaskRun(db, db_id)
