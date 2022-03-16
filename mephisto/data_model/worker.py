#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedABCMeta,
    MephistoDataModelComponentMixin,
)
from typing import Any, List, Optional, Mapping, Tuple, Dict, Type, Tuple, TYPE_CHECKING
from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.qualification import GrantedQualification
    from argparse import _ArgumentGroup as ArgumentGroup


@dataclass
class WorkerArgs:
    """Base class for arguments to register a worker"""

    name: str = field(
        metadata={
            "help": (
                "Name to associate external worker id with an internal mephisto id. "
                "Should be based on the external provider id."
            )
        }
    )


class Worker(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta):
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
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
                "Direct Worker and data model access via ...Worker(db, id) is "
                "now deprecated in favor of calling Worker.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_worker(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["worker_id"]
        self.provider_type = row["provider_type"]
        self.worker_name = row["worker_name"]
        # TODO(#568) Do we want any other attributes here?

    def __new__(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ) -> "Worker":
        """
        The new method is overridden to be able to automatically generate
        the expected Worker class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Worker
        as you will instead be returned the correct Worker class according to
        the crowdprovider associated with this Worker.
        """
        from mephisto.operations.registry import get_crowd_provider_from_type

        if cls == Worker:
            # We are trying to construct a Worker, find what type to use and
            # create that instead
            if row is None:
                row = db.get_worker(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class: Type[Worker] = get_crowd_provider_from_type(
                row["provider_type"]
            ).WorkerClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    # TODO(#568) make getters for helpful worker statistics

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
        worker = Worker.get(db, db_id)
        logger.debug(f"Registered new worker {worker}")
        return worker

    @classmethod
    def new_from_provider_data(
        cls, db: "MephistoDB", creation_data: Dict[str, Any]
    ) -> "Worker":
        """
        Given the parameters passed through wrap_crowd_source.js, construct
        a new worker

        Basic case simply takes the worker id and registers it
        """
        return cls.new(db, creation_data["worker_name"])

    def get_granted_qualification(
        self, qualification_name: str
    ) -> Optional["GrantedQualification"]:
        """Return the granted qualification for this worker for the given name"""
        found_qualifications = self.db.find_qualifications(qualification_name)
        if len(found_qualifications) == 0:
            return None
        qualification = found_qualifications[0]
        granted_qualifications = self.db.check_granted_qualifications(
            qualification.db_id, self.db_id
        )
        if len(granted_qualifications) == 0:
            return None
        return granted_qualifications[0]

    def is_disqualified(self, qualification_name: str):
        """
        Find out if the given worker has been disqualified by the given qualification

        Returns True if the qualification exists and has a falsey value
        Returns False if the qualification doesn't exist or has a truthy value
        """
        qualification = self.get_granted_qualification(qualification_name)
        if qualification is None:
            return False
        return not qualification.value

    def is_qualified(self, qualification_name: str):
        """
        Find out if the given worker has qualified by the given qualification

        Returns True if the qualification exists and is truthy value
        Returns False if the qualification doesn't exist or falsey value
        """
        qualification = self.get_granted_qualification(qualification_name)
        if qualification is None:
            return False
        return bool(qualification.value)

    def revoke_qualification(self, qualification_name) -> bool:
        """
        Remove this user's qualification if it exists

        Returns True if removal happens locally and externally, False if an exception
        happens with the crowd provider
        """
        granted_qualification = self.get_granted_qualification(qualification_name)
        if granted_qualification is None:
            return False

        logger.debug(f"Revoking qualification {qualification_name} from worker {self}.")
        self.db.revoke_qualification(granted_qualification.qualification_id, self.db_id)
        try:
            self.revoke_crowd_qualification(qualification_name)
            return True
        except Exception as e:
            logger.exception(
                f"Found error while trying to revoke qualification: {repr(e)}",
                exc_info=True,
            )
            return False
        return True

    def grant_qualification(
        self, qualification_name: str, value: int = 1, skip_crowd=False
    ):
        """
        Grant a positive or negative qualification to this worker

        Returns True if granting happens locally and externally, False if an exception
        happens with the crowd provider
        """
        found_qualifications = self.db.find_qualifications(qualification_name)
        if len(found_qualifications) == 0:
            raise Exception(
                f"No qualification by the name {qualification_name} found in the db"
            )

        logger.debug(
            f"Granting worker {self} qualification {qualification_name}: {value}"
        )
        qualification = found_qualifications[0]
        self.db.grant_qualification(qualification.db_id, self.db_id, value=value)
        if not skip_crowd:
            try:
                self.grant_crowd_qualification(qualification_name, value)
                return True
            except Exception as e:
                logger.exception(
                    f"Found error while trying to grant qualification: {repr(e)}",
                    exc_info=True,
                )
                return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id})"

    # Children classes can implement the following methods

    def grant_crowd_qualification(
        self, qualification_name: str, value: int = 1
    ) -> None:
        """
        Grant a qualification by the given name to this worker

        If the CrowdProvider has a notion of qualifications, they can be granted
        in sync with Mephisto's qualifications
        """
        return None

    def revoke_crowd_qualification(self, qualification_name: str) -> None:
        """
        Revoke the qualification by the given name from this worker

        If the CrowdProvider has a notion of qualifications, they can be revoked
        in sync with Mephisto's qualifications
        """
        return None

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
    def new(db: "MephistoDB", worker_name: str) -> "Worker":
        """
        Create a new worker attached to the given identifier, assuming it doesn't already
        exist in the database.

        Implementation should return the result of _register_worker when sure the worker
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()
