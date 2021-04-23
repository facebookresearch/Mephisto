#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from typing import Mapping, Optional, Any, List, Dict
from mephisto.operations.utils import get_data_dir
from mephisto.operations.registry import get_valid_provider_types
from mephisto.data_model.agent import Agent, AgentState, OnboardingAgent
from mephisto.data_model.unit import Unit
from mephisto.data_model.assignment import Assignment, AssignmentState
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import Qualification, GrantedQualification

import sqlite3
from sqlite3 import Connection, Cursor
import threading
# We should be using WeakValueDictionary rather than a full dict once
# we're better able to trade-off between memory and space.
# from weakref import WeakValueDictionary

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)

# Note: This class could be a generic factory around any MephistoDB, converting
# the system to a singleton implementation. It requires all of the data being
# updated locally though, so binding to LocalMephistoDB makes sense for now.
class MephistoSingletonDB(LocalMephistoDB):
    """
    Class that creates a singleton storage for all accessed data.

    Tries to keep the data usage down with weak references, but it's
    still subject to memory leaks.

    This is a tradeoff to have more speed for not making db queries from disk
    """

    # All classes cached by this DB, in order of expected references
    _cached_classes = [
        Agent,
        Unit,
        Assignment,
        Worker,
        OnboardingAgent,
        Qualification,
        TaskRun,
        Task,
        Project,
        Requester,
    ]

    def __init__(self, database_path=None):
        super().__init__(database_path=database_path)

        # Create singleton dictionaries for entries
        self._singleton_cache = {k: dict() for k in self._cached_classes}

    def shutdown(self) -> None:
        """Close all open connections"""
        with self.table_access_condition:
            curr_thread = threading.get_ident()
            self.conn[curr_thread].close()
            del self.conn[curr_thread]

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
        for stored_class in self._cached_classes:
            if issubclass(target_cls, stored_class):
                return self._singleton_cache[stored_class].get(db_id)
        return None

    def cache_result(self, target_cls, value) -> None:
        """Store the result of a load for caching reasons"""
        for stored_class in self._cached_classes:
            if issubclass(target_cls, stored_class):
                self._singleton_cache[stored_class][value.db_id] = value
                break
        return None

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
        Wrapper around the new_agent call that finds and updates the unit locally
        too, as this isn't guaranteed otherwise but is an important part of the singleton
        """
        agent_id = super().new_agent(
            worker_id,
            unit_id,
            task_id,
            task_run_id,
            assignment_id,
            task_type,
            provider_type,
        )
        agent = Agent(self, agent_id)
        unit = agent.get_unit()
        unit.agent_id = agent_id
        unit.db_status = AssignmentState.ASSIGNED
        unit.worker_id = agent.worker_id
        return agent_id
