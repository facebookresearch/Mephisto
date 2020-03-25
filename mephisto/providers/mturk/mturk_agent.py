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

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        unit: "MTurkUnit" = self.get_unit()
        self.mturk_assignment_id = unit.get_mturk_assignment_id()
        # TODO any additional init as is necessary once
        # a mock DB exists

    def _get_client(self) -> Any:
        """
        Get an mturk client for usage with mturk_utils for this agent
        """
        unit = self.get_unit()
        requester: "MTurkRequester" = unit.get_requester()
        return self.datastore.get_client_for_requester(requester._requester_name)

    @classmethod
    def new_from_provider_data(
        cls,
        db: "MephistoDB",
        worker: "Worker",
        unit: "Unit",
        provider_data: Dict[str, Any],
    ) -> "Agent":
        """
        Wrapper around the new method that allows registering additional
        bookkeeping information from a crowd provider for this agent
        """
        datastore: "MTurkDatastore" = db.get_datastore_for_provider(cls.PROVIDER_TYPE)
        datastore.register_assignment_to_hit(provider_data['hit_id'], unit.db_id, provider_data["assignment_id"])
        return cls.new(db, worker, unit)

    # Required functions for Agent Interface

    def approve_work(self) -> None:
        """Approve the work done on this specific Unit"""
        client = self._get_client()
        approve_work(client, self.mturk_assignment_id, override_rejection=True)

    def reject_work(self, reason) -> None:
        """Reject the work done on this specific Unit"""
        client = self._get_client()
        reject_work(client, self.mturk_assignment_id, reason)

    def mark_done(self) -> None:
        """
        MTurk agents are marked as done on the side of MTurk, so if this agent
        is marked as done there's nothing else we need to do as the task has been
        submitted.
        """
        if self.get_status() != AgentState.STATUS_DISCONNECT:
            self.db.update_agent(
                agent_id=self.db_id, status=AgentState.STATUS_COMPLETED
            )

    @staticmethod
    def new(db: "MephistoDB", worker: "Worker", unit: "Unit") -> "Agent":
        """Create an agent for this worker to be used for work on the given Unit."""
        return MTurkAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
