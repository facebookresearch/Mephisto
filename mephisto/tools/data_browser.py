#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.database import MephistoDB
from mephisto.data_model.assignment import Unit
from mephisto.data_model.task_run import TaskRun
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.agent import Agent

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.constants.assignment_state import AssignmentState

from typing import List, Optional, Any, Dict


class DataBrowser:
    """
    Class with convenience methods for getting completed data
    back from runs to parse and manage with other scripts
    """

    def __init__(self, db=None):
        if db is None:
            db = LocalMephistoDB()
        self.db = db

    def _get_units_for_task_runs(self, task_runs: List[TaskRun]) -> List[Unit]:
        units = []
        for task_run in task_runs:
            assignments = task_run.get_assignments()
            for assignment in assignments:
                found_units = assignment.get_units()
                for unit in found_units:
                    if unit.get_status() in [
                        AssignmentState.COMPLETED,
                        AssignmentState.ACCEPTED,
                        AssignmentState.REJECTED,
                        AssignmentState.SOFT_REJECTED,
                    ]:
                        units.append(unit)
        return units

    def get_units_for_task_name(self, task_name: str) -> List[Unit]:
        tasks = self.db.find_tasks(task_name=task_name)
        assert len(tasks) >= 1, f"No task found under name {task_name}"
        task_runs = self.db.find_task_runs(task_id=tasks[0].db_id)
        return self._get_units_for_task_runs(task_runs)

    def get_units_for_run_id(self, run_id: str) -> List[Unit]:
        task_run = TaskRun(self.db, run_id)
        return self._get_units_for_task_runs([task_run])

    def get_data_from_unit(self, unit: Unit) -> Dict[str, Any]:
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
        }
