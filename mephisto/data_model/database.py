#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import sqlite3

from abc import ABC, abstractmethod
from typing import Mapping, Optional, Any
from mephisto.data_model.project import Project
from mephisto.data_model.task import Task, TaskRun
from mephisto.data_model.assignment import Assignment, Unit
from mephisto.data_model.requester import Requester
from mephisto.data_model.agent import Agent

# TODO investigate rate limiting against the db by caching locally where appropriate across the data model?
# TODO investigate cursors for DB queries as the project scales


class MephistoDBException(Exception):
    pass


class EntryAlreadyExistsException(MephistoDBException):
    pass


class EntryDoesNotExistException(MephistoDBException):
    pass


class MephistoDB(ABC):
    """
    Provides the interface for all queries that are necessary for the Mephisto
    architecture to run as expected. All other databases should implement
    these methods to be used as the database that backs Mephisto.

    By default, we use a LocalMesphistoDB located at `mephisto/data/database.db`
    """

    def __init__(self):
        self.init_tables()

    @staticmethod
    @abstractmethod
    def init_tables() -> None:
        """
        Initialize any tables that may be required to run this database. If this is an expensive
        operation, check to see if they already exist before trying to initialize
        """
        raise NotImplementedError()

    @abstractmethod
    def new_project(self, project_name: str) -> str:
        """
        Create a new project with the given project name. Raise EntryAlreadyExistsException if a project
        with this name has already been created.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return project's fields by the given project_id, raise EntryDoesNotExistException if no id exists
        in projects

        See Project for the expected returned mapping's fields
        """
        raise NotImplementedError()

    @abstractmethod
    def find_projects(
        self, project_id: Optional[str] = None, project_name: Optional[str] = None
    ) -> List[Project]:
        """
        Try to find any project that matches the above. When called with no arguments,
        return all projects.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_project(self, project_id: str, project_name: str) -> None:
        """
        Update the given project with the given parameters if possible, raise appropriate exception otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_task(
        self,
        task_name: str,
        task_type: str,
        project_id: Optional[str],
        parent_task_id: Optional[str],
    ) -> str:
        """
        Create a new task with the given task name. Raise EntryAlreadyExistsException if a task
        with this name has already been created.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return task's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        See Task for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def find_tasks(
        self,
        task_id: Optional[str] = None,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
    ) -> List[Task]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_task(
        self,
        task_id: str,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_task_run(self, task_id: str, requester_id: str, init_params: str) -> str:
        """
        Create a new task_run for the given task.

        Once a run is created, it should no longer be altered. The assignments and
        subassignments depend on the data set up within, as the launched task
        cannot be replaced and the requester can not be swapped mid-run.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_task_run(self, task_run_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return the given task_run's fields by task_run_id, raise EntryDoesNotExistException if no id exists
        in task_runs.

        See TaskRun for the expected fields to populate in the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def find_task_runs(
        self,
        task_run_id: Optional[str] = None,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
    ) -> List[TaskRun]:
        """
        Try to find any task_run that matches the above. When called with no arguments,
        return all task_runs.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_assignment(self, task_run_id: str) -> str:
        """
        Create a new assignment for the given task

        Assignments should not be edited or altered once created
        """
        raise NotImplementedError()

    @abstractmethod
    def get_assignment(self, task_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return assignment's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        See Assignment for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def find_assignments(self, task_run_id: Optional[str] = None) -> List[Assignment]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_unit(
        self, assignment_id: str, unit_index: int, pay_amount: float, provider_type: str
    ) -> str:
        """
        Create a new unit with the given index. Raises EntryAlreadyExistsException
        if there is already a unit for the given assignment with the given index.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_unit(self, unit_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return unit's fields by unit_id, raise EntryDoesNotExistException
        if no id exists in units

        See unit for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def find_units(
        self,
        assignment_id: Optional[str] = None,
        index: Optional[int] = None,
        agent_id: Optional[str] = None,
    ) -> List[Unit]:
        """
        Try to find any unit that matches the above. When called with no arguments,
        return all units.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_requester(self, requester_name: str, provider_type: str) -> str:
        """
        Create a new requester with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a requester with this name
        """
        # TODO ensure that provider type is a valid type
        raise NotImplemente4dError

    @abstractmethod
    def get_requester(self, requester_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return requester's fields by requester_id, raise EntryDoesNotExistException
        if no id exists in requesters

        See requester for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def find_requesters(
        self, requester_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Requester]:
        """
        Try to find any requester that matches the above. When called with no arguments,
        return all requesters.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_worker(self, worker_name: str, provider_type: str) -> str:
        """
        Create a new worker with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a worker with this name
        """
        # TODO ensure that provider type is a valid type
        raise NotImplemente4dError

    @abstractmethod
    def get_worker(self, worker_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return worker's fields by worker_id, raise EntryDoesNotExistException
        if no id exists in workers

        See worker for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def find_workers(self, provider_type: Optional[str] = None) -> List[Worker]:
        """
        Try to find any worker that matches the above. When called with no arguments,
        return all workers.
        """
        raise NotImplementedError()

    @abstractmethod
    def new_agent(
        self, worker_id: str, unit_id: str, task_type: str, provider_type: str
    ) -> str:
        """
        Create a new agent with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a agent with this name
        """
        # TODO ensure that provider type is a valid type
        raise NotImplementedError()

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Mapping[str, Any]]:
        """
        Return agent's fields by agent_id, raise EntryDoesNotExistException
        if no id exists in agents

        See Agent for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    @abstractmethod
    def update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def find_agents(
        self,
        status: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[int] = None,
    ) -> List[Agent]:
        """
        Try to find any agent that matches the above. When called with no arguments,
        return all agents.
        """
        raise NotImplementedError()
