#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from mephisto.data_model.blueprint import AgentState
from mephisto.core.utils import get_crowd_provider_from_type
from typing import Any, List, Optional, Tuple, Dict, Type, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.task import TaskRun


class Worker(ABC):
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        self.db_id: str = db_id
        self.db: "MephistoDB" = db
        row = db.get_worker(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.provider_type = row["provider_type"]
        self.worker_name = row["worker_name"]
        # TODO Do we want any other attributes here?

    def __new__(cls, db: "MephistoDB", db_id: str) -> "Worker":
        """
        The new method is overridden to be able to automatically generate
        the expected Worker class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Worker
        as you will instead be returned the correct Worker class according to
        the crowdprovider associated with this Worker.
        """
        if cls == Worker:
            # We are trying to construct a Worker, find what type to use and
            # create that instead
            row = db.get_worker(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class: Type[Worker] = get_crowd_provider_from_type(
                row["provider_type"]
            ).WorkerClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    # TODO make getters for helpful worker statistics
    # TODO add worker qualification tracking?

    def get_agents(self, status: Optional[str] = None) -> List["Agent"]:
        """
        Get the list of agents that this worker was responsible for, by the given status
        if needed
        """
        assert status is None or status in AgentState.valid(), "Invalid agent status"
        return self.db.find_agents(worker_id=self.db_id, status=status)

    @staticmethod
    def _register_worker(
        db: "MephistoDB", worker_name: str, provider_type: str
    ) -> "Worker":
        """
        Create an entry for this worker in the database
        """
        db_id = db.new_worker(worker_name, provider_type)
        return Worker(db, db_id)

    @classmethod
    def new_from_provider_data(cls, db, creation_data: Dict[str, Any]) -> "Worker":
        """
        Given the parameters passed through wrap_crowd_source.js, construct
        a new worker

        Basic case simply takes the worker id and registers it
        """
        return cls.new(db, creation_data['worker_name'])

    # Children classes should implement the following methods

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional["Unit"] = None
    ) -> Tuple[bool, str]:
        """Bonus this worker for work any reason. Return success of bonus"""
        raise NotImplementedError()

    def block_worker(
        self,
        reason: str,
        unit: Optional["Unit"] = None,
        requester: Optional["Requester"] = None,
    ) -> Tuple[bool, str]:
        """Block this worker for a specified reason. Return success of block"""
        raise NotImplementedError()

    def unblock_worker(self, reason: str, requester: "Requester") -> bool:
        """unblock a blocked worker for the specified reason"""
        raise NotImplementedError()

    def is_blocked(self, requester: "Requester") -> bool:
        """Determine if a worker is blocked"""
        raise NotImplementedError()

    def is_eligible(self, task_run: "TaskRun") -> bool:
        """Determine if this worker is eligible for the given task run"""
        raise NotImplementedError()

    def register(self, args: Optional[Dict[str, str]] = None) -> None:
        """Register this worker with the crowdprovider, if necessary"""
        pass

    @staticmethod
    def get_register_args() -> Dict[str, str]:
        """Get the args required to register this worker to the crowd provider"""
        # TODO perhaps at some point we can support more than just string arguents?
        return {
            # Dict is a map from param name to query text, such as
            # "HELP_TEXT": 'This key is used to put any important instruction text behind',
            # "requester_secret_key": "What is the secret key to register this worker?"
            # "worker_creation_confirmation": "What is the confirmation code to make this worker?"
        }

    @staticmethod
    def new(db: "MephistoDB", worker_name: str) -> "Worker":
        """
        Create a new worker attached to the given identifier, assuming it doesn't already
        exist in the database.

        Implementation should return the result of _register_worker when sure the worker
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()
