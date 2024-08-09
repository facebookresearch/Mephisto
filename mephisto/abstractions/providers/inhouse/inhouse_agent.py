#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import cast
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.providers.inhouse.provider_type import PROVIDER_TYPE
from mephisto.data_model.agent import Agent
from mephisto.utils.logger_core import get_logger

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.inhouse.inhouse_datastore import InhouseDatastore
    from mephisto.abstractions.providers.inhouse.inhouse_unit import InhouseUnit
    from mephisto.abstractions.providers.inhouse.inhouse_worker import InhouseWorker
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker

logger = get_logger(name=__name__)


class InhouseAgent(Agent):
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
        self.datastore: "InhouseDatastore" = db.get_datastore_for_provider(self.PROVIDER_TYPE)
        self.unit: "InhouseUnit" = cast("InhouseUnit", self.get_unit())
        self.worker: "InhouseWorker" = cast("InhouseWorker", self.get_worker())

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
        logger.debug(
            f"{cls.log_prefix}Registering Inhouse Submission in datastore from Inhouse. "
            f"Data: {provider_data}"
        )

        return super().new_from_provider_data(db, worker, unit, provider_data)

    def approve_work(
        self,
        review_note: Optional[str] = None,
        bonus: Optional[Union[int, float]] = None,
        skip_unit_review: bool = False,
    ) -> None:
        """Approve the work done on this specific Unit"""
        logger.debug(f"{self.log_prefix}Approving work")

        if self.get_status() == AgentState.STATUS_APPROVED:
            logger.info(f"{self.log_prefix}Approving already approved agent {self}, skipping")
            return

        logger.debug(
            f"{self.log_prefix}"
            f'Work "{self.unit.db_id}" completed by worker "{self.worker.db_id}" '
            f"has been approved"
        )

        self.update_status(AgentState.STATUS_APPROVED)

        if not skip_unit_review:
            self.db.new_unit_review(
                unit_id=self.unit.db_id,
                task_id=self.unit.task_id,
                worker_id=self.unit.worker_id,
                status=AgentState.STATUS_APPROVED,
                review_note=review_note,
                bonus=str(bonus),
            )

    def soft_reject_work(self, review_note: Optional[str] = None) -> None:
        """Mark as soft rejected on Mephisto and approve Worker on Inhouse"""
        logger.debug(
            f"{self.log_prefix}"
            f'Work "{self.unit.db_id}" completed by worker "{self.worker.db_id}" '
            f"has been soft rejected"
        )
        super().soft_reject_work(review_note=review_note)

    def reject_work(self, review_note: Optional[str] = None) -> None:
        """Reject the work done on this specific Unit"""
        logger.debug(f"{self.log_prefix}Rejecting work")

        if self.get_status() == AgentState.STATUS_APPROVED:
            logger.warning(f"{self.log_prefix}Cannot reject {self}, it is already approved")
            return

        logger.debug(
            f"{self.log_prefix}"
            f'Work for Study "{self.unit.db_id}" completed by worker "{self.worker.db_id}" '
            f"has been rejected. Review note: {review_note}"
        )

        self.update_status(AgentState.STATUS_REJECTED)

        self.db.new_unit_review(
            unit_id=self.unit.db_id,
            task_id=self.unit.task_id,
            worker_id=self.unit.worker_id,
            status=AgentState.STATUS_REJECTED,
            review_note=review_note,
        )

    def mark_done(self) -> None:
        """
        Inhouse agents are marked as done on the side of Inhouse, so if this agent
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
        return InhouseAgent._register_agent(db, worker, unit, PROVIDER_TYPE)
