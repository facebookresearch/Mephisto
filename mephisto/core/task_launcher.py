#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


# TODO(#99) do we standardize some kinds of data loader formats? perhaps
# one that loads from files, and then an arbitrary kind? Simple
# interface could be like an iterator. This class will launch tasks
# as if the loader is an iterator.

from mephisto.data_model.assignment import (
    Assignment,
    Unit,
    InitializationData,
    AssignmentState,
)

from typing import Dict, Optional, List, Any, TYPE_CHECKING

import os
import time

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB

import threading
from mephisto.core.logger_core import get_logger

logger = get_logger(name=__name__, verbose=True, level="info")

UNIT_GENERATOR_WAIT_SECONDS = 10


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
        max_num_concurrent_units: int = 2,
    ):
        """Prepare the task launcher to get it ready to launch the assignments"""
        self.db = db
        self.task_run = task_run
        self.assignment_data_list = assignment_data_list
        self.assignments: List[Assignment] = []
        self.units: List[Unit] = []
        self.provider_type = task_run.get_provider().PROVIDER_TYPE
        self.max_num_concurrent_units = max_num_concurrent_units
        self.launched_units: Dict[str, Unit] = {}
        self.unlaunched_units: Dict[str, Unit] = {}
        self.keep_launching: bool = False
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
                self.unlaunched_units[unit_id] = Unit(self.db, unit_id)
                self.keep_launching = True

    def generate_units(self):
        """ units generator which checks that only 'max_num_concurrent_units' running at the same time,
        i.e. in the LAUNCHED or ASSIGNED states """
        while self.keep_launching:
            units_id_to_remove = []
            for db_id, unit in self.launched_units.items():
                status = unit.get_status()
                if (
                    status != AssignmentState.LAUNCHED
                    and status != AssignmentState.ASSIGNED
                ):
                    units_id_to_remove.append(db_id)
            for db_id in units_id_to_remove:
                self.launched_units.pop(db_id)

            num_avail_units = self.max_num_concurrent_units - len(self.launched_units)
            units_id_to_remove = []
            for i, item in enumerate(self.unlaunched_units.items()):
                db_id, unit = item
                if i < num_avail_units:
                    self.launched_units[unit.db_id] = unit
                    units_id_to_remove.append(db_id)
                    yield unit
                else:
                    break
            for db_id in units_id_to_remove:
                self.unlaunched_units.pop(db_id)

            time.sleep(UNIT_GENERATOR_WAIT_SECONDS)
            if not self.unlaunched_units:
                break

    def _launch_limited_units(self, url: str) -> None:
        """ use units' generator to launch limited number of units according to (max_num_concurrent_units)"""
        for unit in self.generate_units():
            unit.launch(url)

    def launch_units(self, url: str) -> None:
        """launch any units registered by this TaskLauncher"""
        if self.max_num_concurrent_units > 0:
            thread = threading.Thread(target=self._launch_limited_units, args=(url,))
            thread.start()
        else:
            for db_id, unit in self.unlaunched_units.items():
                unit.launch(url)

    def expire_units(self) -> None:
        """Clean up all units on this TaskLauncher"""
        self.keep_launching = False
        for unit in self.units:
            try:
                unit.expire()
            except Exception as e:
                logger.exception(
                    f"Warning: failed to expire unit {unit.db_id}. Stated error: {e}",
                    exc_info=True,
                )
