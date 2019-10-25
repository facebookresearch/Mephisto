#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.worker import Worker
from mephisto.providers.mock.provider_type import PROVIDER_TYPE
from typing import List, Optional, Tuple, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB


class MockWorker(Worker):
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        # TODO any additional init as is necessary once
        # a mock DB exists

    def bonus_worker(self, amount: float, reason: str) -> bool:
        """Bonus this worker for work any reason. Return success of bonus"""
        return True

    def block_worker(self, reason: str) -> bool:
        """Block this worker for a specified reason. Return success of block"""
        return True

    def unblock_worker(self, reason: str) -> bool:
        """unblock a blocked worker for the specified reason"""
        return True

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        return MockWorker._register_worker(db, worker_id, PROVIDER_TYPE)
