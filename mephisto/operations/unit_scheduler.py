from abc import ABC, abstractmethod
from mephisto.data_model.task_run import TaskRun
from random import shuffle

class UnitScheduler(ABC):
    def __init__(self, task_run: "TaskRun"):
        self.task_run = task_run

@abstractmethod
def reserve_unit(self, available_units):
    """
    Implementations of this method should choose one of 'available_units'
    according to their scheduling strategy, reserve it in the task run and return it.
    If there are no available_units left or none of them can succesfully be reserved
    this method returns 'None'.
    """
    pass

class FIFOUnitScheduler(UnitScheduler):
    def reserve_unit(self, available_units):
        reserved_unit = None

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop(0)
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit

class LIFOUnitScheduler(UnitScheduler):
    def reserve_unit(self, available_units):
        reserved_unit = None

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop()
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit


class RandomUnitScheduler(UnitScheduler):
    def reserve_unit(self, available_units):
        reserved_unit = None
        shuffle(available_units)

        while len(available_units) > 0 and reserved_unit is None:
            unit = available_units.pop()
            reserved_unit = self.task_run.reserve_unit(unit)

        return reserved_unit