#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.providers.mturk.mturk_worker import MTurkWorker
from mephisto.providers.mturk_sandbox.provider_type import PROVIDER_TYPE

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.providers.mturk.mturk_datastore import MTurkDatastore
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.database import MephistoDB


class SandboxMTurkWorker(MTurkWorker):
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
        # sandbox workers use a different name
        self._worker_name = self.worker_name[:-8]

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_sandbox_client_for_requester(requester_name)

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        return MTurkWorker._register_worker(db, worker_id + "_sandbox", PROVIDER_TYPE)
