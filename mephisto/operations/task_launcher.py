#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.data_model.assignment import (
    Assignment,
    InitializationData,
    AssignmentState,
)
from mephisto.data_model.unit import (
    Unit,
    SCREENING_UNIT_INDEX,
    GOLD_UNIT_INDEX,
    COMPENSATION_UNIT_INDEX,
)

from typing import Dict, Optional, List, Any, TYPE_CHECKING, Iterator, Iterable
from tqdm import tqdm  # type: ignore
import os
import time
import enum

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.database import MephistoDB
import threading
from mephisto.utils.logger_core import get_logger
import types

logger = get_logger(name=__name__)

UNIT_GENERATOR_WAIT_SECONDS = 10
ASSIGNMENT_GENERATOR_WAIT_SECONDS = 0.5


class GeneratorType(enum.Enum):
    NONE = 0
    UNIT = 1
    ASSIGNMENT = 2


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
        assignment_data_iterator: Iterable[InitializationData],
        max_num_concurrent_units: int = 0,
    ):
        """Prepare the task launcher to get it ready to launch the assignments"""
        self.db = db
        self.task_run = task_run
        self.assignment_data_iterable = assignment_data_iterator
        self.assignments: List[Assignment] = []
        self.units: List[Unit] = []
        self.provider_type = task_run.get_provider().PROVIDER_TYPE
        self.UnitClass = task_run.get_provider().UnitClass
        self.max_num_concurrent_units = max_num_concurrent_units
        self.launched_units: Dict[str, Unit] = {}
        self.unlaunched_units: Dict[str, Unit] = {}
        self.keep_launching_units: bool = False
        self.finished_generators: bool = False
        self.assignment_thread_done: bool = True
        self.launch_url: Optional[str] = None

        self.unlaunched_units_access_condition = threading.Condition()
        if isinstance(self.assignment_data_iterable, types.GeneratorType):
            self.generator_type = GeneratorType.ASSIGNMENT
            self.assignment_thread_done = False
        elif max_num_concurrent_units != 0:
            self.generator_type = GeneratorType.UNIT
        else:
            self.generator_type = GeneratorType.NONE
        run_dir = task_run.get_run_dir()
        os.makedirs(run_dir, exist_ok=True)

        logger.debug(f"type of assignment data: {type(self.assignment_data_iterable)}")
        self.units_thread: Optional[threading.Thread] = None
        self.assignments_thread: Optional[threading.Thread] = None

    def _create_single_assignment(self, assignment_data) -> None:
        """Create a single assignment in the database using its read assignment_data"""
        task_run = self.task_run
        task_args = task_run.get_task_args()
        assignment_id = self.db.new_assignment(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
            task_run.sandbox,
        )
        assignment = Assignment.get(self.db, assignment_id)
        assignment.write_assignment_data(assignment_data)
        self.assignments.append(assignment)
        unit_count = len(assignment_data.unit_data)
        for unit_idx in range(unit_count):
            unit = self.UnitClass.new(
                self.db, assignment, unit_idx, task_args.task_reward
            )
            self.units.append(unit)
            with self.unlaunched_units_access_condition:
                self.unlaunched_units[unit.db_id] = unit

    def _try_generating_assignments(
        self, assignment_data_iterator: Iterator[InitializationData]
    ) -> None:
        """Try to generate more assignments from the assignments_data_iterator"""
        while not self.finished_generators:
            try:
                data = next(assignment_data_iterator)
                self._create_single_assignment(data)
            except StopIteration:
                self.assignment_thread_done = True
            time.sleep(ASSIGNMENT_GENERATOR_WAIT_SECONDS)

    def create_assignments(self) -> None:
        """Create an assignment and associated units for the generated assignment data"""
        self.keep_launching_units = True
        if self.generator_type != GeneratorType.ASSIGNMENT:
            for data in self.assignment_data_iterable:
                self._create_single_assignment(data)
        else:
            assert isinstance(
                self.assignment_data_iterable, types.GeneratorType
            ), "Must have assignment data generator for this"
            self.assignments_thread = threading.Thread(
                target=self._try_generating_assignments,
                args=(self.assignment_data_iterable,),
                name="assignment-generator",
            )
            self.assignments_thread.start()

    def generate_units(self):
        """units generator which checks that only 'max_num_concurrent_units' running at the same time,
        i.e. in the LAUNCHED or ASSIGNED states"""
        while self.keep_launching_units:
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
            num_avail_units = (
                len(self.unlaunched_units)
                if self.max_num_concurrent_units == 0
                else num_avail_units
            )

            units_id_to_remove = []
            for i, item in enumerate(self.unlaunched_units.items()):
                db_id, unit = item
                if i < num_avail_units:
                    self.launched_units[unit.db_id] = unit
                    units_id_to_remove.append(db_id)
                    yield unit
                else:
                    break
            with self.unlaunched_units_access_condition:
                for db_id in units_id_to_remove:
                    self.unlaunched_units.pop(db_id)

            time.sleep(UNIT_GENERATOR_WAIT_SECONDS)
            if not self.unlaunched_units:
                break

    def _launch_limited_units(self, url: str) -> None:
        """use units' generator to launch limited number of units according to (max_num_concurrent_units)"""
        # Continue launching if we haven't pulled the plug, so long as there are currently
        # units to launch, or more may come in the future.
        while not self.finished_generators and (
            len(self.unlaunched_units) > 0 or not self.assignment_thread_done
        ):
            for unit in self.generate_units():
                if unit is None:
                    break
                unit.launch(url)
            if self.generator_type == GeneratorType.NONE:
                break
        self.finished_generators = True

    def launch_units(self, url: str) -> None:
        """launch any units registered by this TaskLauncher"""
        self.launch_url = url
        self.units_thread = threading.Thread(
            target=self._launch_limited_units,
            args=(url,),
            name="unit-generator",
        )
        self.units_thread.start()

    def launch_evaluation_unit(
        self, unit_data: Dict[str, Any], unit_type_index: int
    ) -> "Unit":
        """Launch a specific evaluation unit, used for quality control"""
        assert (
            self.launch_url is not None
        ), "Cannot launch an evaluation unit before launching others"
        task_run = self.task_run
        task_args = task_run.get_task_args()
        assignment_id = self.db.new_assignment(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
            task_run.sandbox,
        )
        data = InitializationData(unit_data, [{}])
        assignment = Assignment.get(self.db, assignment_id)
        assignment.write_assignment_data(data)
        self.assignments.append(assignment)
        evaluation_unit = self.UnitClass.new(
            self.db, assignment, unit_type_index, task_args.task_reward
        )
        evaluation_unit.launch(self.launch_url)
        return evaluation_unit

    def launch_screening_unit(self, unit_data: Dict[str, Any]) -> "Unit":
        """Launch a screening unit, which should never return to the pool"""
        return self.launch_evaluation_unit(unit_data, SCREENING_UNIT_INDEX)

    def launch_gold_unit(self, unit_data: Dict[str, Any]) -> "Unit":
        """Launch a screening unit, which should never return to the pool"""
        return self.launch_evaluation_unit(unit_data, GOLD_UNIT_INDEX)

    def get_assignments_are_all_created(self) -> bool:
        return self.assignment_thread_done

    def expire_units(self) -> None:
        """Clean up all units on this TaskLauncher"""
        self.keep_launching_units = False
        self.finished_generators = True
        for unit in tqdm(self.units):
            try:
                unit.expire()
            except Exception as e:
                logger.exception(
                    f"Warning: failed to expire unit {unit.db_id}. Stated error: {e}",
                    exc_info=True,
                )

    def shutdown(self) -> None:
        """Clean up running threads for generating assignments and units"""
        self.assignment_thread_done = True
        self.keep_launching_units = False
        self.finished_generators = True
        if self.assignments_thread is not None:
            self.assignments_thread.join()
        if self.units_thread is not None:
            self.units_thread.join()
