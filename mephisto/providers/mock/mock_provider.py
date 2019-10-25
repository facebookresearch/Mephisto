#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.crowd_provider import CrowdProvider
from mephisto.providers.mock.mock_agent import MockAgent
from mephisto.providers.mock.mock_requester import MockRequester
from mephisto.providers.mock.mock_unit import MockUnit
from mephisto.providers.mock.mock_worker import MockWorker

from typing import ClassVar, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun


class MockProvider(CrowdProvider):
    """
    Mock implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """

    curr_db_location: ClassVar[str]

    def get_default_db_location(self) -> str:
        """Mocks don't store anything when not told explicitly"""
        return ""

    def initialize_provider(storage_path: Optional[str] = None) -> None:
        """Mocks don't need any initialization"""
        # TODO when writing tests for the rest of the system, maybe
        # we do have a local database that we set up and
        # tear down
        assert (
            storage_path is not None
        ), "MockProviders should specify paths and be used only in tests"
        return None

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

    def worker_valid_for_task(self, worker: "Worker", task_run: "TaskRun") -> bool:
        """Workers are always valid for now"""
        return True
