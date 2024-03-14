#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import random
from abc import ABC
from typing import Any
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.data_model.constants.assignment_state import AssignmentState

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit


class UnitPrioritizer(ABC):
    def __init__(self, task_run: "TaskRun"):
        self.task_run = task_run

    def reserve_unit(self, available_units: List["Unit"]) -> Optional["Unit"]:
        """
        Reserve the next unit, according to the indicated `unit_prioritizing_strategy` task param
        """
        reserved_unit = None
        unit_index_to_reserve = self.find_next_index_to_reserve(available_units)

        if unit_index_to_reserve is None:
            return reserved_unit

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop(unit_index_to_reserve)
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit

    def find_next_index_to_reserve(self, available_items: List[Any]) -> Optional[int]:
        """
        Identify the next unit index to be reserved from `available_units`.
        Abstract method to be overridden for each particular prioritizing strategy.
        """
        raise NotImplementedError


class FIFOUnitPrioritizer(UnitPrioritizer):
    def find_next_index_to_reserve(self, available_items: List[Any]) -> Optional[int]:
        return 0


class LIFOUnitPrioritizer(UnitPrioritizer):
    def find_next_index_to_reserve(self, available_items: List[Any]) -> Optional[int]:
        return -1


class RandomUnitPrioritizer(UnitPrioritizer):
    def find_next_index_to_reserve(self, available_items: List[Any]) -> Optional[int]:
        if not available_items:
            return None
        return random.randint(0, len(available_items) - 1)


class RandomAssignmentUnitPrioritizer(RandomUnitPrioritizer):
    def reserve_unit(self, available_units: List["Unit"]) -> Optional["Unit"]:
        reserved_unit = None

        started_assignment_ids = list(set([
            unit.assignment_id
            for unit in available_units
            if unit.get_assignment().get_status() == AssignmentState.LAUNCHED
        ]))

        random_assignment_index = self.find_next_index_to_reserve(started_assignment_ids)
        if random_assignment_index is None:
            return reserved_unit

        random_assignment_id = started_assignment_ids[random_assignment_index]
        available_units_from_random_assignment = [
            unit
            for unit in available_units
            if unit.assignment_id == random_assignment_id
        ]

        while len(available_units_from_random_assignment) > 0 and reserved_unit is None:
            unit = available_units_from_random_assignment.pop(0)
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit
