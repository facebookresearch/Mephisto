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
    from argparse import _ArgumentGroup as ArgumentGroup


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
        for req_field in ["access_key_id", "secret_access_key"]:
            if args is not None and req_field not in args:
                raise Exception(
                    f'Missing IAM "{req_field}" in requester registration args'
                )
        setup_aws_credentials(self._requester_name, args)

    def is_registered(self) -> bool:
        """Return whether or not this requester has registered yet"""
        return check_aws_credentials(self._requester_name)

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Add mturk registration arguments to the argument group.
        """
        super(MTurkRequester, cls).add_args_to_group(group)

        group.description = """
            MTurkRequester: AWS are required to create a new Requester.
            Please create an IAM user with programmatic access and
            AmazonMechanicalTurkFullAccess policy at
            'https://console.aws.amazon.com/iam/ (On the "Set permissions"
            page, choose "Attach existing policies directly" and then select
            "AmazonMechanicalTurkFullAccess" policy). After creating
            the IAM user, you should get an Access Key ID
            and Secret Access Key.
        """
        group.add_argument(
            "--access-key-id", dest="access_key_id", help="IAM Access Key ID"
        )
        group.add_argument(
            "--secret-access-key",
            dest="secret_access_key",
            help="IAM Secret Access Key",
        )
        return

    def get_available_budget(self) -> float:
        """Get the available budget from MTurk"""
        client = self._get_client(self._requester_name)
        return get_requester_balance(client)

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return MTurkRequester._register_requester(db, requester_name, PROVIDER_TYPE)
