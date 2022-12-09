#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import sqlite3
from prometheus_client import Histogram  # type: ignore

from abc import ABC, abstractmethod
from mephisto.utils.dirs import get_data_dir
from mephisto.operations.registry import (
    get_crowd_provider_from_type,
    get_valid_provider_types,
)
from typing import Mapping, Optional, Any, List, Dict
import enum
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.data_model.unit import Unit
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import Qualification, GrantedQualification


# TODO(#101) investigate cursors for DB queries as the project scales


class MephistoDBException(Exception):
    pass


class EntryAlreadyExistsException(MephistoDBException):
    pass


class EntryDoesNotExistException(MephistoDBException):
    pass


# Initialize histogram for database latency
DATABASE_LATENCY = Histogram(
    "database_latency_seconds", "Logging for db requests", ["method"]
)
# Need all the specific decorators b/c cascading is not allowed in decorators
# thanks to https://mail.python.org/pipermail/python-dev/2004-August/046711.html
NEW_PROJECT_LATENCY = DATABASE_LATENCY.labels(method="new_project")
GET_PROJECT_LATENCY = DATABASE_LATENCY.labels(method="get_project")
FIND_PROJECTS_LATENCY = DATABASE_LATENCY.labels(method="find_projects")
NEW_TASK_LATENCY = DATABASE_LATENCY.labels(method="new_task")
GET_TASK_LATENCY = DATABASE_LATENCY.labels(method="get_task")
FIND_TASKS_LATENCY = DATABASE_LATENCY.labels(method="find_tasks")
UPDATE_TASK_LATENCY = DATABASE_LATENCY.labels(method="update_task")
NEW_TASK_RUN_LATENCY = DATABASE_LATENCY.labels(method="new_task_run")
GET_TASK_RUN_LATENCY = DATABASE_LATENCY.labels(method="get_task_run")
FIND_TASK_RUNS_LATENCY = DATABASE_LATENCY.labels(method="find_task_runs")
UPDATE_TASK_RUN_LATENCY = DATABASE_LATENCY.labels(method="update_task_run")
NEW_ASSIGNMENT_LATENCY = DATABASE_LATENCY.labels(method="new_assignment")
GET_ASSIGNMENT_LATENCY = DATABASE_LATENCY.labels(method="get_assignment")
FIND_ASSIGNMENTS_LATENCY = DATABASE_LATENCY.labels(method="find_assignments")
NEW_UNIT_LATENCY = DATABASE_LATENCY.labels(method="new_unit")
GET_UNIT_LATENCY = DATABASE_LATENCY.labels(method="get_unit")
FIND_UNITS_LATENCY = DATABASE_LATENCY.labels(method="find_units")
UPDATE_UNIT_LATENCY = DATABASE_LATENCY.labels(method="update_unit")
NEW_REQUESTER_LATENCY = DATABASE_LATENCY.labels(method="new_requester")
GET_REQUESTER_LATENCY = DATABASE_LATENCY.labels(method="get_requester")
FIND_REQUESTERS_LATENCY = DATABASE_LATENCY.labels(method="find_requesters")
NEW_WORKER_LATENCY = DATABASE_LATENCY.labels(method="new_worker")
GET_WORKER_LATENCY = DATABASE_LATENCY.labels(method="get_worker")
FIND_WORKERS_LATENCY = DATABASE_LATENCY.labels(method="find_workers")
NEW_AGENT_LATENCY = DATABASE_LATENCY.labels(method="new_agent")
GET_AGENT_LATENCY = DATABASE_LATENCY.labels(method="get_agent")
FIND_AGENTS_LATENCY = DATABASE_LATENCY.labels(method="find_agents")
UPDATE_AGENT_LATENCY = DATABASE_LATENCY.labels(method="update_agent")
CLEAR_UNIT_AGENT_ASSIGNMENT_LATENCY = DATABASE_LATENCY.labels(
    method="clear_unit_agent_assignment"
)
NEW_ONBOARDING_AGENT_LATENCY = DATABASE_LATENCY.labels(method="new_onboarding_agent")
GET_ONBOARDING_AGENT_LATENCY = DATABASE_LATENCY.labels(method="get_onboarding_agent")
FIND_ONBOARDING_AGENTS_LATENCY = DATABASE_LATENCY.labels(
    method="find_onboarding_agents"
)
UPDATE_ONBOARDING_AGENT_LATENCY = DATABASE_LATENCY.labels(
    method="update_onboarding_agent"
)
MAKE_QUALIFICATION_LATENCY = DATABASE_LATENCY.labels(method="make_qualification")
GET_QUALIFICATION_LATENCY = DATABASE_LATENCY.labels(method="get_qualification")
FIND_QUALIFICATIONS_LATENCY = DATABASE_LATENCY.labels(method="find_qualifications")
DELETE_QUALIFICATION_LATENCY = DATABASE_LATENCY.labels(method="delete_qualification")
GRANT_QUALIFICATION_LATENCY = DATABASE_LATENCY.labels(method="grant_qualification")
CHECK_GRANTED_QUALIFICATIONS_LATENCY = DATABASE_LATENCY.labels(
    method="check_granted_qualifications"
)
GET_GRANTED_QUALIFICATION_LATENCY = DATABASE_LATENCY.labels(
    method="get_granted_qualification"
)
REVOKE_QUALIFICATION_LATENCY = DATABASE_LATENCY.labels(method="revoke_qualification")


class MephistoDB(ABC):
    """
    Provides the interface for all queries that are necessary for the Mephisto
    architecture to run as expected. All other databases should implement
    these methods to be used as the database that backs Mephisto.

    By default, we use a LocalMesphistoDB located at `mephisto/data/database.db`
    """

    def __init__(self, database_path=None):
        """Ensure the database is set up and ready to handle data"""
        if database_path is None:
            database_path = os.path.join(get_data_dir(), "database.db")
        self.db_path = database_path
        self.db_root = os.path.dirname(self.db_path)
        self.init_tables()
        self.__provider_datastores: Dict[str, Any] = {}

    def get_db_path_for_provider(self, provider_type) -> str:
        """Get the path to store data for a specific provider in"""
        database_root = os.path.dirname(self.db_path)
        provider_root = os.path.join(database_root, provider_type)
        os.makedirs(provider_root, exist_ok=True)
        return provider_root

    def has_datastore_for_provider(self, provider_type: str) -> bool:
        """Determine if a datastore has been registered for the given provider"""
        return provider_type in self.__provider_datastores

    def get_datastore_for_provider(self, provider_type: str) -> Any:
        """Get the provider datastore registered with this db"""
        if provider_type not in self.__provider_datastores:
            # Register this provider for usage now
            ProviderClass = get_crowd_provider_from_type(provider_type)
            provider = ProviderClass(self)
        return self.__provider_datastores.get(provider_type)

    def set_datastore_for_provider(self, provider_type: str, datastore: Any) -> None:
        """Set the provider datastore registered with this db"""
        self.__provider_datastores[provider_type] = datastore

    def optimized_load(
        self,
        target_cls,
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
    ):
        """
        Load the given class in an optimized fashion, if this DB has a more
        efficient way of storing and managing the data
        """
        return None

    def cache_result(self, target_cls, value) -> None:
        """Opportunity to store the result class from a load"""
        return None

    @abstractmethod
    def shutdown(self) -> None:
        """Do whatever is required to close this database's resources"""
        raise NotImplementedError()

    @abstractmethod
    def init_tables(self) -> None:
        """
        Initialize any tables that may be required to run this database. If this is an expensive
        operation, check to see if they already exist before trying to initialize
        """
        raise NotImplementedError()

    @abstractmethod
    def _new_project(self, project_name: str) -> str:
        """new_project implementation"""
        raise NotImplementedError()

    @NEW_PROJECT_LATENCY.time()
    def new_project(self, project_name: str) -> str:
        """
        Create a new project with the given project name. Raise EntryAlreadyExistsException if a project
        with this name has already been created.

        Project names are permanent, as changing directories later is painful.
        """
        return self._new_project(project_name=project_name)

    @abstractmethod
    def _get_project(self, project_id: str) -> Mapping[str, Any]:
        """get_project implementation"""
        raise NotImplementedError()

    @GET_PROJECT_LATENCY.time()
    def get_project(self, project_id: str) -> Mapping[str, Any]:
        """
        Return project's fields by the given project_id, raise EntryDoesNotExistException if no id exists
        in projects

        See Project for the expected returned mapping's fields
        """
        return self._get_project(project_id=project_id)

    @abstractmethod
    def _find_projects(self, project_name: Optional[str] = None) -> List[Project]:
        """find_projects implementation"""
        raise NotImplementedError()

    @FIND_PROJECTS_LATENCY.time()
    def find_projects(self, project_name: Optional[str] = None) -> List[Project]:
        """
        Try to find any project that matches the above. When called with no arguments,
        return all projects.
        """
        return self._find_projects(project_name=project_name)

    @abstractmethod
    def _new_task(
        self,
        task_name: str,
        task_type: str,
        project_id: Optional[str] = None,
    ) -> str:
        """new_task implementation"""
        raise NotImplementedError()

    @NEW_TASK_LATENCY.time()
    def new_task(
        self,
        task_name: str,
        task_type: str,
        project_id: Optional[str] = None,
    ) -> str:
        """
        Create a new task with the given task name. Raise EntryAlreadyExistsException if a task
        with this name has already been created.
        """
        return self._new_task(
            task_name=task_name, task_type=task_type, project_id=project_id
        )

    @abstractmethod
    def _get_task(self, task_id: str) -> Mapping[str, Any]:
        """get_task implementation"""
        raise NotImplementedError()

    @GET_TASK_LATENCY.time()
    def get_task(self, task_id: str) -> Mapping[str, Any]:
        """
        Return task's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        See Task for the expected fields for the returned mapping
        """
        return self._get_task(task_id=task_id)

    @abstractmethod
    def _find_tasks(
        self,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Task]:
        """find_tasks implementation"""
        raise NotImplementedError()

    @FIND_TASKS_LATENCY.time()
    def find_tasks(
        self,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Task]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        return self._find_tasks(task_name=task_name, project_id=project_id)

    @abstractmethod
    def _update_task(
        self,
        task_id: str,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """update_task implementation"""
        raise NotImplementedError()

    @UPDATE_TASK_LATENCY.time()
    def update_task(
        self,
        task_id: str,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.

        Should only be runable if no runs have been created for this task
        """
        self._update_task(task_id=task_id, task_name=task_name, project_id=project_id)

    @abstractmethod
    def _new_task_run(
        self,
        task_id: str,
        requester_id: str,
        init_params: str,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """new_task_run implementation"""
        raise NotImplementedError()

    @NEW_TASK_RUN_LATENCY.time()
    def new_task_run(
        self,
        task_id: str,
        requester_id: str,
        init_params: str,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """
        Create a new task_run for the given task.

        Once a run is created, it should no longer be altered. The assignments and
        subassignments depend on the data set up within, as the launched task
        cannot be replaced and the requester can not be swapped mid-run.
        """
        return self._new_task_run(
            task_id=task_id,
            requester_id=requester_id,
            init_params=init_params,
            provider_type=provider_type,
            task_type=task_type,
            sandbox=sandbox,
        )

    @abstractmethod
    def _get_task_run(self, task_run_id: str) -> Mapping[str, Any]:
        """get_task_run implementation"""
        raise NotImplementedError()

    @GET_TASK_RUN_LATENCY.time()
    def get_task_run(self, task_run_id: str) -> Mapping[str, Any]:
        """
        Return the given task_run's fields by task_run_id, raise EntryDoesNotExistException if no id exists
        in task_runs.

        See TaskRun for the expected fields to populate in the returned mapping
        """
        return self._get_task_run(task_run_id=task_run_id)

    @abstractmethod
    def _find_task_runs(
        self,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        is_completed: Optional[bool] = None,
    ) -> List[TaskRun]:
        """find_task_runs implementation"""
        raise NotImplementedError()

    @FIND_TASK_RUNS_LATENCY.time()
    def find_task_runs(
        self,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        is_completed: Optional[bool] = None,
    ) -> List[TaskRun]:
        """
        Try to find any task_run that matches the above. When called with no arguments,
        return all task_runs.
        """
        return self._find_task_runs(
            task_id=task_id, requester_id=requester_id, is_completed=is_completed
        )

    @abstractmethod
    def _update_task_run(self, task_run_id: str, is_completed: bool):
        """update_task_run implementation"""
        raise NotImplementedError()

    @UPDATE_TASK_RUN_LATENCY.time()
    def update_task_run(self, task_run_id: str, is_completed: bool):
        """
        Update a task run. At the moment, can only update completion status
        """
        return self._update_task_run(task_run_id=task_run_id, is_completed=is_completed)

    @abstractmethod
    def _new_assignment(
        self,
        task_id: str,
        task_run_id: str,
        requester_id: str,
        task_type: str,
        provider_type: str,
        sandbox: bool = True,
    ) -> str:
        """new_assignment implementation"""
        raise NotImplementedError()

    @NEW_ASSIGNMENT_LATENCY.time()
    def new_assignment(
        self,
        task_id: str,
        task_run_id: str,
        requester_id: str,
        task_type: str,
        provider_type: str,
        sandbox: bool = True,
    ) -> str:
        """
        Create a new assignment for the given task

        Assignments should not be edited or altered once created
        """
        return self._new_assignment(
            task_id=task_id,
            task_run_id=task_run_id,
            requester_id=requester_id,
            task_type=task_type,
            provider_type=provider_type,
            sandbox=sandbox,
        )

    @abstractmethod
    def _get_assignment(self, assignment_id: str) -> Mapping[str, Any]:
        """get_assignment implementation"""
        raise NotImplementedError()

    @GET_ASSIGNMENT_LATENCY.time()
    def get_assignment(self, assignment_id: str) -> Mapping[str, Any]:
        """
        Return assignment's fields by assignment_id, raise EntryDoesNotExistException if
        no id exists in tasks

        See Assignment for the expected fields for the returned mapping
        """
        return self._get_assignment(assignment_id=assignment_id)

    @abstractmethod
    def _find_assignments(
        self,
        task_run_id: Optional[str] = None,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[str] = None,
        sandbox: Optional[bool] = None,
    ) -> List[Assignment]:
        """find_assignments implementation"""
        raise NotImplementedError()

    @FIND_ASSIGNMENTS_LATENCY.time()
    def find_assignments(
        self,
        task_run_id: Optional[str] = None,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[str] = None,
        sandbox: Optional[bool] = None,
    ) -> List[Assignment]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        return self._find_assignments(
            task_run_id=task_run_id,
            task_id=task_id,
            requester_id=requester_id,
            task_type=task_type,
            provider_type=provider_type,
            sandbox=sandbox,
        )

    @abstractmethod
    def _new_unit(
        self,
        task_id: str,
        task_run_id: str,
        requester_id: str,
        assignment_id: str,
        unit_index: int,
        pay_amount: float,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """new_unit implementation"""
        raise NotImplementedError()

    @NEW_UNIT_LATENCY.time()
    def new_unit(
        self,
        task_id: str,
        task_run_id: str,
        requester_id: str,
        assignment_id: str,
        unit_index: int,
        pay_amount: float,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """
        Create a new unit with the given index. Raises EntryAlreadyExistsException
        if there is already a unit for the given assignment with the given index.
        """
        return self._new_unit(
            task_id=task_id,
            task_run_id=task_run_id,
            requester_id=requester_id,
            assignment_id=assignment_id,
            unit_index=unit_index,
            pay_amount=pay_amount,
            provider_type=provider_type,
            task_type=task_type,
            sandbox=sandbox,
        )

    @abstractmethod
    def _get_unit(self, unit_id: str) -> Mapping[str, Any]:
        """get_unit implementation"""
        raise NotImplementedError()

    @GET_UNIT_LATENCY.time()
    def get_unit(self, unit_id: str) -> Mapping[str, Any]:
        """
        Return unit's fields by unit_id, raise EntryDoesNotExistException
        if no id exists in units

        See unit for the expected fields for the returned mapping
        """
        return self._get_unit(unit_id=unit_id)

    @abstractmethod
    def _find_units(
        self,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        unit_index: Optional[int] = None,
        provider_type: Optional[str] = None,
        task_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        sandbox: Optional[bool] = None,
        status: Optional[str] = None,
    ) -> List[Unit]:
        """find_units implementation"""
        raise NotImplementedError()

    @FIND_UNITS_LATENCY.time()
    def find_units(
        self,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        unit_index: Optional[int] = None,
        provider_type: Optional[str] = None,
        task_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        sandbox: Optional[bool] = None,
        status: Optional[str] = None,
    ) -> List[Unit]:
        """
        Try to find any unit that matches the above. When called with no arguments,
        return all units.
        """
        return self._find_units(
            task_id=task_id,
            task_run_id=task_run_id,
            requester_id=requester_id,
            assignment_id=assignment_id,
            unit_index=unit_index,
            provider_type=provider_type,
            task_type=task_type,
            agent_id=agent_id,
            worker_id=worker_id,
            sandbox=sandbox,
            status=status,
        )

    @abstractmethod
    def _clear_unit_agent_assignment(self, unit_id: str) -> None:
        """clear_unit_agent_assignment implementation"""
        raise NotImplementedError()

    @CLEAR_UNIT_AGENT_ASSIGNMENT_LATENCY.time()
    def clear_unit_agent_assignment(self, unit_id: str) -> None:
        """
        Update the given unit by removing the agent that is assigned to it, thus updating
        the status to assignable.
        """
        return self._clear_unit_agent_assignment(unit_id=unit_id)

    @abstractmethod
    def _update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """update_unit implementation"""
        raise NotImplementedError()

    @UPDATE_UNIT_LATENCY.time()
    def update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        return self._update_unit(unit_id=unit_id, status=status)

    @abstractmethod
    def _new_requester(self, requester_name: str, provider_type: str) -> str:
        """new_requester implementation"""
        raise NotImplementedError()

    @NEW_REQUESTER_LATENCY.time()
    def new_requester(self, requester_name: str, provider_type: str) -> str:
        """
        Create a new requester with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a requester with this name
        """
        return self._new_requester(
            requester_name=requester_name, provider_type=provider_type
        )

    @abstractmethod
    def _get_requester(self, requester_id: str) -> Mapping[str, Any]:
        """get_requester implementation"""
        raise NotImplementedError()

    @GET_REQUESTER_LATENCY.time()
    def get_requester(self, requester_id: str) -> Mapping[str, Any]:
        """
        Return requester's fields by requester_id, raise EntryDoesNotExistException
        if no id exists in requesters

        See requester for the expected fields for the returned mapping
        """
        return self._get_requester(requester_id=requester_id)

    @abstractmethod
    def _find_requesters(
        self, requester_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Requester]:
        """find_requesters implementation"""
        raise NotImplementedError()

    @FIND_REQUESTERS_LATENCY.time()
    def find_requesters(
        self, requester_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Requester]:
        """
        Try to find any requester that matches the above. When called with no arguments,
        return all requesters.
        """
        return self._find_requesters(
            requester_name=requester_name, provider_type=provider_type
        )

    @abstractmethod
    def _new_worker(self, worker_name: str, provider_type: str) -> str:
        """new_worker implementation"""
        raise NotImplementedError()

    @NEW_WORKER_LATENCY.time()
    def new_worker(self, worker_name: str, provider_type: str) -> str:
        """
        Create a new worker with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a worker with this name

        worker_name should be the unique identifier by which the crowd provider
        is using to keep track of this worker
        """
        return self._new_worker(worker_name=worker_name, provider_type=provider_type)

    @abstractmethod
    def _get_worker(self, worker_id: str) -> Mapping[str, Any]:
        """get_worker implementation"""
        raise NotImplementedError()

    @GET_WORKER_LATENCY.time()
    def get_worker(self, worker_id: str) -> Mapping[str, Any]:
        """
        Return worker's fields by worker_id, raise EntryDoesNotExistException
        if no id exists in workers

        See worker for the expected fields for the returned mapping
        """
        return self._get_worker(worker_id=worker_id)

    @abstractmethod
    def _find_workers(
        self, worker_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Worker]:
        """find_workers implementation"""
        raise NotImplementedError()

    @FIND_WORKERS_LATENCY.time()
    def find_workers(
        self, worker_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Worker]:
        """
        Try to find any worker that matches the above. When called with no arguments,
        return all workers.
        """
        return self._find_workers(worker_name=worker_name, provider_type=provider_type)

    @abstractmethod
    def _new_agent(
        self,
        worker_id: str,
        unit_id: str,
        task_id: str,
        task_run_id: str,
        assignment_id: str,
        task_type: str,
        provider_type: str,
    ) -> str:
        """new_agent implementation"""
        raise NotImplementedError()

    @NEW_AGENT_LATENCY.time()
    def new_agent(
        self,
        worker_id: str,
        unit_id: str,
        task_id: str,
        task_run_id: str,
        assignment_id: str,
        task_type: str,
        provider_type: str,
    ) -> str:
        """
        Create a new agent for the given worker id to assign to the given unit
        Raises EntryAlreadyExistsException

        Should update the unit's status to ASSIGNED and the assigned agent to
        this one.
        """
        return self._new_agent(
            worker_id=worker_id,
            unit_id=unit_id,
            task_id=task_id,
            task_run_id=task_run_id,
            assignment_id=assignment_id,
            task_type=task_type,
            provider_type=provider_type,
        )

    @abstractmethod
    def _get_agent(self, agent_id: str) -> Mapping[str, Any]:
        """get_agent implementation"""
        raise NotImplementedError()

    @GET_AGENT_LATENCY.time()
    def get_agent(self, agent_id: str) -> Mapping[str, Any]:
        """
        Return agent's fields by agent_id, raise EntryDoesNotExistException
        if no id exists in agents

        See Agent for the expected fields for the returned mapping
        """
        return self._get_agent(agent_id=agent_id)

    @abstractmethod
    def _update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """update_agent implementation"""
        raise NotImplementedError()

    @UPDATE_AGENT_LATENCY.time()
    def update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        return self._update_agent(agent_id=agent_id, status=status)

    @abstractmethod
    def _find_agents(
        self,
        status: Optional[str] = None,
        unit_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[str] = None,
    ) -> List[Agent]:
        """find_agents implementation"""
        raise NotImplementedError()

    @FIND_AGENTS_LATENCY.time()
    def find_agents(
        self,
        status: Optional[str] = None,
        unit_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[str] = None,
    ) -> List[Agent]:
        """
        Try to find any agent that matches the above. When called with no arguments,
        return all agents.
        """
        return self._find_agents(
            status=status,
            unit_id=unit_id,
            worker_id=worker_id,
            task_id=task_id,
            task_run_id=task_run_id,
            assignment_id=assignment_id,
            task_type=task_type,
            provider_type=provider_type,
        )

    @abstractmethod
    def _new_onboarding_agent(
        self, worker_id: str, task_id: str, task_run_id: str, task_type: str
    ) -> str:
        """new_onboarding_agent implementation"""
        raise NotImplementedError()

    @NEW_ONBOARDING_AGENT_LATENCY.time()
    def new_onboarding_agent(
        self, worker_id: str, task_id: str, task_run_id: str, task_type: str
    ) -> str:
        """
        Create a new agent for the given worker id to assign to the given unit
        Raises EntryAlreadyExistsException

        Should update the unit's status to ASSIGNED and the assigned agent to
        this one.
        """
        return self._new_onboarding_agent(
            worker_id=worker_id,
            task_id=task_id,
            task_run_id=task_run_id,
            task_type=task_type,
        )

    @abstractmethod
    def _get_onboarding_agent(self, onboarding_agent_id: str) -> Mapping[str, Any]:
        """get_onboarding_agent implementation"""
        raise NotImplementedError()

    @GET_ONBOARDING_AGENT_LATENCY.time()
    def get_onboarding_agent(self, onboarding_agent_id: str) -> Mapping[str, Any]:
        """
        Return onboarding agent's fields by onboarding_agent_id, raise
        EntryDoesNotExistException if no id exists in onboarding_agents

        See OnboardingAgent for the expected fields for the returned mapping
        """
        return self._get_onboarding_agent(onboarding_agent_id=onboarding_agent_id)

    @abstractmethod
    def _update_onboarding_agent(
        self, onboarding_agent_id: str, status: Optional[str] = None
    ) -> None:
        """update_onboarding_agent implementation"""
        raise NotImplementedError()

    @UPDATE_ONBOARDING_AGENT_LATENCY.time()
    def update_onboarding_agent(
        self, onboarding_agent_id: str, status: Optional[str] = None
    ) -> None:
        """
        Update the given onboarding agent with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        return self._update_onboarding_agent(
            onboarding_agent_id=onboarding_agent_id, status=status
        )

    @abstractmethod
    def _find_onboarding_agents(
        self,
        status: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[OnboardingAgent]:
        """find_onboarding_agents implementation"""
        raise NotImplementedError()

    @FIND_ONBOARDING_AGENTS_LATENCY.time()
    def find_onboarding_agents(
        self,
        status: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[OnboardingAgent]:
        """
        Try to find any onboarding agent that matches the above. When called with no arguments,
        return all onboarding agents.
        """
        return self._find_onboarding_agents(
            status=status,
            worker_id=worker_id,
            task_id=task_id,
            task_run_id=task_run_id,
            task_type=task_type,
        )

    @abstractmethod
    def _make_qualification(self, qualification_name: str) -> str:
        """make_qualification implementation"""
        raise NotImplementedError()

    @MAKE_QUALIFICATION_LATENCY.time()
    def make_qualification(self, qualification_name: str) -> str:
        """
        Make a new qualification, throws an error if a qualification by the given name
        already exists. Return the id for the qualification.
        """
        return self._make_qualification(qualification_name=qualification_name)

    @abstractmethod
    def _find_qualifications(
        self, qualification_name: Optional[str] = None
    ) -> List[Qualification]:
        """find_qualifications implementation"""
        raise NotImplementedError()

    @FIND_QUALIFICATIONS_LATENCY.time()
    def find_qualifications(
        self, qualification_name: Optional[str] = None
    ) -> List[Qualification]:
        """
        Find a qualification. If no name is supplied, returns all qualifications.
        """
        return self._find_qualifications(qualification_name=qualification_name)

    @abstractmethod
    def _get_qualification(self, qualification_id: str) -> Mapping[str, Any]:
        """get_qualification implementation"""
        raise NotImplementedError()

    @GET_QUALIFICATION_LATENCY.time()
    def get_qualification(self, qualification_id: str) -> Mapping[str, Any]:
        """
        Return qualification's fields by qualification_id, raise
        EntryDoesNotExistException if no id exists in qualifications

        See Qualification for the expected fields for the returned mapping
        """
        return self._get_qualification(qualification_id=qualification_id)

    @abstractmethod
    def _delete_qualification(self, qualification_name: str) -> None:
        """
        Remove this qualification from all workers that have it, then delete the qualification
        """
        raise NotImplementedError()

    @DELETE_QUALIFICATION_LATENCY.time()
    def delete_qualification(self, qualification_name: str) -> None:
        """
        Remove this qualification from all workers that have it, then delete the qualification
        """
        self._delete_qualification(qualification_name)
        for crowd_provider_name in get_valid_provider_types():
            ProviderClass = get_crowd_provider_from_type(crowd_provider_name)
            provider = ProviderClass(self)
            provider.cleanup_qualification(qualification_name)

    @abstractmethod
    def _grant_qualification(
        self, qualification_id: str, worker_id: str, value: int = 1
    ) -> None:
        """grant_qualification implementation"""
        raise NotImplementedError()

    @GRANT_QUALIFICATION_LATENCY.time()
    def grant_qualification(
        self, qualification_id: str, worker_id: str, value: int = 1
    ) -> None:
        """
        Grant a worker the given qualification. Update the qualification value if it
        already exists
        """
        return self._grant_qualification(
            qualification_id=qualification_id, worker_id=worker_id, value=value
        )

    @abstractmethod
    def _check_granted_qualifications(
        self,
        qualification_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        value: Optional[int] = None,
    ) -> List[GrantedQualification]:
        """check_granted_qualifications implementation"""
        raise NotImplementedError()

    @CHECK_GRANTED_QUALIFICATIONS_LATENCY.time()
    def check_granted_qualifications(
        self,
        qualification_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        value: Optional[int] = None,
    ) -> List[GrantedQualification]:
        """
        Find granted qualifications that match the given specifications
        """
        return self._check_granted_qualifications(
            qualification_id=qualification_id, worker_id=worker_id, value=value
        )

    @abstractmethod
    def _get_granted_qualification(
        self, qualification_id: str, worker_id: str
    ) -> Mapping[str, Any]:
        """get_granted_qualification implementation"""
        raise NotImplementedError()

    @GET_GRANTED_QUALIFICATION_LATENCY.time()
    def get_granted_qualification(
        self, qualification_id: str, worker_id: str
    ) -> Mapping[str, Any]:
        """
        Return the granted qualification in the database between the given
        worker and qualification id

        See GrantedQualification for the expected fields for the returned mapping
        """
        return self._get_granted_qualification(
            qualification_id=qualification_id, worker_id=worker_id
        )

    @abstractmethod
    def _revoke_qualification(self, qualification_id: str, worker_id: str) -> None:
        """revoke_qualification implementation"""
        raise NotImplementedError()

    @REVOKE_QUALIFICATION_LATENCY.time()
    def revoke_qualification(self, qualification_id: str, worker_id: str) -> None:
        """
        Remove the given qualification from the given worker
        """
        return self._revoke_qualification(
            qualification_id=qualification_id, worker_id=worker_id
        )

    # File/blob manipulation methods

    @abstractmethod
    def write_dict(self, path_key: str, target_dict: Dict[str, Any]):
        """Write an object to the given key"""
        raise NotImplementedError()

    @abstractmethod
    def read_dict(self, path_key: str) -> Dict[str, Any]:
        """Return the dict loaded from the given path key"""
        raise NotImplementedError()

    @abstractmethod
    def write_text(self, path_key: str, data_string: str):
        """Write the given text to the given key"""
        raise NotImplementedError()

    @abstractmethod
    def read_text(self, path_key: str) -> str:
        """Get text data stored at the given key"""
        raise NotImplementedError()

    @abstractmethod
    def key_exists(self, path_key: str) -> bool:
        """See if the given path refers to a known file"""
        raise NotImplementedError()
