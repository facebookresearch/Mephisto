#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.unit import Unit
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.abstractions.blueprint import AgentState

from mephisto.abstractions.providers.mock.provider_type import PROVIDER_TYPE
from typing import List, Optional, Tuple, Dict, Mapping, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.assignment import Assignment
    from mephisto.abstractions.providers.mock.mock_datastore import MockDatastore

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class MockUnit(Unit):
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
        self.datastore: "MockDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    def launch(self, task_url: str) -> None:
        """Mock launches do nothing right now beyond updating state"""
        self.set_db_status(status=AssignmentState.LAUNCHED)

        # TODO(OWN) get this link to the frontend
        port = task_url.split(":")[1].split("/")[0]
        print(
            f"Mock task launched: http://localhost:{port} for preview, "
            f"http://localhost:{port}/?worker_id=x&assignment_id={self.db_id}"
        )
        logger.info(
            f"Mock task launched: http://localhost:{port} for preview, "
            f"http://localhost:{port}/?worker_id=x&assignment_id={self.db_id} for assignment {self.assignment_id}"
        )

        return None

    def expire(self) -> float:
        """Expiration is immediate on Mocks"""
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
        return MockUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)
