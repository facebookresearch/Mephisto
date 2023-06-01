#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import cast
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.agent import Agent
from mephisto.utils.logger_core import get_logger
from . import api as prolific_api

if TYPE_CHECKING:
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
    from mephisto.abstractions.providers.prolific.prolific_unit import ProlificUnit
    from mephisto.abstractions.providers.prolific.prolific_worker import ProlificWorker
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker

logger = get_logger(name=__name__)


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
        db: 'MephistoDB',
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: 'ProlificDatastore' = db.get_datastore_for_provider(self.PROVIDER_TYPE)
        self.unit: 'ProlificUnit' = cast('ProlificUnit', self.get_unit())
        self.worker: 'ProlificWorker' = cast('ProlificWorker', self.get_worker())

    def _get_client(self) -> prolific_api:
        """Get a Prolific client"""
        requester: 'ProlificRequester' = cast('ProlificRequester', self.unit.get_requester())
        return self.datastore.get_client_for_requester(requester.requester_name)

    def approve_work(self) -> None:
        """Approve the work done on this specific Unit"""
        if self.get_status() == AgentState.STATUS_APPROVED:
            logger.info(f'Approving already approved agent {self}, skipping')
            return

        client = self._get_client()
        prolific_study_id = self.unit.get_prolific_study_id()
        worker_id = self.worker.get_prolific_worker_id()
        prolific_utils.approve_work(client, study_id=prolific_study_id, worker_id=worker_id)
        self.update_status(AgentState.STATUS_APPROVED)

    def reject_work(self, reason) -> None:
        """Reject the work done on this specific Unit"""
        if self.get_status() == AgentState.STATUS_APPROVED:
            logger.warning(f'Cannot reject {self}, it is already approved')
            return

        client = self._get_client()
        prolific_study_id = self.unit.get_prolific_study_id()
        worker_id = self.worker.get_prolific_worker_id()
        prolific_utils.reject_work(client, study_id=prolific_study_id, worker_id=worker_id)
        self.update_status(AgentState.STATUS_REJECTED)

    def mark_done(self) -> None:
        """
        Prolific agents are marked as done on the side of Prolific, so if this agent
        is marked as done there's nothing else we need to do as the task has been
        submitted.
        """
        if self.get_status() != AgentState.STATUS_DISCONNECT:
            self.db.update_agent(agent_id=self.db_id, status=AgentState.STATUS_COMPLETED)

    @staticmethod
    def new(db: 'MephistoDB', worker: 'Worker', unit: 'Unit') -> 'Agent':
        """Create an agent for this worker to be used for work on the given Unit."""
        return ProlificAgent._register_agent(db, worker, unit, PROVIDER_TYPE)