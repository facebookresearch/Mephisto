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
from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.agent import Agent
from mephisto.utils.logger_core import get_logger
from .api.client import ProlificClient

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
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "ProlificDatastore" = db.get_datastore_for_provider(self.PROVIDER_TYPE)
        self.unit: "ProlificUnit" = cast("ProlificUnit", self.get_unit())
        self.worker: "ProlificWorker" = cast("ProlificWorker", self.get_worker())

    def _get_client(self) -> ProlificClient:
        """Get a Prolific client"""
        requester: "ProlificRequester" = cast(
            "ProlificRequester", self.unit.get_requester()
        )
        return self.datastore.get_client_for_requester(requester.requester_name)

    @property
    def log_prefix(self) -> str:
        return f"[Agent {self.db_id}] "

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
        from mephisto.abstractions.providers.prolific.prolific_unit import ProlificUnit

        logger.debug(
            f"Registering Prolific Submission in datastore from Prolific. Data: {provider_data}"
        )

        assert isinstance(
            unit, ProlificUnit
        ), "Can only register Prolific agents to Prolific units"

        prolific_study_id = provider_data["prolific_study_id"]
        prolific_submission_id = provider_data["assignment_id"]
        unit.register_from_provider_data(prolific_study_id, prolific_submission_id)

        logger.debug("Prolific Submission has been registered successfully")

        return super().new_from_provider_data(db, worker, unit, provider_data)

    def approve_work(self) -> None:
        """Approve the work done on this specific Unit"""
        logger.debug(f"{self.log_prefix}Approving work")

        if self.get_status() == AgentState.STATUS_APPROVED:
            logger.info(
                f"{self.log_prefix}Approving already approved agent {self}, skipping"
            )
            return

        client = self._get_client()
        prolific_study_id = self.unit.get_prolific_study_id()
        worker_id = self.worker.get_prolific_participant_id()
        prolific_utils.approve_work(
            client, study_id=prolific_study_id, worker_id=worker_id,
        )

        logger.debug(
            f"{self.log_prefix}"
            f'Work for Study "{prolific_study_id}" completed by worker "{worker_id}" '
            f"has been approved"
        )

        self.update_status(AgentState.STATUS_APPROVED)

    def soft_reject_work(self) -> None:
        """Mark as soft rejected on Mephisto and approve Worker on Prolific"""
        super().soft_reject_work()

        client = self._get_client()
        prolific_study_id = self.unit.get_prolific_study_id()
        worker_id = self.worker.get_prolific_participant_id()
        prolific_utils.approve_work(
            client, study_id=prolific_study_id, worker_id=worker_id,
        )

        logger.debug(
            f"{self.log_prefix}"
            f'Work for Study "{prolific_study_id}" completed by worker "{worker_id}" '
            f"has been soft rejected"
        )

    def reject_work(self, reason) -> None:
        """Reject the work done on this specific Unit"""
        logger.debug(f"{self.log_prefix}Rejecting work")

        if self.get_status() == AgentState.STATUS_APPROVED:
            logger.warning(f"{self.log_prefix}Cannot reject {self}, it is already approved")
            return

        client = self._get_client()
        prolific_study_id = self.unit.get_prolific_study_id()
        worker_id = self.worker.get_prolific_participant_id()

        # TODO (#1008): remove this suppression of exception when Prolific fixes their API
        from .api.exceptions import ProlificException

        try:
            prolific_utils.reject_work(
                client, study_id=prolific_study_id, worker_id=worker_id,
            )
        except ProlificException:
            logger.info(
                "IGNORE ABOVE ERROR - it's a bug of Prolific API. "
                "It always returns error here, even when the request works."
            )

        logger.debug(
            f"{self.log_prefix}"
            f'Work for Study "{prolific_study_id}" completed by worker "{worker_id}" '
            f"has been rejected. Reason: {reason}"
        )

        self.update_status(AgentState.STATUS_REJECTED)

    def mark_done(self) -> None:
        """
        Prolific agents are marked as done on the side of Prolific, so if this agent
        is marked as done there's nothing else we need to do as the task has been
        submitted.
        """
        logger.debug(f"{self.log_prefix}Work has been marked as Done")

        if self.get_status() != AgentState.STATUS_DISCONNECT:
            self.db.update_agent(
                agent_id=self.db_id,
                status=AgentState.STATUS_COMPLETED,
            )

    @staticmethod
    def new(db: "MephistoDB", worker: "Worker", unit: "Unit") -> "Agent":
        """Create an agent for this worker to be used for work on the given Unit."""
        return ProlificAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
