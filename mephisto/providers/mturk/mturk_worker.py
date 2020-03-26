#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.worker import Worker
from mephisto.providers.mturk.provider_type import PROVIDER_TYPE
from mephisto.providers.mturk.mturk_utils import (
    pay_bonus,
    block_worker,
    unblock_worker,
    is_worker_blocked,
)

from uuid import uuid4

from typing import List, Optional, Tuple, Dict, Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.providers.mturk.mturk_datastore import MTurkDatastore
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.requester import Requester
    from mephisto.providers.mturk.mturk_unit import MTurkUnit
    from mephisto.providers.mturk.mturk_requester import MTurkRequester


class MTurkWorker(Worker):
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        # TODO are there MTurk specific worker things to track?
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        self._worker_name = self.worker_name  # sandbox workers use a different name

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional["Unit"] = None
    ) -> Tuple[bool, str]:
        """Bonus this worker for work any reason. Return tuple of success and failure message"""
        if unit is None:
            # TODO implement
            return False, "bonusing via compensation tasks not yet available"

        unit = cast("MTurkUnit", unit)
        requester = unit.get_assignment().get_task_run().get_requester()
        client = self._get_client(requester.requester_name)
        mturk_assignment_id = unit.get_mturk_assignment_id() 
        assert mturk_assignment_id is not None, "Cannot bonus for a unit with no agent"
        pay_bonus(
            client,
            self._worker_name,
            amount,
            mturk_assignment_id,
            reason,
            str(uuid4()),
        )
        return True, ""

    def block_worker(
        self,
        reason: str,
        unit: Optional["Unit"] = None,
        requester: Optional["Requester"] = None,
    ) -> Tuple[bool, str]:
        """Block this worker for a specified reason. Return success of block"""
        if unit is None and requester is None:
            # TODO soft block from all requesters? Maybe have the master
            # requester soft block?
            # revisit when qualifications are done
            return (
                False,
                "Blocking without a unit or requester not yet supported for MTurkWorkers",
            )
        elif unit is not None and requester is None:
            # TODO disqual from this worker, so all others can disqual as well
            # revisit when qualifications are done
            requester = unit.get_assignment().get_task_run().get_requester()
        requester = cast("MTurkRequester", requester)
        client = self._get_client(requester._requester_name)
        block_worker(client, self._worker_name, reason)
        return True, ""

    def unblock_worker(self, reason: str, requester: "Requester") -> bool:
        """unblock a blocked worker for the specified reason. Return success of unblock"""
        requester = cast("MTurkRequester", requester)
        client = self._get_client(requester._requester_name)
        unblock_worker(client, self._worker_name, reason)
        return True

    def is_blocked(self, requester: "Requester") -> bool:
        """Determine if a worker is blocked"""
        requester = cast("MTurkRequester", requester)
        client = self._get_client(requester._requester_name)
        return is_worker_blocked(client, self._worker_name)

    def is_eligible(self, task_run: "TaskRun") -> bool:
        """
        Qualifications are handled primarily by MTurk, so if a worker is able to get
        through to be able to access the task, they should be eligible
        """
        # TODO check to see if the worker has exceeded the max number of
        # units for this assignment
        return True

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        return MTurkWorker._register_worker(db, worker_id, PROVIDER_TYPE)
