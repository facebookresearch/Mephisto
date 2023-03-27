#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import cast
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.agent import Agent
from . import api as prolific_api

if TYPE_CHECKING:
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker


class ProlificAgent(Agent):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "ProlificDatastore" = db.get_datastore_for_provider(self.PROVIDER_TYPE)
        if db_id not in self.datastore.agent_data:
            self.datastore.agent_data[db_id] = {
                "observed": [],
                "pending_acts": [],
                "acts": [],
                "pending_submit": None,
            }

    def _get_client(self) -> prolific_api:
        """Get a Prolific client"""
        unit = self.get_unit()
        requester: "ProlificRequester" = cast('ProlificRequester', unit.get_requester())
        return self.datastore.get_client_for_requester(requester.requester_name)

    def observe(self, live_update: Dict[str, Any]) -> None:
        """Put observations into this Prolific agent's observation list"""
        self.datastore.agent_data[self.db_id]["observed"].append(live_update)
        super().observe(live_update)

    def get_live_update(self, timeout=None) -> Optional[Dict[str, Any]]:
        """
        Either take an act from this mock agent's act queue (for use
        by tests and other mock purposes) or request a regular act
        (for use in manual testing).
        """  # TODO (#1008)
        if len(self.datastore.agent_data[self.db_id]["pending_acts"]) > 0:
            act = self.datastore.agent_data[self.db_id]["pending_acts"].pop(0)
        else:
            act = super().get_live_update(timeout=timeout)

        if act is not None:
            self.datastore.agent_data[self.db_id]["acts"].append(act)
        return act

    def approve_work(self) -> None:
        """
        Approve the work done on this specific Unit

        Prolific Units
        """
        self.update_status(AgentState.STATUS_APPROVED)

    def reject_work(self, reason) -> None:
        """
        Reject the work done on this specific Unit
        """
        self.update_status(AgentState.STATUS_REJECTED)

    def mark_done(self):
        pass

    def mark_disconnected(self) -> None:
        """Mark this Prolific agent as having disconnected"""
        self.update_status(AgentState.STATUS_DISCONNECT)

    def await_submit(self, timeout: Optional[int] = None) -> bool:
        """
        Check the submission status of this agent, first popping off
        and triggering a local submit if there is one on a timeout submit
        """
        if self.did_submit.is_set():
            return True
        if timeout is not None:
            local_submit = self.datastore.agent_data[self.db_id]["pending_submit"]
            if local_submit is not None:
                self.handle_submit(local_submit)
        return super().await_submit(timeout)

    @staticmethod
    def new(db: "MephistoDB", worker: "Worker", unit: "Unit") -> "Agent":
        """Create an agent for this worker to be used for work on the given Unit."""
        return ProlificAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
