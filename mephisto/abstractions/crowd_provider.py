#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.abstractions.blueprint import AgentState, SharedTaskState
from mephisto.data_model.unit import Unit
from mephisto.data_model.requester import Requester
from mephisto.data_model.worker import Worker
from mephisto.data_model.agent import Agent

from typing import List, Optional, Tuple, Dict, Any, ClassVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup


@dataclass
class ProviderArgs:
    """Base class for arguments to configure Crowd Providers"""

    _provider_type: str = MISSING
    requester_name: str = MISSING


class CrowdProvider(ABC):
    """
    Base class that defines the required functionality for
    the mephisto system to be able to interface with an
    external crowdsourcing vendor.

    Implementing the methods within, as well as supplying
    wrapped Unit, Requester, Worker, and Agent classes
    should ensure support for a vendor.
    """

    PROVIDER_TYPE = "__PROVIDER_BASE_CLASS__"

    UnitClass: ClassVar[Type[Unit]] = Unit

    RequesterClass: ClassVar[Type[Requester]] = Requester

    WorkerClass: ClassVar[Type[Worker]] = Worker

    AgentClass: ClassVar[Type[Agent]] = Agent

    ArgsClass: ClassVar[Type[ProviderArgs]] = ProviderArgs

    def __init__(self, db: "MephistoDB"):
        """
        Crowd provider classes should keep as much of their state
        as possible in their non-python datastore. This way
        the system can work even after shutdowns, and the
        state of the system can be managed or observed from
        other processes.

        In order to set up a datastore, init should check to see
        if one is already set (using get_datastore_for_provider)
        and use that one if available, otherwise make a new one
        and register it with the database.
        """
        self.db = db
        if db.has_datastore_for_provider(self.PROVIDER_TYPE):
            self.datastore = db.get_datastore_for_provider(self.PROVIDER_TYPE)
        else:
            self.datastore_root = db.get_db_path_for_provider(self.PROVIDER_TYPE)
            self.datastore = self.initialize_provider_datastore(self.datastore_root)
            db.set_datastore_for_provider(self.PROVIDER_TYPE, self.datastore)

    @classmethod
    def is_sandbox(cls) -> bool:
        """Determine if the given crowd provider is a sandbox provider"""
        return cls.RequesterClass.is_sandbox()

    @classmethod
    def assert_task_args(cls, args: DictConfig, shared_state: "SharedTaskState"):
        """
        Assert that the provided arguments are valid. Should
        fail if a task launched with these arguments would
        not work
        """
        return

    @classmethod
    @abstractmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        raise NotImplementedError

    @abstractmethod
    def initialize_provider_datastore(self, storage_path: str) -> Any:
        """
        Do whatever is required to initialize this provider insofar
        as setting up local or external state is required to ensure
        that this vendor is usable.

        Local data storage should be put into the given root path.

        This method should return the local data storage component that
        is required to do any object initialization, as it will be available
        from the MephistoDB in a db.get_provider_datastore(PROVIDER_TYPE).
        """
        raise NotImplementedError()

    @abstractmethod
    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: DictConfig,
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        """
        Setup any required resources for managing any additional resources
        surrounding a specific task run.
        """
        raise NotImplementedError()

    @abstractmethod
    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """
        Destroy any resources set up specifically for this task run
        """
        raise NotImplementedError()

    def cleanup_qualification(self, qualification_name: str) -> None:
        """
        Remove the linked qualification from the crowdprovider if it exists
        """
        return None
