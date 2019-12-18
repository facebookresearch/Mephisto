#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.agent import Agent
from mephisto.data_model.blueprint import AgentState
from mephisto.providers.mturk.provider_type import PROVIDER_TYPE
from mephisto.providers.mturk.mturk_utils import (
    approve_work,
    reject_work,
    get_assignment,
)

from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.packet import Packet
    from mephisto.providers.mturk.requester import MTurkRequester
    from mephisto.providers.mturk.unit import MTurkUnit
    from mephisto.providers.mturk.datastore import MTurkDatastore


class MTurkAgent(Agent):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            PROVIDER_TYPE
        )
        unit: "MTurkUnit" = self.get_unit()
        # self.mturk_assignment_id = unit.get_mturk_assignment_id()
        # TODO any additional init as is necessary once
        # a mock DB exists

    def _get_client(self) -> Any:
        """
        Get an mturk client for usage with mturk_utils for this agent
        """
        unit = self.get_unit()
        requester: "MTurkRequester" = unit.get_requester()
        return self.datastore.get_client_for_requester(requester._requester_name)

    # Required functions for Agent Interface

    def observe(self, action: "Packet") -> None:
        """
        Pass the observed information to the AgentState, then
        push that information to the user
        """
        # TODO implement with the task runner system
        raise NotImplementedError()

    def act(self, timeout=None) -> Optional["Packet"]:
        """
        Request information from the Agent's frontend. If non-blocking,
        should return None if no actions are ready to be returned.
        """
        # TODO implement with the task runner system
        raise NotImplementedError()

    def approve_work(self) -> None:
        """Approve the work done on this specific Unit"""
        client = self._get_client()
        approve_work(client, self.mturk_assignment_id, override_rejection=True)

    def reject_work(self, reason) -> None:
        """Reject the work done on this specific Unit"""
        client = self._get_client()
        reject_work(client, self.mturk_assignment_id, reason)

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
        # TODO do we need to query any other statuses?
        # When do we update this?
        return self.db_status

    def mark_done(self) -> None:
        """
        Take any required step with the crowd_provider to ensure that
        the worker can submit their work and be marked as complete via
        a call to get_status
        """
        # TODO implement
        raise NotImplementedError()

    @staticmethod
    def new(db: "MephistoDB", worker: "Worker", unit: "Unit") -> "Agent":
        """Create an agent for this worker to be used for work on the given Unit."""
        return MTurkAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
