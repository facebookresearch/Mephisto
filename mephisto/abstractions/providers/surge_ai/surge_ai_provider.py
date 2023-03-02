#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass
from typing import Any
from typing import ClassVar
from typing import Type
from typing import TYPE_CHECKING

from mephisto.abstractions.crowd_provider import CrowdProvider
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.abstractions.providers.surge_ai.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.surge_ai.surge_ai_agent import SurgeAIAgent
from mephisto.abstractions.providers.surge_ai.surge_ai_datastore import SurgeAIDatastore
from mephisto.abstractions.providers.surge_ai.surge_ai_requester import SurgeAIRequester
from mephisto.abstractions.providers.surge_ai.surge_ai_unit import SurgeAIUnit
from mephisto.abstractions.providers.surge_ai.surge_ai_worker import SurgeAIWorker
from mephisto.operations.registry import register_mephisto_abstraction

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.blueprint import SharedTaskState
    from omegaconf import DictConfig


@dataclass
class SurgeAIProviderArgs(ProviderArgs):
    """Base class for arguments to configure Crowd Providers"""

    _provider_type: str = PROVIDER_TYPE


@register_mephisto_abstraction()
class SurgeAIProvider(CrowdProvider):
    """
    Surge AI implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """

    UnitClass: ClassVar[Type["Unit"]] = SurgeAIUnit

    RequesterClass: ClassVar[Type["Requester"]] = SurgeAIRequester

    WorkerClass: ClassVar[Type["Worker"]] = SurgeAIWorker

    AgentClass: ClassVar[Type["Agent"]] = SurgeAIAgent

    ArgsClass = SurgeAIProviderArgs

    PROVIDER_TYPE = PROVIDER_TYPE

    curr_db_location: ClassVar[str]

    def initialize_provider_datastore(self, storage_path: str) -> Any:
        return SurgeAIDatastore(datastore_root=storage_path)

    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        return None

    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        return None

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")
