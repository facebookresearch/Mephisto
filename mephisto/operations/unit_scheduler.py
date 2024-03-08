import random
from typing import List

from abc import ABC, abstractmethod
from mephisto.data_model.task_run import TaskRun
from random import shuffle
from mephisto.data_model.constants.assignment_state import AssignmentState


class UnitScheduler(ABC):

    def __init__(self, task_run: "TaskRun", prioritize_started_assignments: bool):
        self.task_run = task_run
        self.prioritize_started_assignments = prioritize_started_assignments

    def reserve_unit(self, available_units: List["Unit"]) -> Optional["Unit"]:
        """
        Reserve the next unit, according to the indicated `scheduling_strategy` task param
        """
        started_assignment_ids = []  # TODO: make a DB query for this
        available_units_from_started_assignments = [
            unit
            for unit in available_units
            if unit.assignment_id in started_assignment_ids
        ]

        unit_to_reserve = None
        if self.prioritize_started_assignments:
            # Before checking among all available units, check among prioritized one first
            unit_to_reserve = self.find_next_unit_to_reserve(available_units_from_started_assignments)
        if unit_to_reserve is None:
            unit_to_reserve = self.find_next_unit_to_reserve(available_units)

        available_units.remove(unit_to_reserve)
        reserved_unit = self.task_run.reserve_unit(unit_to_reserve)

        return reserved_unit

    def find_next_unit_to_reserve(self, available_units: List["Unit"]) -> Optional["Unit"]:
        """
        Identify the next unit to be reserved from `available_units`.
        Abstract method to be overridden for each particular scheduling strategy.
        """
        raise NotImplementedError


class FIFOUnitScheduler(UnitScheduler):
    def find_next_unit_to_reserve(self, available_units: List["Unit"]) -> Optional["Unit"]:
        if available_units:
            return available_units[0]


class LIFOUnitScheduler(UnitScheduler):

    def find_next_unit_to_reserve(self, available_units: List["Unit"]) -> Optional["Unit"]:
        if available_units:
            return available_units[-1]


class RandomUnitScheduler(UnitScheduler):

    def find_next_unit_to_reserve(self, available_units: List["Unit"]) -> Optional["Unit"]:
        if available_units:
            index = random.randint(0, len(available_units) - 1)
            return available_units[index]


class RoundRobinUnitScheduler(UnitScheduler):

    def find_next_unit_to_reserve(self, available_units: List["Unit"]) -> Optional["Unit"]:
        asignments_unscheduled_units = [] # TODO: run a GROUP BY query in the DB that would return list of tuples (assignment_id, ids_of_unscheduled_units), order by `assignment_id`
        available_units_by_id = {u.id: u for u in available_units}

        unscheduled_units_counts = set([
            len(auu[1])
            for auu in asignments_unscheduled_units
            if len(auu[1])
        ])
        if not unscheduled_units_counts:
            # Everything has already been scheduled
            return None

        target_units_count = min(unscheduled_units_counts)
        for (assignment_id, unscheduled_units_ids) in asignments_unscheduled_units:
            # Take the first assignemnt that has the taraget count of unscheduled units
            if len(unscheduled_units_ids) == target_units_count:
                unit_id = sorted(unscheduled_units_ids)[0]
                return available_units_by_id[unit_id]
