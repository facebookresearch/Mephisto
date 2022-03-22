#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import abstractmethod, abstractstaticmethod
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedABCMeta,
    MephistoDataModelComponentMixin,
)
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig

from typing import List, Optional, Mapping, Dict, TYPE_CHECKING, Any, Type, ClassVar

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


@dataclass
class RequesterArgs:
    """Base class for arguments to register a requester"""

    name: str = field(
        default=MISSING,
        metadata={
            "help": "Name for the requester in the Mephisto DB.",
            "required": True,
        },
    )


class Requester(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    ArgsClass: ClassVar[Type["RequesterArgs"]] = RequesterArgs

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct Requester and data model access via Requester(db, id) is "
                "now deprecated in favor of calling Requester.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_requester(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["requester_id"]
        self.provider_type: str = row["provider_type"]
        self.requester_name: str = row["requester_name"]

    def __new__(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ) -> "Requester":
        """
        The new method is overridden to be able to automatically generate
        the expected Requester class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Requester
        as you will instead be returned the correct Requester class according to
        the crowdprovider associated with this Requester.
        """
        from mephisto.operations.registry import get_crowd_provider_from_type

        if cls == Requester:
            # We are trying to construct a Requester, find what type to use and
            # create that instead
            if row is None:
                row = db.get_requester(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).RequesterClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def get_task_runs(self) -> List["TaskRun"]:
        """
        Return the list of task runs that are run by this requester
        """
        return self.db.find_task_runs(requester_id=self.db_id)

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent by this requester
        across all tasks.
        """
        task_runs = self.db.find_task_runs(requester_id=self.db_id)
        total_spend = 0.0
        for run in task_runs:
            total_spend += run.get_total_spend()
        return total_spend

    @classmethod
    def is_sandbox(self) -> bool:
        """
        Determine if this is a requester on a sandbox/test account
        """
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id})"

    @staticmethod
    def _register_requester(
        db: "MephistoDB", requester_id: str, provider_type: str
    ) -> "Requester":
        """
        Create an entry for this requester in the database
        """
        db_id = db.new_requester(requester_id, provider_type)
        requester = Requester.get(db, db_id)
        logger.debug(f"Registered new requester {requester}")
        return requester

    # Children classes should implement the following methods

    def register(self, args: Optional[DictConfig] = None) -> None:
        """
        Register this requester with the crowd provider by providing any required credentials
        or such. If no args are provided, assume the registration is already made and try
        to assert it as such.

        Should throw an exception if something is wrong with provided registration arguments.
        """
        raise NotImplementedError()

    def is_registered(self) -> bool:
        """Check to see if this requester has already been registered"""
        raise NotImplementedError()

    def get_available_budget(self) -> float:
        """
        Return the funds that this requester profile has available for usage with
        its crowdsourcing vendor
        """
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        """
        Produce a dict of this requester and important features for json serialization
        """
        return {
            "requester_id": self.db_id,
            "provider_type": self.provider_type,
            "requester_name": self.requester_name,
            "registered": self.is_registered(),
        }

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        """
        Try to create a new requester by this name, raise an exception if
        the name already exists.

        Implementation should call _register_requester(db, requester_id) when sure the requester
        can be successfully created to have it put into the db and return the result.
        """
        raise NotImplementedError()
