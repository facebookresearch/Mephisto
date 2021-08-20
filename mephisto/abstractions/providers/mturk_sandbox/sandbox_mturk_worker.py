#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.mturk.mturk_worker import MTurkWorker
from mephisto.abstractions.providers.mturk_sandbox.provider_type import PROVIDER_TYPE

from typing import Any, Mapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.providers.mturk.mturk_datastore import MTurkDatastore
    from mephisto.data_model.worker import Worker
    from mephisto.abstractions.database import MephistoDB


class SandboxMTurkWorker(MTurkWorker):
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
        # sandbox workers use a different name
        self._worker_name = self.worker_name[:-8]

    def grant_crowd_qualification(
        self, qualification_name: str, value: int = 1
    ) -> None:
        """
        Grant a qualification by the given name to this worker. Check the local
        MTurk db to find the matching MTurk qualification to grant, and pass
        that. If no qualification exists, try to create one.
        """
        return super().grant_crowd_qualification(qualification_name + "_sandbox", value)

    def revoke_crowd_qualification(self, qualification_name: str) -> None:
        """
        Revoke the qualification by the given name from this worker. Check the local
        MTurk db to find the matching MTurk qualification to revoke, pass if
        no such qualification exists.
        """
        return super().revoke_crowd_qualification(qualification_name + "_sandbox")

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_sandbox_client_for_requester(requester_name)

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        return MTurkWorker._register_worker(db, worker_id + "_sandbox", PROVIDER_TYPE)
