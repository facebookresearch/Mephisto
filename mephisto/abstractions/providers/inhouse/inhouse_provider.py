#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import ClassVar
from typing import Type
from typing import TYPE_CHECKING

from omegaconf import DictConfig

from mephisto.abstractions.crowd_provider import CrowdProvider
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.abstractions.providers.inhouse.inhouse_agent import InhouseAgent
from mephisto.abstractions.providers.inhouse.inhouse_datastore import InhouseDatastore
from mephisto.abstractions.providers.inhouse.inhouse_requester import InhouseRequester
from mephisto.abstractions.providers.inhouse.inhouse_unit import InhouseUnit
from mephisto.abstractions.providers.inhouse.inhouse_worker import InhouseWorker
from mephisto.abstractions.providers.inhouse.provider_type import PROVIDER_TYPE
from mephisto.operations.registry import register_mephisto_abstraction
from mephisto.utils.logger_core import get_logger

if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import SharedTaskState
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker

logger = get_logger(name=__name__)


@dataclass
class InhouseProviderArgs(ProviderArgs):
    """Base class for arguments to configure Crowd Providers"""

    # `_provider_type` cannot be `OmegaConf.MISSING`,
    # because `dataclasses` does not allow defining non-default properties before optional
    # in Python 3.9
    _provider_type: str = PROVIDER_TYPE

    ui_base_url: str = field(
        default="http://localhost:3000",
        metadata={
            "help": (
                "Base URL to task UI. "
                "Mostly needed for Docker, as hosting port may differ from container port."
            ),
            "required": False,
        },
    )


@register_mephisto_abstraction()
class InhouseProvider(CrowdProvider):
    """
    Inhouse implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """

    UnitClass: ClassVar[Type["Unit"]] = InhouseUnit

    RequesterClass: ClassVar[Type["Requester"]] = InhouseRequester

    WorkerClass: ClassVar[Type["Worker"]] = InhouseWorker

    AgentClass: ClassVar[Type["Agent"]] = InhouseAgent

    ArgsClass = InhouseProviderArgs

    PROVIDER_TYPE = PROVIDER_TYPE

    curr_db_location: ClassVar[str]

    def initialize_provider_datastore(self, storage_path: str) -> Any:
        return InhouseDatastore(datastore_root=storage_path)

    @property
    def log_prefix(self) -> str:
        return "[Inhouse Provider] "

    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        logger.debug(f"{self.log_prefix}Setting up Inhouse resources for TaskRun")
        return None

    def cleanup_resources_from_task_run(self, task_run: "TaskRun", server_url: str) -> None:
        """Cleanup all temporary data for this TaskRun"""
        logger.debug(f"{self.log_prefix}Cleanning up Inhouse resources from TaskRun")
        return None

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")

    def cleanup_qualification(self, qualification_name: str) -> None:
        """Remove the qualifications"""
        return None
