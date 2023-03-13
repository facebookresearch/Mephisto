#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit

if TYPE_CHECKING:
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.assignment import Assignment

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class ProlificUnit(Unit):
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
        self.datastore: "ProlificDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    def launch(self, task_url: str) -> None:
        """Mock launches do nothing right now beyond updating state"""  # TODO(#1009)
        self.set_db_status(status=AssignmentState.LAUNCHED)

        # TODO(OWN) get this link to the frontend
        port = task_url.split(":")[1].split("/")[0]
        if port:
            assignment_url = (
                f"http://localhost:{port}/?worker_id=x&assignment_id={self.db_id}"
            )
        else:
            assignment_url = f"{task_url}/?worker_id=x&assignment_id={self.db_id}"
        logger.info(
            f"Mock task launched: http://localhost:{port} for preview, "  # TODO(#1009)
            f"{assignment_url}"
        )
        logger.info(
            f"Mock task launched: http://localhost:{port} for preview, "  # TODO(#1009)
            f"{assignment_url} for assignment {self.assignment_id}"
        )

        return None

    def expire(self) -> float:
        """Expiration is immediate on Mocks"""  # TODO(#1009)
        if self.get_status() not in [
            AssignmentState.EXPIRED,
            AssignmentState.COMPLETED,
        ]:
            self.set_db_status(AssignmentState.EXPIRED)
        self.datastore.set_unit_expired(self.db_id, True)
        return 0.0

    def is_expired(self) -> bool:
        """Determine if this unit is expired as according to the vendor."""
        return self.datastore.get_unit_expired(self.db_id)

    @staticmethod
    def new(
        db: "MephistoDB", assignment: "Assignment", index: int, pay_amount: float
    ) -> "Unit":
        """Create a Unit for the given assignment"""
        return ProlificUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)
