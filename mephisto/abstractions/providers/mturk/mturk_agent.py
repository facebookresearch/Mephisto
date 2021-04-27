#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.agent import Agent
from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.providers.mturk.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.mturk.mturk_utils import (
    approve_work,
    reject_work,
    get_assignment,
)

from typing import List, Optional, Tuple, Dict, Mapping, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.packet import Packet
    from mephisto.abstractions.providers.mturk.requester import MTurkRequester
    from mephisto.abstractions.providers.mturk.unit import MTurkUnit
    from mephisto.abstractions.providers.mturk.datastore import MTurkDatastore


class MTurkAgent(Agent):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(
        self, db: "MephistoDB", db_id: str, row: Optional[Mapping[str, Any]] = None
    ):
        super().__init__(db, db_id, row=row)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        unit: "MTurkUnit" = self.get_unit()
        self.mturk_assignment_id = unit.get_mturk_assignment_id()
        # TODO(#97) any additional init as is necessary once
        # a mock DB exists

    def _get_mturk_assignment_id(self):
        if self.mturk_assignment_id is None:
            self.mturk_assignment_id = self.get_unit().get_mturk_assignment_id()
        return self.mturk_assignment_id

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
        unit.register_from_provider_data(
            provider_data["hit_id"], provider_data["assignment_id"]
        )
        return super().new_from_provider_data(db, worker, unit, provider_data)

    # Required functions for Agent Interface

    def approve_work(self) -> None:
        """Approve the work done on this specific Unit"""
        if self.get_status() == AgentState.STATUS_APPROVED:
            logging.info(f"Approving already approved agent {self}, skipping")
            return
        client = self._get_client()
        approve_work(client, self._get_mturk_assignment_id(), override_rejection=True)
        self.update_status(AgentState.STATUS_APPROVED)

    def reject_work(self, reason) -> None:
        """Reject the work done on this specific Unit"""
        if self.get_status() == AgentState.STATUS_APPROVED:
            logging.warning(f"Cannot reject {self}, it is already approved")
            return
        client = self._get_client()
        reject_work(client, self._get_mturk_assignment_id(), reason)
        self.update_status(AgentState.STATUS_REJECTED)

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
