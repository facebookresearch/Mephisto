#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.requester import Requester
from mephisto.providers.mturk.mturk_utils import (
    setup_aws_credentials,
    get_requester_balance,
)
from mephisto.providers.mturk.provider_type import PROVIDER_TYPE

from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from mephisto.providers.mturk.mturk_datastore import MTurkDatastore


class MTurkRequester(Requester):
    """
    Wrapper for requester behavior as provided by MTurk. Makes
    all requests directly to MTurk through boto3.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            PROVIDER_TYPE
        )
        # Use _requester_name to preserve sandbox behavior which
        # utilizes a different requester_name
        self._requester_name = self.requester_name

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    def is_sandbox(self) -> bool:
        """
        Determine if this is a requester on sandbox
        """
        # Regular requesters are never sandbox requesters
        return False

    # Required functions for a Requester implementation

    def register_credentials(self) -> None:
        """Try to register credentials for the given requester"""
        setup_aws_credentials(self._requester_name)

    def get_available_budget(self) -> float:
        """Get the available budget from MTurk"""
        client = self._get_client(self._requester_name)
        return get_requester_balance(client)

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return MTurkRequester._register_requester(db, requester_name, PROVIDER_TYPE)
