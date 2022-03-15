#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.worker import Worker
from mephisto.data_model.requester import Requester
from mephisto.abstractions.providers.mturk.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.mturk.mturk_utils import (
    pay_bonus,
    block_worker,
    unblock_worker,
    is_worker_blocked,
    give_worker_qualification,
    remove_worker_qualification,
)
from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester

from uuid import uuid4

from typing import List, Optional, Tuple, Dict, Mapping, Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.providers.mturk.mturk_datastore import MTurkDatastore
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.providers.mturk.mturk_unit import MTurkUnit
    from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class MTurkWorker(Worker):
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
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
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        self._worker_name = self.worker_name  # sandbox workers use a different name

    @classmethod
    def get_from_mturk_worker_id(
        cls, db: "MephistoDB", mturk_worker_id: str
    ) -> Optional["MTurkWorker"]:
        """Get the MTurkWorker from the given worker_id"""
        if cls.PROVIDER_TYPE != PROVIDER_TYPE:
            mturk_worker_id += "_sandbox"
        workers = db.find_workers(
            worker_name=mturk_worker_id, provider_type=cls.PROVIDER_TYPE
        )
        if len(workers) == 0:
            logger.warning(
                f"Could not find a Mephisto Worker for mturk_id {mturk_worker_id}"
            )
            return None
        return cast("MTurkWorker", workers[0])

    def get_mturk_worker_id(self):
        return self._worker_name

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    def grant_crowd_qualification(
        self, qualification_name: str, value: int = 1
    ) -> None:
        """
        Grant a qualification by the given name to this worker. Check the local
        MTurk db to find the matching MTurk qualification to grant, and pass
        that. If no qualification exists, try to create one.

        In creating a new qualification, Mephisto resolves the ambiguity over which
        requester to associate that qualification with by using the FIRST requester
        of the given account type (either `mturk` or `mturk_sandbox`)
        """
        mturk_qual_details = self.datastore.get_qualification_mapping(
            qualification_name
        )
        if mturk_qual_details is not None:
            requester = Requester.get(self.db, mturk_qual_details["requester_id"])
            qualification_id = mturk_qual_details["mturk_qualification_id"]
        else:
            target_type = (
                "mturk_sandbox" if qualification_name.endswith("sandbox") else "mturk"
            )
            requester = self.db.find_requesters(provider_type=target_type)[-1]
            assert isinstance(
                requester, MTurkRequester
            ), "find_requesters must return mturk requester for given provider types"
            qualification_id = requester._create_new_mturk_qualification(
                qualification_name
            )
        assert isinstance(
            requester, MTurkRequester
        ), "Must be an MTurk requester for MTurk quals"
        client = self._get_client(requester._requester_name)
        give_worker_qualification(
            client, self.get_mturk_worker_id(), qualification_id, value
        )
        return None

    def revoke_crowd_qualification(self, qualification_name: str) -> None:
        """
        Revoke the qualification by the given name from this worker. Check the local
        MTurk db to find the matching MTurk qualification to revoke, pass if
        no such qualification exists.
        """
        mturk_qual_details = self.datastore.get_qualification_mapping(
            qualification_name
        )
        if mturk_qual_details is None:
            logger.error(
                f"No locally stored MTurk qualification to revoke for name {qualification_name}"
            )
            return None

        requester = Requester.get(self.db, mturk_qual_details["requester_id"])
        assert isinstance(
            requester, MTurkRequester
        ), "Must be an MTurk requester from MTurk quals"
        client = self._get_client(requester._requester_name)
        qualification_id = mturk_qual_details["mturk_qualification_id"]
        remove_worker_qualification(
            client, self.get_mturk_worker_id(), qualification_id
        )
        return None

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional["Unit"] = None
    ) -> Tuple[bool, str]:
        """Bonus this worker for work any reason. Return tuple of success and failure message"""
        if unit is None:
            # TODO(#652) implement. The content in scripts/mturk/launch_makeup_hits.py
            # may prove useful for this.
            return False, "bonusing via compensation tasks not yet available"

        unit = cast("MTurkUnit", unit)
        requester = cast(
            "MTurkRequester", unit.get_assignment().get_task_run().get_requester()
        )
        client = self._get_client(requester._requester_name)
        mturk_assignment_id = unit.get_mturk_assignment_id()
        assert mturk_assignment_id is not None, "Cannot bonus for a unit with no agent"
        pay_bonus(
            client, self._worker_name, amount, mturk_assignment_id, reason, str(uuid4())
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
            # TODO(WISH) soft block from all requesters? Maybe have the main
            # requester soft block?
            return (
                False,
                "Blocking without a unit or requester not yet supported for MTurkWorkers",
            )
        elif unit is not None and requester is None:
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
        return True

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        return MTurkWorker._register_worker(db, worker_id, PROVIDER_TYPE)
