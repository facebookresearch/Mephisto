#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.agent import Agent
from mephisto.data_model.requester import Requester
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)
from typing import List, Optional, Mapping, Dict, Any, TYPE_CHECKING, IO

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.unit import Unit

import os
import json
from dataclasses import dataclass

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)

ASSIGNMENT_DATA_FILE = "assign_data.json"


@dataclass
class InitializationData:
    shared: Dict[str, Any]
    unit_data: List[Dict[str, Any]]

    def dumpJSON(self, fp: IO[str]):
        return json.dump({"shared": self.shared, "unit_data": self.unit_data}, fp)

    @staticmethod
    def loadFromJSON(fp: IO[str]):
        as_dict = json.load(fp)
        return InitializationData(
            shared=as_dict["shared"], unit_data=as_dict["unit_data"]
        )


class Assignment(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of units within via abstracted database helpers
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct Assignment and data model access via Assignment(db, id) is "
                "now deprecated in favor of calling Assignment.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_assignment(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["assignment_id"]
        self.task_run_id: str = row["task_run_id"]
        self.sandbox: bool = row["sandbox"]
        self.task_id: str = row["task_id"]
        self.requester_id: str = row["requester_id"]
        self.task_type: str = row["task_type"]
        self.provider_type: str = row["provider_type"]

        # Deferred loading of related entities
        self.__task_run: Optional["TaskRun"] = None
        self.__task: Optional["Task"] = None
        self.__requester: Optional["Requester"] = None

    def get_data_dir(self) -> str:
        """Return the directory we expect to find assignment data in"""
        task_run = self.get_task_run()
        run_dir = task_run.get_run_dir()
        return os.path.join(run_dir, self.db_id)

    def get_assignment_data(self) -> InitializationData:
        """Return the specific assignment data for this assignment"""
        assign_data_filename = os.path.join(self.get_data_dir(), ASSIGNMENT_DATA_FILE)
        assert os.path.exists(assign_data_filename), "No data exists for assignment"
        with open(assign_data_filename, "r") as json_file:
            return InitializationData.loadFromJSON(json_file)

    def write_assignment_data(self, data: InitializationData) -> None:
        """Set the assignment data for this assignment"""
        assign_data_filename = os.path.join(self.get_data_dir(), ASSIGNMENT_DATA_FILE)
        os.makedirs(self.get_data_dir(), exist_ok=True)
        with open(assign_data_filename, "w+") as json_file:
            data.dumpJSON(json_file)

    def get_agents(self) -> List[Optional["Agent"]]:
        """
        Return all of the agents for this assignment
        """
        units = self.get_units()
        return [u.get_assigned_agent() for u in units]

    def get_status(self) -> str:
        """
        Get the status of this assignment, as determined by the status of
        the units
        """
        units = self.get_units()
        statuses = set(unit.get_status() for unit in units)

        if len(statuses) == 1:
            return statuses.pop()

        if len(statuses) == 0:
            return AssignmentState.CREATED

        if AssignmentState.CREATED in statuses:
            return AssignmentState.CREATED

        if any([s == AssignmentState.LAUNCHED for s in statuses]):
            # If any are only launched, consider the whole thing launched
            return AssignmentState.LAUNCHED

        if any([s == AssignmentState.ASSIGNED for s in statuses]):
            # If any are still assigned, consider the whole thing assigned
            return AssignmentState.ASSIGNED

        if all(
            [
                s in [AssignmentState.ACCEPTED, AssignmentState.REJECTED]
                for s in statuses
            ]
        ):
            return AssignmentState.MIXED

        if all([s in AssignmentState.final_agent() for s in statuses]):
            return AssignmentState.COMPLETED

        raise NotImplementedError(f"Unexpected set of unit statuses {statuses}")

    def get_task_run(self) -> TaskRun:
        """
        Return the task run that this assignment is part of
        """
        if self.__task_run is None:
            self.__task_run = TaskRun.get(self.db, self.task_run_id)
        return self.__task_run

    def get_task(self) -> Task:
        """
        Return the task run that this assignment is part of
        """
        if self.__task is None:
            if self.__task_run is not None:
                self.__task = self.__task_run.get_task()
            else:
                self.__task = Task.get(self.db, self.task_id)
        return self.__task

    def get_requester(self) -> Requester:
        """
        Return the requester who offered this Assignment
        """
        if self.__requester is None:
            if self.__task_run is not None:
                self.__requester = self.__task_run.get_requester()
            else:
                self.__requester = Requester.get(self.db, self.requester_id)
        return self.__requester

    def get_units(self, status: Optional[str] = None) -> List["Unit"]:
        """
        Get units for this assignment, optionally
        constrained by the specific status.
        """
        assert (
            status is None or status in AssignmentState.valid_unit()
        ), "Invalid assignment status"
        units = self.db.find_units(assignment_id=self.db_id)
        if status is not None:
            units = [u for u in units if u.get_status() == status]
        return units

    def get_workers(self) -> List["Worker"]:
        """
        Get the list of workers that have worked on this specific assignment
        """
        units = self.get_units()
        pos_agents = [s.get_assigned_agent() for s in units]
        agents = [a for a in pos_agents if a is not None]
        workers = [a.get_worker() for a in agents]
        return workers

    def get_cost_of_statuses(self, statuses: List[str]) -> float:
        """
        Return the sum of all pay_amounts for every unit
        of this assignment with any of the given statuses
        """
        units = [u for u in self.get_units() if u.get_status() in statuses]
        sum_cost = 0.0
        for unit in units:
            sum_cost += unit.get_pay_amount()
        return sum_cost

    def __repr__(self) -> str:
        return f"Assignment({self.db_id})"

    @staticmethod
    def new(
        db: "MephistoDB", task_run: TaskRun, assignment_data: Optional[Dict[str, Any]]
    ) -> "Assignment":
        """
        Create an assignment for the given task. Initialize the folders for storing
        the results for this assignment. Can take assignment_data to save and
        load for this particular assignment.
        """
        # TODO(#567) consider offloading this state management to the MephistoDB
        # as it is data handling and can theoretically be done differently
        # in different implementations
        db_id = db.new_assignment(
            task_run.db_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
            task_run.sandbox,
        )
        run_dir = task_run.get_run_dir()
        assign_dir = os.path.join(run_dir, db_id)
        os.makedirs(assign_dir)
        if assignment_data is not None:
            with open(
                os.path.join(assign_dir, ASSIGNMENT_DATA_FILE), "w+"
            ) as json_file:
                json.dump(assignment_data, json_file)
        assignment = Assignment.get(db, db_id)
        logger.debug(f"{assignment} created for {task_run}")
        return assignment
