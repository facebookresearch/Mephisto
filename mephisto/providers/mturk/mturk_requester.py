#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.requester import Requester
from mephisto.providers.mturk.mturk_utils import (
    setup_aws_credentials,
    get_requester_balance,
    check_aws_credentials,
)
from mephisto.providers.mturk.provider_type import PROVIDER_TYPE

from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from mephisto.providers.mturk.mturk_datastore import MTurkDatastore


class MTurkRequester(Requester):
    """
    Wrapper for requester behavior as provided by MTurk. Makes
    all requests directly to MTurk through boto3.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        # Use _requester_name to preserve sandbox behavior which
        # utilizes a different requester_name
        self._requester_name = self.requester_name

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    # Required functions for a Requester implementation

    def register(self, args: Optional[Dict[str, str]] = None) -> None:
        """
        Register this requester with the crowd provider by providing any required credentials
        or such. If no args are provided, assume the registration is already made and try
        to assert it as such.
        """
        setup_aws_credentials(self._requester_name, args)

    def is_registered(self) -> bool:
        """Return whether or not this requester has registered yet"""
        return check_aws_credentials(self._requester_name)

    @staticmethod
    def get_register_args() -> Dict[str, str]:
        """Get the args required to register this requester to the crowd provider"""
        return {
            "HELP_TEXT": "AWS are required to create a new Requester. Please create "
            "an IAM user with "
            "programmatic access and AdministratorAccess policy at "
            'https://console.aws.amazon.com/iam/ (On the "Set permissions" '
            'page, choose "Attach existing policies directly" and then select '
            '"AdministratorAccess" policy). After creating the IAM user, '
            "please enter the user's Access Key ID and Secret Access Key.",
            "access_key_id": "IAM Access Key ID: ",
            "secret_access_key": "IAM Secret Access Key: ",
        }

    def get_available_budget(self) -> float:
        """Get the available budget from MTurk"""
        client = self._get_client(self._requester_name)
        return get_requester_balance(client)

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return MTurkRequester._register_requester(db, requester_name, PROVIDER_TYPE)
