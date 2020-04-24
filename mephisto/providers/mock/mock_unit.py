#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.assignment import Unit
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.blueprint import AgentState

from mephisto.providers.mock.provider_type import PROVIDER_TYPE
from typing import List, Optional, Tuple, Dict, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.assignment import Assignment


class MockUnit(Unit):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.

    It should be extended for usage with a specific crowd provider
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        # TODO(#97) any additional init as is necessary once
        # a mock DB exists

    def launch(self, task_url: str) -> None:
        """Mock launches do nothing right now beyond updating state"""
        self.db.update_unit(self.db_id, status=AssignmentState.LAUNCHED)
        return None

    def expire(self) -> float:
        """Expiration is immediate on Mocks"""
        self.db.update_unit(self.db_id, status=AssignmentState.EXPIRED)
        return 0.0

    def is_expired(self) -> bool:
        """Determine if this unit is expired as according to the vendor."""
        # TODO(#97) pull from the mockdb
        return True

    @staticmethod
    def new(
        db: "MephistoDB", assignment: "Assignment", index: int, pay_amount: float
    ) -> "Unit":
        """Create a Unit for the given assignment"""
        return MockUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)
