#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import json
from dataclasses import dataclass, field

from mephisto.data_model.requester import Requester
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.utils.dirs import get_dir_for_run

from omegaconf import OmegaConf, MISSING

from typing import List, Optional, Dict, Mapping, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.assignment import Assignment
    from mephisto.abstractions.blueprint import Blueprint, SharedTaskState
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.data_model.task import Task
    from omegaconf import DictConfig

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


@dataclass
class TaskRunArgs:
    """Object for grouping the contents to configure a class"""

    task_name: Optional[str] = field(
        default=MISSING,
        metadata={
            "help": "Grouping to launch this task run under, none defaults to the blueprint type"
        },
    )
    task_title: str = field(
        default=MISSING,
        metadata={
            "help": "Display title for your task on the crowd provider.",
            "required": True,
        },
    )
    task_description: str = field(
        default=MISSING,
        metadata={
            "help": "Longer form description for what your task entails.",
            "required": True,
        },
    )
    task_reward: float = field(
        default=MISSING,
        metadata={
            "help": "Amount to pay per worker per unit, in dollars.",
            "required": True,
        },
    )
    task_tags: str = field(
        default=MISSING,
        metadata={
            "help": "Comma seperated tags for workers to use to find your task.",
            "required": True,
        },
    )
    task_lifetime_in_seconds: int = field(
        default=60 * 60 * 24 * 31,
        metadata={"help": "The time that the task will last for before expiring"},
    )
    assignment_duration_in_seconds: int = field(
        default=30 * 60,
        metadata={"help": "Time that workers have to work on your task once accepted."},
    )
    no_submission_patience: int = field(
        default=60 * 60 * 12,
        metadata={
            "help": (
                "How long to wait between task submissions before shutting the run down "
                "for a presumed issue. Value in seconds, default 12 hours. "
            )
        },
    )
    allowed_concurrent: int = field(
        default=0,
        metadata={
            "help": "Maximum units a worker is allowed to work on at once. (0 is infinite)",
            "required": True,
        },
    )
    maximum_units_per_worker: int = field(
        default=0,
        metadata={
            "help": (
                "Maximum tasks of this task name that a worker can work on across all "
                "tasks that share this task_name. (0 is infinite)"
            )
        },
    )
    max_num_concurrent_units: int = field(
        default=0,
        metadata={
            "help": (
                "Maximum units that will be released simultaneously, setting a limit "
                "on concurrent connections to Mephisto overall. (0 is infinite)"
            )
        },
    )
    submission_timeout: int = field(
        default=600,
        metadata={
            "help": (
                "Time that mephisto will wait after marking a task done before abandoning "
                "waiting for the worker to actually press submit."
            )
        },
    )

    post_install_script: str = field(
        default="",
        metadata={
            "help": (
                "The name of a shell script in your webapp directory that will run right after npm install and before npm build."
                "This can be useful for local package development where you would want to link a package after installing dependencies from package.json"
            )
        },
    )

    force_rebuild: bool = field(
        default=False,
        metadata={
            "help": (
                "Determines if npm build should be ran every time the task is ran."
                "By default there is an optimization that only builds the webapp when there is a change in its contents."
                "It would make sense to set this to true when doing local package development as you want to force a rebuild after running the post_install_script."
            )
        },
    )

    @classmethod
    def get_mock_params(cls) -> str:
        """Returns a param string with default / mock arguments to use for testing"""
        from mephisto.operations.hydra_config import MephistoConfig

        return OmegaConf.structured(
            MephistoConfig(
                task=TaskRunArgs(
                    task_title="Mock Task Title",
                    task_reward=0.3,
                    task_tags="mock,task,tags",
                    task_description="This is a test description",
                )
            )
        )


class TaskRun(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of assignments within
    """

    ArgsClass = TaskRunArgs

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct TaskRun and data model access via TaskRun(db, id) is "
                "now deprecated in favor of calling TaskRun.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_task_run(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["task_run_id"]
        self.task_id: str = row["task_id"]
        self.requester_id: str = row["requester_id"]
        self.param_string: str = row["init_params"]
        try:
            self.args: "DictConfig" = OmegaConf.create(json.loads(self.param_string))
        except Exception as e:
            self.args = OmegaConf.create({})
            print(e)
        self.start_time = row["creation_date"]
        self.provider_type: str = row["provider_type"]
        self.task_type: str = row["task_type"]
        self.sandbox: bool = row["sandbox"]
        self.assignments_generator_done: bool = False

        # properties with deferred loading
        self.__is_completed = row["is_completed"]
        self.__has_assignments = False
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
        config = self.get_task_args()

        # TODO(#773) handle with temporary local qualifications to allow
        # pushing real exclusionary qualifications after exceeding
        # maximum_units_per_worker
        if config.allowed_concurrent != 0 or config.maximum_units_per_worker:
            current_units = self.db.find_units(
                task_run_id=self.db_id,
                worker_id=worker.db_id,
                status=AssignmentState.ASSIGNED,
            )
            currently_active = len(current_units)
            if config.allowed_concurrent != 0:
                if currently_active >= config.allowed_concurrent:
                    logger.debug(
                        f"{worker} at maximum concurrent units {currently_active}"
                    )
                    return []  # currently at the maximum number of concurrent units
            if config.maximum_units_per_worker != 0:
                completed_types = AssignmentState.completed()
                related_units = self.db.find_units(
                    task_id=self.task_id,
                    worker_id=worker.db_id,
                )
                currently_completed = len(
                    [u for u in related_units if u.db_status in completed_types]
                )
                if (
                    currently_active + currently_completed
                    >= config.maximum_units_per_worker
                ):
                    logger.debug(
                        f"{worker} at maximum units {currently_active}, {currently_completed}"
                    )
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

        # Valid units must be launched and must not be special units (negative indices)
        # Can use db_status directly rather than polling in the critical path, as in
        # the worst case we miss the transition from an active to launched unit
        valid_units = [
            u
            for u in units
            if u.db_status == AssignmentState.LAUNCHED and u.unit_index >= 0
        ]
        logger.debug(f"Found {len(valid_units)} available units")

        # Should load cached blueprint for SharedTaskState
        blueprint = self.get_blueprint()
        ret_units = [
            u
            for u in valid_units
            if blueprint.shared_state.worker_can_do_unit(worker, u)
        ]

        logger.debug(f"This worker is qualified for {len(ret_units)} unit.")
        logger.debug(f"Found {ret_units[:3]} for {worker}.")
        return ret_units

    def clear_reservation(self, unit: "Unit") -> None:
        """
        Remove the holder used to reserve a unit
        """
        file_name = f"unit_res_{unit.db_id}"
        write_dir = os.path.join(self.get_run_dir(), "reservations")
        if os.path.exists(os.path.join(write_dir, file_name)):
            os.unlink(os.path.join(write_dir, file_name))
            logger.debug(f"Cleared reservation {file_name} for {unit}")

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
        logger.debug(f"Reserved {unit} with {file_name}")
        return unit

    def get_blueprint(
        self,
        args: Optional["DictConfig"] = None,
        shared_state: Optional["SharedTaskState"] = None,
    ) -> "Blueprint":
        """Return the runner associated with this task run"""
        from mephisto.operations.registry import get_blueprint_from_type
        from mephisto.abstractions.blueprint import SharedTaskState

        if self.__blueprint is None:
            cache = False
            if args is None:
                args = self.args
            else:
                cache = True

            BlueprintClass = get_blueprint_from_type(self.task_type)
            if shared_state is None:
                shared_state = BlueprintClass.SharedStateClass()
            if not cache:
                return BlueprintClass(self, args, shared_state)
            self.__blueprint = BlueprintClass(self, args, shared_state)
        return self.__blueprint

    def get_provider(self) -> "CrowdProvider":
        """Return the crowd provider used to launch this task"""
        from mephisto.operations.registry import get_crowd_provider_from_type

        if self.__crowd_provider is None:
            CrowdProviderClass = get_crowd_provider_from_type(self.provider_type)
            self.__crowd_provider = CrowdProviderClass(self.db)
        return self.__crowd_provider

    def get_task(self) -> "Task":
        """Return the task used to initialize this run"""
        if self.__task is None:
            from mephisto.data_model.task import Task

            self.__task = Task.get(self.db, self.task_id)
        return self.__task

    def get_task_args(self) -> "DictConfig":
        return self.args.task

    def get_requester(self) -> Requester:
        """
        Return the requester that started this task.
        """
        if self.__requester is None:
            self.__requester = Requester.get(self.db, self.requester_id)
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
        """Flag the task run that the assignments' generator has finished"""
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
            "params": OmegaConf.to_container(self.args),
            "param_string": self.param_string,
            "task_status": self.get_assignment_statuses(),
            "sandbox": self.get_requester().is_sandbox(),
        }

    def __repr__(self) -> str:
        return f"TaskRun({self.db_id})"

    @staticmethod
    def new(
        db: "MephistoDB", task: "Task", requester: Requester, param_string: str
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
        task_run = TaskRun.get(db, db_id)
        logger.debug(f"Created new task run {task_run}")
        return task_run
