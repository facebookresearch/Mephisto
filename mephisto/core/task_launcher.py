#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


# TODO do we standardize some kinds of data loader formats? perhaps
# one that loads from files, and then an arbitrary kind? Simple
# interface could be like an iterator. This class will launch tasks
# as if the loader is an iterator.

from mephisto.data_model.assignment import Assignment, Unit, InitializationData

from typing import Dict, Optional, List, Any, TYPE_CHECKING

import os

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB


class TaskLauncher:
    """
    This class is responsible for managing the process of registering
    and launching units, including the steps for pre-processing
    data and storing them locally for assignments when appropriate.
    """

    def __init__(
        self,
        db: "MephistoDB",
        task_run: "TaskRun",
        assignment_data_list: List[InitializationData],
    ):
        """Prepare the task launcher to get it ready to launch the assignments"""
        self.db = db
        self.task_run = task_run
        self.assignment_data_list = assignment_data_list
        self.assignments: List[Assignment] = []
        self.units: List[Unit] = []
        self.provider_type = task_run.get_provider().PROVIDER_TYPE

        run_dir = task_run.get_run_dir()
        os.makedirs(run_dir, exist_ok=True)

    def create_assignments(self) -> None:
        """
        Create an assignment and associated units for any data
        currently in the assignment config
        """
        task_run = self.task_run
        task_config = task_run.get_task_config()
        for data in self.assignment_data_list:
            assignment_id = self.db.new_assignment(
                task_run.task_id,
                task_run.db_id,
                task_run.requester_id,
                task_run.task_type,
                task_run.provider_type,
                task_run.sandbox,
            )
            assignment = Assignment(self.db, assignment_id)
            assignment.write_assignment_data(data)
            self.assignments.append(assignment)
            unit_count = len(data["unit_data"])
            for unit_idx in range(unit_count):
                unit_id = self.db.new_unit(
                    task_run.task_id,
                    task_run.db_id,
                    task_run.requester_id,
                    assignment_id,
                    unit_idx,
                    task_config.task_reward,
                    task_run.provider_type,
                    task_run.task_type,
                    task_run.sandbox,
                )
                self.units.append(Unit(self.db, unit_id))

    def launch_units(self, url: str) -> None:
        """launch any units registered by this TaskLauncher"""
        for unit in self.units:
            unit.launch(url)

    def expire_units(self) -> None:
        """Clean up all units on this TaskLauncher"""
        for unit in self.units:
            unit.expire()
