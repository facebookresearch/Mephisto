#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.mturk_sandbox.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.mturk.mturk_provider import (
    MTurkProvider,
    MTurkProviderArgs,
)
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_agent import (
    SandboxMTurkAgent,
)
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_requester import (
    SandboxMTurkRequester,
)
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_unit import (
    SandboxMTurkUnit,
)
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_worker import (
    SandboxMTurkWorker,
)
from mephisto.operations.registry import register_mephisto_abstraction

import os
from dataclasses import dataclass

from typing import Any, ClassVar, Type, List, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent


@dataclass
class SandboxMTurkProviderArgs(MTurkProviderArgs):
    """Provider args for a sandbox MTurk provider"""

    _provider_type: str = PROVIDER_TYPE


@register_mephisto_abstraction()
class SandboxMTurkProvider(MTurkProvider):
    """
    Mock implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    UnitClass: ClassVar[Type["Unit"]] = SandboxMTurkUnit

    RequesterClass: ClassVar[Type["Requester"]] = SandboxMTurkRequester

    WorkerClass: ClassVar[Type["Worker"]] = SandboxMTurkWorker

    AgentClass: ClassVar[Type["Agent"]] = SandboxMTurkAgent

    ArgsClass = SandboxMTurkProviderArgs

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_sandbox_client_for_requester(requester_name)

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")

    def cleanup_qualification(self, qualification_name: str) -> None:
        """Remove the qualification from the sandbox server"""
        return super().cleanup_qualification(f"{qualification_name}_sandbox")
