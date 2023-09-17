from abc import ABC, abstractmethod
from mephisto.data_model.task_run import TaskRun
from random import shuffle
from mephisto.data_model.constants.assignment_state import AssignmentState


class UnitScheduler(ABC):
    def __init__(self, task_run: "TaskRun", prefer_assigned_assignments: bool):
        self.task_run = task_run
        self.prefer_assigned_assignments = prefer_assigned_assignments

    def reserve_unit(self, available_units):
        """
        This method wraps the internal strategy.

        If 'prefer_assigned_assignments' is False, this method behaves exactly
        like the internal strategy.

        If 'prefer_assigned_assignments' is True, the scheduler prefers
        assignments with assigned units over unassigned assignments. This is
        usefull when dealing with concurrent assignments.
        """
        if not self.prefer_assigned_assignments:
            return self.reserve_unit(available_units)
        else:
            assignments = self.task_run.get_assignments()

            def hasAssignedUnit(assignment):
                """
                Returns if a given assignment has assigned units. Note that this
                is different from 'assignemt.get_status() == assigned' as the
                get_status() would return launched if the assignment has any
                unit that is launched but not assigned.
                """
                units = assignment.get_units()
                statuses = set(unit.get_status() for unit in units)
                return any([s == AssignmentState.ASSIGNED for s in statuses])

            ids_of_assigned_assignments = [
                assignment.db_id for assignment in assignments if hasAssignedUnit(assignment)
            ]
            units_in_assigned_assignments = list(
                filter(
                    lambda unit: unit.assignment_id in ids_of_assigned_assignments, available_units
                )
            )
            other_units = list(
                filter(
                    lambda unit: (not (unit.assignment_id in ids_of_assigned_assignments)),
                    available_units,
                )
            )

            res = self._reserve_unit(units_in_assigned_assignments)
            if res != None:
                return res
            else:
                return self._reserve_unit(other_units)

    @abstractmethod
    def _reserve_unit(self, available_units):
        """
        Implementations of this method should choose one of 'available_units'
        according to their scheduling strategy, reserve it in the task run and return it.
        If there are no available_units left or none of them can succesfully be reserved
        this method returns 'None'.
        """


class FIFOUnitScheduler(UnitScheduler):
    def _reserve_unit(self, available_units):
        reserved_unit = None

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop(0)
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit


class LIFOUnitScheduler(UnitScheduler):
    def _reserve_unit(self, available_units):
        reserved_unit = None

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop()
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit


class RandomUnitScheduler(UnitScheduler):
    def _reserve_unit(self, available_units):
        reserved_unit = None
        shuffle(available_units)

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop()
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit
