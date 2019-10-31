#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.providers.mturk_sandbox.provider_type import PROVIDER_TYPE
from mephisto.providers.mturk.mturk_agent import MTurkAgent

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.providers.mturk.requester import MTurkRequester
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.worker import Worker


class SandboxMTurkAgent(MTurkAgent):
    """
    Wrapper for a regular MTurk agent that will only communicate with sandbox
    """

    def _get_client(self) -> Any:
        """
        Get an mturk client for usage with mturk_utils for this agent
        """
        unit = self.get_unit()
        requester: "MTurkRequester" = unit.get_requester()
        return self.datastore.get_sandbox_client_for_requester(
            requester._requester_name
        )

    @staticmethod
    def new(db: "MephistoDB", worker: "Worker", unit: "Unit") -> "Agent":
        """Create an agent for this worker to be used for work on the given Unit."""
        return MTurkAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
