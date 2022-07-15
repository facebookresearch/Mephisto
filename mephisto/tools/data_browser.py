#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.unit import Unit
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.worker import Worker

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.constants.assignment_state import AssignmentState

from typing import List, Any, Dict


class DataBrowser:
    """
    Class with convenience methods for getting completed data
    back from runs to parse and manage with other scripts
    """

    def __init__(self, db=None):
        if db is None:
            db = LocalMephistoDB()
        self.db = db

    def collect_matching_units_from_task_runs(
        self, task_runs: List[TaskRun], statuses: List[str]
    ) -> List[Unit]:
        """
        Loops through task_runs to collect all units in the provided statuses list
        """
        units = []
        for task_run in task_runs:
            assignments = task_run.get_assignments()
            for assignment in assignments:
                found_units = assignment.get_units()
                for unit in found_units:
                    if unit.get_status() in statuses:
                        units.append(unit)
        return units

    def _get_units_for_task_runs(self, task_runs: List[TaskRun]) -> List[Unit]:
        """
        Return a list of all Units in a terminal completed state from all
        the provided TaskRuns.
        """
        return self.collect_matching_units_from_task_runs(
            task_runs, AssignmentState.completed()
        )

    def _get_all_units_for_task_runs(self, task_runs: List[TaskRun]) -> List[Unit]:
        """
        Does the same as _get_units_for_task_runs except that it includes the EXPIRED state
        """
        return self.collect_matching_units_from_task_runs(
            task_runs, AssignmentState.final_agent()
        )

    def get_task_name_list(self) -> List[str]:
        return [task.task_name for task in self.db.find_tasks()]

    def get_units_for_task_name(self, task_name: str) -> List[Unit]:
        """
        Return a list of all Units in a terminal completed state from all
        task runs with the given task_name
        """
        tasks = self.db.find_tasks(task_name=task_name)
        assert len(tasks) >= 1, f"No task found under name {task_name}"
        task_runs = self.db.find_task_runs(task_id=tasks[0].db_id)
        return self._get_units_for_task_runs(task_runs)

    def get_all_units_for_task_name(self, task_name: str) -> List[Unit]:
        tasks = self.db.find_tasks(task_name=task_name)
        assert len(tasks) >= 1, f"No task found under name {task_name}"
        task_runs = self.db.find_task_runs(task_id=tasks[0].db_id)
        return self._get_all_units_for_task_runs(task_runs)

    def get_units_for_run_id(self, run_id: str) -> List[Unit]:
        """
        Return a list of all Units in a terminal completed state from the
        task run with the given run_id
        """
        task_run = TaskRun.get(self.db, run_id)
        return self._get_units_for_task_runs([task_run])

    def get_data_from_unit(self, unit: Unit) -> Dict[str, Any]:
        """
        Return a dict containing all data associated with the given
        unit, including its status, data, and start and end time.

        Also includes the DB ids for the worker, the unit, and the
        relevant assignment this unit was a part of.
        """
        agent = unit.get_assigned_agent()
        assert (
            agent is not None
        ), f"Trying to get completed data from unassigned unit {unit}"
        return {
            "worker_id": agent.worker_id,
            "unit_id": unit.db_id,
            "assignment_id": unit.assignment_id,
            "status": agent.db_status,
            "data": agent.state.get_parsed_data(),
            "task_start": agent.state.get_task_start(),
            "task_end": agent.state.get_task_end(),
            "tips": agent.state.get_tips(),
            "feedback": agent.state.get_feedback(),
        }

    def get_workers_with_qualification(self, qualification_name: str) -> List[Worker]:
        """
        Returns a list of 'Worker's for workers who are qualified wrt `qualification_name`.
        """
        qual_list = self.db.find_qualifications(qualification_name=qualification_name)
        assert len(qual_list) >= 1, f"No qualification found named {qualification_name}"
        qualification_id = qual_list[0].db_id
        qualifieds = self.db.check_granted_qualifications(
            qualification_id=qualification_id, value=1
        )
        return [Worker.get(self.db, qual.worker_id) for qual in qualifieds]

    def get_metadata_property_from_task_name(
        self, task_name: str, property_name: str
    ) -> List[Any]:
        """Returns all metadata for a task by going through its agents"""

        units = self.get_all_units_for_task_name(task_name=task_name)
        result: List[Any] = []

        for unit in units:
            if unit.agent_id is not None:
                unit_data = self.get_data_from_unit(unit)

                assert property_name in unit_data, (
                    "The {property_name} field must exist in the unit's data. Look for {property_name} in the get_data_from_unit function"
                ).format(property_name=property_name)

                unit_property_val = unit_data[property_name]
                if unit_property_val is not None:
                    result = result + unit_property_val

        return result
