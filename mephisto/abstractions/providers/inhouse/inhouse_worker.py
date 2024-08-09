#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import cast
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

from mephisto.abstractions.providers.inhouse.provider_type import PROVIDER_TYPE
from mephisto.data_model.worker import Worker
from mephisto.utils.logger_core import get_logger

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.inhouse.inhouse_datastore import InhouseDatastore
    from mephisto.abstractions.providers.inhouse.inhouse_unit import InhouseUnit
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit

DEFAULT_IS_ELIGIBLE = True

logger = get_logger(name=__name__)


class InhouseWorker(Worker):
    """
    This class represents an individual - namely a person.
    It maintains components of ongoing identity for a user.
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "InhouseDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    @property
    def log_prefix(self) -> str:
        return f"[Worker {self.db_id}] "

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional["Unit"] = None
    ) -> Tuple[bool, str]:
        """Bonus a worker for work any reason. Return success of bonus"""
        logger.debug(f"{self.log_prefix}Paying bonuses")

        if unit is None:
            return False, "bonusing via compensation tasks not yet available"

        unit: "InhouseUnit" = cast("InhouseUnit", unit)
        if unit is None:
            # TODO(WISH) soft block from all requesters? Maybe have the main requester soft block?
            return (
                False,
                "Paying bonuses without a unit not yet supported for InhouseWorkers",
            )

        logger.debug(
            f"{self.log_prefix}Trying to pay bonuses. "
            f"But with Inhouse provider you need to do this manually"
        )

        return True, ""

    @staticmethod
    def _get_first_task_run(requester: "Requester") -> "TaskRun":
        task_runs: List[TaskRun] = requester.get_task_runs()
        return task_runs[0]

    def block_worker(
        self,
        reason: str,
        unit: Optional["Unit"] = None,
        requester: Optional["Requester"] = None,
    ) -> Tuple[bool, str]:
        """Block this worker for a specified reason. Return success of block"""
        logger.debug(f"{self.log_prefix}Blocking worker {self.worker_name}")
        self.datastore.set_worker_blocked(self.db_id, True)
        logger.debug(f"{self.log_prefix}Worker {self.worker_name} blocked")
        return True, ""

    def unblock_worker(self, reason: str, requester: "Requester") -> Tuple[bool, str]:
        """Unblock a blocked worker for the specified reason. Return success of unblock"""
        logger.debug(f"{self.log_prefix}Unlocking worker {self.worker_name}")
        self.datastore.set_worker_blocked(self.db_id, False)
        logger.debug(f"{self.log_prefix}Worker {self.worker_name} unblocked")
        return True, ""

    def is_blocked(self, requester: "Requester") -> bool:
        """Determine if a worker is blocked"""
        is_blocked = self.datastore.get_worker_blocked(self.db_id)
        logger.debug(f'{self.log_prefix}Worker "{self.worker_name}" {is_blocked=}')
        return is_blocked

    def is_eligible(self, task_run: "TaskRun") -> bool:
        """Determine if this worker is eligible for the given task run"""
        return DEFAULT_IS_ELIGIBLE

    def send_feedback_message(self, text: str, unit: "Unit") -> bool:
        """Send feedback message to a worker"""
        logger.debug(f"Inhouse sending feedback message to worker: '{text}'. Unit: {unit}")
        return True

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        new_worker = InhouseWorker._register_worker(db, worker_id, PROVIDER_TYPE)
        # Save worker in provider-specific datastore
        datastore: "InhouseDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)
        datastore.ensure_worker_exists(worker_id)
        return new_worker
