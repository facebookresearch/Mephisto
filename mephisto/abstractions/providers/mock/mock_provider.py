#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.crowd_provider import CrowdProvider, ProviderArgs
from mephisto.abstractions.providers.mock.mock_agent import MockAgent
from mephisto.abstractions.providers.mock.mock_requester import MockRequester
from mephisto.abstractions.providers.mock.mock_unit import MockUnit
from mephisto.abstractions.providers.mock.mock_worker import MockWorker
from mephisto.abstractions.providers.mock.mock_datastore import MockDatastore
from mephisto.abstractions.providers.mock.provider_type import PROVIDER_TYPE
from mephisto.data_model.requester import RequesterArgs
from mephisto.operations.registry import register_mephisto_abstraction
from dataclasses import dataclass, field

from typing import ClassVar, Dict, Any, Optional, Type, List, TYPE_CHECKING

import os

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.blueprint import SharedTaskState
    from omegaconf import DictConfig


@dataclass
class MockProviderArgs(ProviderArgs):
    """Base class for arguments to configure Crowd Providers"""

    _provider_type: str = PROVIDER_TYPE


@register_mephisto_abstraction()
class MockProvider(CrowdProvider):
    """
    Mock implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """

    UnitClass: ClassVar[Type["Unit"]] = MockUnit

    RequesterClass: ClassVar[Type["Requester"]] = MockRequester

    WorkerClass: ClassVar[Type["Worker"]] = MockWorker

    AgentClass: ClassVar[Type["Agent"]] = MockAgent

    ArgsClass = MockProviderArgs

    PROVIDER_TYPE = PROVIDER_TYPE

    curr_db_location: ClassVar[str]

    def initialize_provider_datastore(self, storage_path: str) -> Any:
        """Mocks don't need any initialization"""
        return MockDatastore(datastore_root=storage_path)

    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        """Mocks don't do any initialization"""
        return None

    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """Mocks don't do any initialization"""
        return None

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")
