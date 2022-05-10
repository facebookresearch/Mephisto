#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC
from prometheus_client import Gauge  # type: ignore
from collections import defaultdict
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.agent import Agent
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedABCMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.requester import Requester
from typing import Optional, Mapping, Dict, Any, Type, DefaultDict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.data_model.assignment import Assignment, InitializationData

import os

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)

SCREENING_UNIT_INDEX = -1
GOLD_UNIT_INDEX = -2
COMPENSATION_UNIT_INDEX = -3
INDEX_TO_TYPE_MAP: DefaultDict[int, str] = defaultdict(
    lambda: "standard",
    {
        0: "standard",
        SCREENING_UNIT_INDEX: "screening_unit",
        GOLD_UNIT_INDEX: "gold_unit",
        COMPENSATION_UNIT_INDEX: "compensation_unit",
    },
)

ACTIVE_UNIT_STATUSES = Gauge(
    "active_unit_statuses",
    "Tracking of all units current statuses",
    ["status", "unit_type"],
)
for status in AssignmentState.valid_unit():
    for unit_type in INDEX_TO_TYPE_MAP.values():
        ACTIVE_UNIT_STATUSES.labels(status=status, unit_type=unit_type)


class Unit(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.

    It should be extended for usage with a specific crowd provider
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct Unit and data model access via ...Unit(db, id) is "
                "now deprecated in favor of calling Unit.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_unit(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["unit_id"]
        self.assignment_id: str = row["assignment_id"]
        self.unit_index: int = row["unit_index"]
        self.pay_amount: float = row["pay_amount"]
        self.agent_id: Optional[str] = row["agent_id"]
        self.provider_type: str = row["provider_type"]
        self.db_status: str = row["status"]
        self.task_type: str = row["task_type"]
        self.task_id: str = row["task_id"]
        self.task_run_id: str = row["task_run_id"]
        self.sandbox: bool = row["sandbox"]
        self.requester_id: str = row["requester_id"]
        self.worker_id: str = row["worker_id"]

        # Deferred loading of related entities
        self.__task: Optional["Task"] = None
        self.__task_run: Optional["TaskRun"] = None
        self.__assignment: Optional["Assignment"] = None
        self.__requester: Optional["Requester"] = None
        self.__agent: Optional["Agent"] = None
        self.__worker: Optional["Worker"] = None

    def __new__(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ) -> "Unit":
        """
        The new method is overridden to be able to automatically generate
        the expected Unit class without needing to specifically find it
        for a given db_id. As such it is impossible to create a Unit
        as you will instead be returned the correct Unit class according to
        the crowdprovider associated with this Unit.
        """
        if cls == Unit:
            # We are trying to construct a Unit, find what type to use and
            # create that instead
            from mephisto.operations.registry import get_crowd_provider_from_type

            if row is None:
                row = db.get_unit(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(row["provider_type"]).UnitClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def get_crowd_provider_class(self) -> Type["CrowdProvider"]:
        """Get the CrowdProvider class that manages this Unit"""
        from mephisto.operations.registry import get_crowd_provider_from_type

        return get_crowd_provider_from_type(self.provider_type)

    def get_assignment_data(self) -> "InitializationData":
        """Return the specific assignment data for this assignment"""
        return self.get_assignment().get_assignment_data()

    def sync_status(self) -> None:
        """
        Ensure that the queried status from this unit and the db status
        are up to date
        """
        # TODO(#102) this will need to be run periodically/on crashes
        # to sync any lost state
        self.set_db_status(self.get_status())

    def get_db_status(self) -> str:
        """
        Return the status as currently stored in the database
        """
        if self.db_status in AssignmentState.final_unit():
            return self.db_status
        row = self.db.get_unit(self.db_id)
        assert row is not None, f"Unit {self.db_id} stopped existing in the db..."
        return row["status"]

    def set_db_status(self, status: str) -> None:
        """
        Set the status reflected in the database for this Unit
        """
        assert (
            status in AssignmentState.valid_unit()
        ), f"{status} not valid Assignment Status, not in {AssignmentState.valid_unit()}"
        if status == self.db_status:
            return
        logger.debug(f"Updating status for {self} from {self.db_status} to {status}")
        ACTIVE_UNIT_STATUSES.labels(
            status=self.db_status, unit_type=INDEX_TO_TYPE_MAP[self.unit_index]
        ).dec()
        ACTIVE_UNIT_STATUSES.labels(
            status=status, unit_type=INDEX_TO_TYPE_MAP[self.unit_index]
        ).inc()
        self.db_status = status
        self.db.update_unit(self.db_id, status=status)

    def _mark_agent_assignment(self) -> None:
        """Special helper to mark the transition from LAUNCHED to ASSIGNED"""
        assert (
            self.db_status == AssignmentState.LAUNCHED
        ), "can only mark LAUNCHED units"
        ACTIVE_UNIT_STATUSES.labels(
            status=AssignmentState.LAUNCHED,
            unit_type=INDEX_TO_TYPE_MAP[self.unit_index],
        ).dec()
        ACTIVE_UNIT_STATUSES.labels(
            status=AssignmentState.ASSIGNED,
            unit_type=INDEX_TO_TYPE_MAP[self.unit_index],
        ).inc()

    def get_assignment(self) -> "Assignment":
        """
        Return the assignment that this Unit is part of.
        """
        if self.__assignment is None:
            from mephisto.data_model.assignment import Assignment

            self.__assignment = Assignment.get(self.db, self.assignment_id)
        return self.__assignment

    def get_task_run(self) -> TaskRun:
        """
        Return the task run that this assignment is part of
        """
        if self.__task_run is None:
            if self.__assignment is not None:
                self.__task_run = self.__assignment.get_task_run()
            else:
                self.__task_run = TaskRun.get(self.db, self.task_run_id)
        return self.__task_run

    def get_task(self) -> Task:
        """
        Return the task that this assignment is part of
        """
        if self.__task is None:
            if self.__assignment is not None:
                self.__task = self.__assignment.get_task()
            elif self.__task_run is not None:
                self.__task = self.__task_run.get_task()
            else:
                self.__task = Task.get(self.db, self.task_id)
        return self.__task

    def get_requester(self) -> "Requester":
        """
        Return the requester who offered this Unit
        """
        if self.__requester is None:
            if self.__assignment is not None:
                self.__requester = self.__assignment.get_requester()
            elif self.__task_run is not None:
                self.__requester = self.__task_run.get_requester()
            else:
                self.__requester = Requester.get(self.db, self.requester_id)
        return self.__requester

    def clear_assigned_agent(self) -> None:
        """Clear the agent that is assigned to this unit"""
        logger.debug(f"Clearing assigned agent {self.agent_id} from {self}")
        self.db.clear_unit_agent_assignment(self.db_id)
        self.set_db_status(AssignmentState.LAUNCHED)
        self.get_task_run().clear_reservation(self)
        self.agent_id = None
        self.__agent = None

    def get_assigned_agent(self) -> Optional[Agent]:
        """
        Get the agent assigned to this Unit if there is one, else return None
        """
        # In these statuses, we know the agent isn't changing anymore, and thus will
        # not need to be re-queried
        if self.db_status in AssignmentState.final_unit():
            if self.agent_id is None:
                return None
            return Agent.get(self.db, self.agent_id)

        # Query the database to get the most up-to-date assignment, as this can
        # change after instantiation if the Unit status isn't final
        unit_copy = Unit.get(self.db, self.db_id)
        self.agent_id = unit_copy.agent_id
        if self.agent_id is not None:
            return Agent.get(self.db, self.agent_id)
        return None

    @staticmethod
    def _register_unit(
        db: "MephistoDB",
        assignment: "Assignment",
        index: int,
        pay_amount: float,
        provider_type: str,
    ) -> "Unit":
        """
        Create an entry for this unit in the database
        """
        db_id = db.new_unit(
            assignment.task_id,
            assignment.task_run_id,
            assignment.requester_id,
            assignment.db_id,
            index,
            pay_amount,
            provider_type,
            assignment.task_type,
            sandbox=assignment.sandbox,
        )
        unit = Unit.get(db, db_id)
        ACTIVE_UNIT_STATUSES.labels(
            status=AssignmentState.CREATED, unit_type=INDEX_TO_TYPE_MAP[index]
        ).inc()
        logger.debug(f"Registered new unit {unit} for {assignment}.")
        return unit

    def get_pay_amount(self) -> float:
        """
        Return the amount that this Unit is costing against the budget,
        calculating additional fees as relevant
        """
        return self.pay_amount

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id}, {self.db_status})"

    # Children classes may need to override the following

    def get_status(self) -> str:
        """
        Get the status of this unit, as determined by whether there's
        a worker working on it at the moment, and any other possible states. Should
        return one of UNIT_STATUSES

        Accurate status is crowd-provider dependent, and thus this method should be
        defined in the child class to ensure that the local record matches
        the ground truth in the provider
        """
        from mephisto.abstractions.blueprint import AgentState

        db_status = self.db_status

        # Expiration is a terminal state, and shouldn't be changed
        if db_status == AssignmentState.EXPIRED:
            return db_status

        computed_status = AssignmentState.LAUNCHED

        agent = self.get_assigned_agent()
        if agent is None:
            row = self.db.get_unit(self.db_id)
            computed_status = row["status"]
        else:
            agent_status = agent.get_status()
            if agent_status == AgentState.STATUS_NONE:
                computed_status = AssignmentState.LAUNCHED
            elif agent_status in [
                AgentState.STATUS_ACCEPTED,
                AgentState.STATUS_ONBOARDING,
                AgentState.STATUS_PARTNER_DISCONNECT,
                AgentState.STATUS_WAITING,
                AgentState.STATUS_IN_TASK,
            ]:
                computed_status = AssignmentState.ASSIGNED
            elif agent_status in [AgentState.STATUS_COMPLETED]:
                computed_status = AssignmentState.COMPLETED
            elif agent_status in [AgentState.STATUS_SOFT_REJECTED]:
                computed_status = AssignmentState.SOFT_REJECTED
            elif agent_status in [AgentState.STATUS_EXPIRED]:
                computed_status = AssignmentState.EXPIRED
            elif agent_status in [
                AgentState.STATUS_DISCONNECT,
                AgentState.STATUS_RETURNED,
                AgentState.STATUS_TIMEOUT,
            ]:
                # Still assigned, as we expect the task launcher to explicitly
                # update our status to expired or to remove the agent
                computed_status = AssignmentState.ASSIGNED
            elif agent_status == AgentState.STATUS_APPROVED:
                computed_status = AssignmentState.ACCEPTED
            elif agent_status == AgentState.STATUS_REJECTED:
                computed_status = AssignmentState.REJECTED

        if computed_status != db_status:
            self.set_db_status(computed_status)

        return computed_status

    # Children classes should implement the below methods

    def launch(self, task_url: str) -> None:
        """
        Make this Unit available on the crowdsourcing vendor. Depending on
        the task type, this could mean a number of different setup steps.

        Some crowd providers require setting up a configuration for the
        very first launch, and this method should call a helper to manage
        that step if necessary.
        """
        raise NotImplementedError()

    def expire(self) -> float:
        """
        Expire this unit, removing it from being workable on the vendor.
        Return the maximum time needed to wait before we know it's taken down.
        """
        raise NotImplementedError()

    def is_expired(self) -> bool:
        """Determine if this unit is expired as according to the vendor."""
        raise NotImplementedError()

    @staticmethod
    def new(
        db: "MephistoDB", assignment: "Assignment", index: int, pay_amount: float
    ) -> "Unit":
        """
        Create a Unit for the given assignment

        Implementation should return the result of _register_unit when sure the unit
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()
