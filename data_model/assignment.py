#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.task import Task, TaskRun
from mephisto.data_model.worker import Worker, Agent
from mephisto.core.utils import get_dir_for_run, get_crowd_provider_from_type
from typing import List, Optional, Tuple, Dict
import os
import json

ASSIGNMENT_STATUSES = [
    # TODO put all the valid assignment statuses here
    # LAUNCHED
    # ASSIGNED
    # COMPLETED
    # ACCEPTED
    # MIXED
    # REJECTED
    # EXPIRED
]

UNIT_STATUSES = [
    # TODO put all the valid unit statuses here
    # LAUNCHED
    # ASSIGNED
    # COMPLETED
    # ACCEPTED
    # REJECTED
    # EXPIRED
]

FINAL_UNIT_AGENT_STATUSES = [
    # TODO put all the statuses after which the agent is not going to change
    # COMPLETED
    # ACCEPTED
    # REJECTED
    # EXPIRED
]

FINAL_UNIT_STATUSES = [
    # TODO put all statuses that should never change once assigned
    # ACCEPTED
    # EXPIRED
]

ASSIGNMENT_DATA_FILE = "assign_data.json"


class Assignment:
    """
    This class tracks an individual run of a specific task, and handles state management
    for the set of units within via abstracted database helpers
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        row = db.get_assignment(db_id)
        self.task_run_id = row["task_run_id"]

    def get_assignment_data(self) -> Optional[Dict[str, Any]]:
        """Return the specific assignment data for this assignment"""
        task_run = TaskRun(self.db, self.task_run_id)
        run_dir = task_run.get_run_dir()
        assign_data_filename = os.path.join(run_dir, self.db_id, ASSIGNMENT_DATA_FILE)
        if os.path.exists(assign_data_filename):
            with open(os.path.join(assign_dir, ASSIGNMENT_DATA_FILE), "r") as json_file:
                return json.load(json_file)
        return None

    def get_status(self) -> str:
        """
        Get the status of this assignment, as determined by the status of
        the sub-assignments
        """
        units = self.get_units()
        statuses = set(unit.get_status() for unit in units])
        if len(statuses) == 1:
            return statuses[0]

        # TODO parse statuses and return a computed status
        # ASSIGNED is any are still assigned
        # MIXED is any form of review status that remains
        raise NotImplementedError()

    def get_task_run(self) -> TaskRun:
        """
        Return the task run that this assignment is part of
        """
        return TaskRun(self.db, self.task_run_id)

    def get_units(self, status: Optional[str]) -> List[Unit]:
        """
        Get units for this assignment, optionally
        constrained by the specific status.
        """
        assert (
            status is None or status in UNIT_STATUSES
        ), "Invalid assignment status"
        units = self.db.find_units(assignment_id=self.assignment_id)
        if status is not None:
            units = [u for u in units if u.get_status() == status]
        return units

    def get_workers(self) -> List[Worker]:
        """
        Get the list of workers that have worked on this specific assignment
        """
        units = self.get_units()
        pos_agents = [s.get_assigned_agent() for s in units]
        agents = [a for a in pos_agents if a is not None]
        workers = [a.get_worker() for a in agents]
        return workers

    # TODO add helpers to manage retrieving results as well

    @staticmethod
    def new(
        db: MephistoDB, task_run: TaskRun, assignment_data: Optional[Dict[str, Any]]
    ) -> Assignment:
        """
        Create an assignment for the given task. Initialize the folders for storing
        the results for this assignment. Can take assignment_data to save and
        load for this particular assignment.
        """
        db_id = db.new_assignment(task_run.db_id)
        run_dir = task_run.get_run_dir()
        assign_dir = os.path.join(run_dir, db_id)
        os.makedirs(assign_dir)
        if assignment_json is not None:
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

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        row = db.get_unit(db_id)
        self.assignment_id = row['assignment_id']
        self.unit_index = row['unit_index']
        self.pay_amount = row['pay_amount']
        self.agent_id = row['agent_id']
        self.crowd_provider = get_crowd_provider_from_type(row['provider_type'])
        self.db_status = row['status']

    def get_assignment_data(self) -> Optional[Dict[str, Any]]:
        """Return the specific assignment data for this assignment"""
        # TODO maybe this is somewhat controlled by task-types?
        return self.get_assignment().get_assignment_data()

    def get_db_status(self) -> str:
        """
        Return the status as currently stored in the database
        """
        if self.db_status in FINAL_UNIT_STATUSES:
            return self.db_status
        row = self.db.get_unit(self.db_id)
        return row['status']

    def set_db_status(self, status: str) -> None:
        """
        Set the status reflected in the database for this Unit
        """
        assert status in UNIT_STATUSES, f'{status} not valid Assignment Status, not in {UNIT_STATUSES}'
        self.db.update_unit(self.db_id, status=status)

    @abstractmethod
    def get_status(self) -> str:
        """
        Get the status of this unit, as determined by whether there's
        a worker working on it at the moment, and any other possible states. Should
        return one of UNIT_STATUSES

        Status is crowd-provider dependent, and thus this method should be defined
        in the child class.
        """
        raise NotImplementedError()

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
        if self.db_status in FINAL_UNIT_AGENT_STATUSES:
            return self.crowd_provider.CrowdAgent(self.db, self.agent_id)

        # Query the database to get the most up-to-date assignment, as this can
        # change after instantiation if the Unit status isn't final
        row = self.db.get_unit(self.db_id)
        agent_id = row['agent_id']
        if agent_id is not None:
            return self.crowd_provider.CrowdAgent(self.db, agent_id)
        return None

    @abstractstaticmethod
    def new(db: MephistoDB, assignment: Assignment, index: int, pay_amount: float) -> Unit:
        """
        Create a Unit for the given assignment via the crowd provider for this version
        """
        raise NotImplementedError()
