#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractmethod
from mephisto.core.utils import get_dir_for_run, get_crowd_provider_from_type
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.task import TaskRun
from mephisto.data_model.agent import Agent
from typing import List, Optional, Tuple, Dict, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.crowd_provider import CrowdProvider

import os
import json


ASSIGNMENT_DATA_FILE = "assign_data.json"


class Assignment:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of units within via abstracted database helpers
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        self.db_id: str = db_id
        self.db: "MephistoDB" = db
        row = db.get_assignment(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.task_run_id = row["task_run_id"]

    def get_assignment_data(self) -> Optional[Dict[str, Any]]:
        """Return the specific assignment data for this assignment"""
        task_run = TaskRun(self.db, self.task_run_id)
        run_dir = task_run.get_run_dir()
        assign_data_filename = os.path.join(run_dir, self.db_id, ASSIGNMENT_DATA_FILE)
        if os.path.exists(assign_data_filename):
            with open(assign_data_filename, "r") as json_file:
                return json.load(json_file)
        return None

    def get_status(self) -> str:
        """
        Get the status of this assignment, as determined by the status of
        the sub-assignments
        """
        units = self.get_units()
        statuses = set(unit.get_status() for unit in units)
        if len(statuses) == 1:
            return statuses.pop()

        # TODO parse statuses and return a computed status
        # ASSIGNED is any are still assigned
        # MIXED is any form of review status that remains
        raise NotImplementedError()

    def get_task_run(self) -> TaskRun:
        """
        Return the task run that this assignment is part of
        """
        return TaskRun(self.db, self.task_run_id)

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

    # TODO add helpers to manage retrieving results as well

    @staticmethod
    def new(
        db: "MephistoDB", task_run: TaskRun, assignment_data: Optional[Dict[str, Any]]
    ) -> "Assignment":
        """
        Create an assignment for the given task. Initialize the folders for storing
        the results for this assignment. Can take assignment_data to save and
        load for this particular assignment.
        """
        # TODO consider offloading this state management to the MephistoDB
        # as it is data handling and can theoretically be done differently
        # in different implementations
        db_id = db.new_assignment(task_run.db_id)
        run_dir = task_run.get_run_dir()
        assign_dir = os.path.join(run_dir, db_id)
        os.makedirs(assign_dir)
        if assignment_data is not None:
            with open(
                os.path.join(assign_dir, ASSIGNMENT_DATA_FILE), "w+"
            ) as json_file:
                json.dump(assignment_data, json_file)
        return Assignment(db, db_id)


class Unit(ABC):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.

    It should be extended for usage with a specific crowd provider
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        self.db_id: str = db_id
        self.db: "MephistoDB" = db
        row = db.get_unit(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.assignment_id = row["assignment_id"]
        self.unit_index = row["unit_index"]
        self.pay_amount = row["pay_amount"]
        self.agent_id = row["agent_id"]
        self.provider_type = row["provider_type"]
        self.db_status = row["status"]

    def __new__(cls, db: "MephistoDB", db_id: str) -> "Unit":
        """
        The new method is overridden to be able to automatically generate
        the expected Unit class without needing to specifically find it
        for a given db_id. As such it is impossible to create a Unit
        as you will instead be returned the correct Unit class according to
        the crowdprovider associated with this Unit.
        """
        if cls == Unit:
            # We are trying to construct a Unit, find what type to use and
            # create that instead
            row = db.get_unit(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(row["provider_type"]).UnitClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def get_crowd_provider_class(self) -> Type["CrowdProvider"]:
        """Get the CrowdProvider class that manages this Unit"""
        return get_crowd_provider_from_type(self.provider_type)

    def get_assignment_data(self) -> Optional[Dict[str, Any]]:
        """Return the specific assignment data for this assignment"""
        # TODO maybe this is somewhat controlled by task-types?
        return self.get_assignment().get_assignment_data()

    def get_db_status(self) -> str:
        """
        Return the status as currently stored in the database
        """
        if self.db_status in AssignmentState.final_unit():
            return self.db_status
        row = self.db.get_unit(self.db_id)
        assert row is not None, f"Unit {self.db_id} stopped existing in the db..."
        return row["status"]

    def set_db_status(self, status: str) -> None:
        """
        Set the status reflected in the database for this Unit
        """
        assert (
            status in AssignmentState.valid_unit()
        ), f"{status} not valid Assignment Status, not in {AssignmentState.valid_unit()}"
        self.db.update_unit(self.db_id, status=status)

    def get_assignment(self) -> Assignment:
        """
        Return the assignment that this Unit is part of.
        """
        return Assignment(self.db, self.assignment_id)

    def get_assigned_agent(self) -> Optional[Agent]:
        """
        Get the agent assigned to this Unit if there is one, else return None
        """
        # In these statuses, we know the agent isn't changing anymore, and thus will
        # not need to be re-queried
        # TODO add test to ensure this behavior/assumption holds always
        if self.db_status in AssignmentState.final_unit():
            return Agent(self.db, self.agent_id)

        # Query the database to get the most up-to-date assignment, as this can
        # change after instantiation if the Unit status isn't final
        row = self.db.get_unit(self.db_id)
        assert row is not None, f"Unit {self.db_id} stopped existing in the db..."
        agent_id = row["agent_id"]
        if agent_id is not None:
            return Agent(self.db, agent_id)
        return None

    @staticmethod
    def _register_unit(
        db: "MephistoDB",
        assignment: Assignment,
        index: int,
        pay_amount: float,
        provider_type: str,
    ) -> "Unit":
        """
        Create an entry for this unit in the database
        """
        db_id = db.new_unit(assignment.db_id, index, pay_amount, provider_type)
        return Unit(db, db_id)

    def get_pay_amount(self) -> float:
        """
        Return the amount that this Unit is costing against the budget,
        calculating additional fees as relevant
        """
        return self.pay_amount

    # Children classes should implement the below methods

    def get_status(self) -> str:
        """
        Get the status of this unit, as determined by whether there's
        a worker working on it at the moment, and any other possible states. Should
        return one of UNIT_STATUSES

        Status is crowd-provider dependent, and thus this method should be defined
        in the child class.
        """
        raise NotImplementedError()

    def launch(self) -> None:
        """
        Make this Unit available on the crowdsourcing vendor. Depending on
        the task type, this could mean a number of different setup steps.

        Some crowd providers require setting up a configuration for the
        very first launch, and this method should call a helper to manage
        that step if necessary.
        """
        raise NotImplementedError()

    def expire(self) -> float:
        """
        Expire this unit, removing it from being workable on the vendor.
        Return the maximum time needed to wait before we know it's taken down.
        """
        raise NotImplementedError()

    def is_expired(self) -> bool:
        """Determine if this unit is expired as according to the vendor."""
        raise NotImplementedError()

    @staticmethod
    def new(
        db: "MephistoDB", assignment: Assignment, index: int, pay_amount: float
    ) -> "Unit":
        """
        Create a Unit for the given assignment

        Implementation should return the result of _register_unit when sure the unit
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()
