#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractproperty
from mephisto.data_model.agent_state import AgentState
from mephisto.core.utils import get_crowd_provider_from_type, get_task_runner_from_type
from mephisto.data_model.assignment import Unit
from mephisto.data_model.requester import Requester
from mephisto.data_model.worker import Worker
from mephisto.data_model.agent import Agent

from typing import List, Optional, Tuple, Dict, Any, ClassVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun


class CrowdProvider(ABC):
    """
    Base class that defines the required functionality for
    the mephisto system to be able to interface with an
    external crowdsourcing vendor.

    Implementing the methods within, as well as supplying
    wrapped Unit, Requester, Worker, and Agent classes
    should ensure support for a vendor.
    """

    UnitClass: ClassVar[Type[Unit]] = Unit

    RequesterClass: ClassVar[Type[Requester]] = Requester

    WorkerClass: ClassVar[Type[Worker]] = Worker

    AgentClass: ClassVar[Type[Agent]] = Agent

    SUPPORTED_TASK_TYPES: ClassVar[List[str]]

    def __init__(self, db_path=None):
        """
        Crowd provider classes should keep as much of their state
        as possible in their non-python datastore. This way
        the system can work even after shutdowns, and the
        state of the system can be managed or observed from
        other processes.
        """
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = self.get_default_db_location()
        self.initialize_provider(self.db_path)

    @abstractmethod
    def get_default_db_location(self):
        """
        Return the folder root we expect the datastore for this
        crowdprovider to be set up in.
        """
        raise NotImplementedError()

    @abstractmethod
    def initialize_provider(storage_path=None):
        """
        Do whatever is required to initialize this provider insofar
        as setting up local or external state is required to ensure
        that this vendor is usable.

        Local data storage should be put into the given root path.
        """
        raise NotImplementedError()

    @abstractmethod
    def setup_resources_for_task_run(self, task_run: "TaskRun", server_url: str):
        """
        Setup any required resources for managing any additional resources
        surrounding a specific task run.
        """
        raise NotImplementedError()

    @abstractmethod
    def cleanup_resources_from_task_run(self, task_run: "TaskRun", server_url: str):
        """
        Destroy any resources set up specifically for this task run
        """
        raise NotImplementedError()
