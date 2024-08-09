#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.abstractions.providers.inhouse.provider_type import PROVIDER_TYPE
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.logger_core import get_logger

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.inhouse.inhouse_datastore import InhouseDatastore
    from mephisto.abstractions.providers.inhouse.inhouse_requester import InhouseRequester
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.task_run import TaskRun

EXPIRE_DELAY_MAX = 0.0

logger = get_logger(name=__name__)


class InhouseUnit(Unit):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.

    It should be extended for usage with a specific crowd provider
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
        self._last_sync_time = 0.0
        self.__requester: Optional["InhouseRequester"] = None

    @property
    def log_prefix(self) -> str:
        return f"[Unit {self.db_id}] "

    def get_pay_amount(self) -> float:
        """
        Return the amount that this Unit is costing against the budget,
        calculating additional fees as relevant
        """
        logger.debug(f"{self.log_prefix}Getting pay amount")
        total_amount = super().get_pay_amount()
        logger.debug(f"{self.log_prefix}Pay amount: {total_amount}")
        return total_amount

    def launch(self, task_url: str) -> None:
        """Publish this Unit on Inhouse (making it available)"""
        logger.debug(f"{self.log_prefix}Launching Unit")
        self.set_db_status(AssignmentState.LAUNCHED)
        task_run: TaskRun = self.get_task_run()
        ui_base_url = task_run.args.provider.ui_base_url
        # This param `id` will only be used by `getAssignmentId` from `wrap_crowd_source.js`
        # as any random pseudo id to pass server validation
        unit_url = f"{ui_base_url}?worker_id=<WORKER_USERNAME>&id={self.assignment_id}"
        logger.info(f'Unit "{self.db_id}" launched: {unit_url}')
        return None

    def expire(self) -> float:
        """
        Expire this unit, removing it from being workable on the vendor.
        Return the maximum time needed to wait before we know it's taken down.
        """
        if self.get_status() not in [
            AssignmentState.EXPIRED,
            AssignmentState.COMPLETED,
        ]:
            self.set_db_status(AssignmentState.EXPIRED)

        return EXPIRE_DELAY_MAX

    def is_expired(self) -> bool:
        """
        Determine if this unit is expired as according to the vendor.

        In this case, we keep track of the expiration locally by refreshing
        the study's status and seeing if we've expired.
        """
        return self.get_status() == AssignmentState.EXPIRED

    @staticmethod
    def new(db: "MephistoDB", assignment: "Assignment", index: int, pay_amount: float) -> "Unit":
        """Create a Unit for the given assignment"""
        unit = InhouseUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)
        logger.debug(f'{InhouseUnit.log_prefix}Created Unit "{unit.db_id}"')
        return unit
