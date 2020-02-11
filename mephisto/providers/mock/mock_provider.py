#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.crowd_provider import CrowdProvider
from mephisto.providers.mock.mock_agent import MockAgent
from mephisto.providers.mock.mock_requester import MockRequester
from mephisto.providers.mock.mock_unit import MockUnit
from mephisto.providers.mock.mock_worker import MockWorker
from mephisto.providers.mock.provider_type import PROVIDER_TYPE

from typing import ClassVar, Dict, Any, Optional, Type, List, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent


class MockProvider(CrowdProvider):
    """
    Mock implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """

    UnitClass: ClassVar[Type["Unit"]] = MockUnit

    RequesterClass: ClassVar[Type["Requester"]] = MockRequester

    WorkerClass: ClassVar[Type["Worker"]] = MockWorker

    AgentClass: ClassVar[Type["Agent"]] = MockAgent

    SUPPORTED_TASK_TYPES: ClassVar[List[str]] = ["mock"]

    PROVIDER_TYPE = PROVIDER_TYPE

    curr_db_location: ClassVar[str]

    def initialize_provider_datastore(self, storage_path: str = None) -> Any:
        """Mocks don't need any initialization"""
        # TODO when writing tests for the rest of the system, maybe
        # we do have a local database that we set up and
        # tear down
        # Mock providers create a dict to store any important info in
        return {"agents": {}, "requesters": {}, "units": {}, "workers": {}}

    def setup_resources_for_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """Mocks don't do any initialization"""
        return None

    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """Mocks don't do any initialization"""
        return None
