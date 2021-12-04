#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.mturk_sandbox.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.mturk.mturk_agent import MTurkAgent

from typing import Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_requester import (
        SandboxMTurkRequester,
    )
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker


class SandboxMTurkAgent(MTurkAgent):
    """
    Wrapper for a regular MTurk agent that will only communicate with sandbox
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def _get_client(self) -> Any:
        """
        Get an mturk client for usage with mturk_utils for this agent
        """
        unit = self.get_unit()
        requester: "SandboxMTurkRequester" = cast(
            "SandboxMTurkRequester", unit.get_requester()
        )
        return self.datastore.get_sandbox_client_for_requester(
            requester._requester_name
        )

    @staticmethod
    def new(db: "MephistoDB", worker: "Worker", unit: "Unit") -> "Agent":
        """Create an agent for this worker to be used for work on the given Unit."""
        return SandboxMTurkAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
