#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from uuid import uuid4
import time
import random

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.data_model.requester import Requester, RequesterArgs
from mephisto.abstractions.providers.mturk.mturk_utils import (
    setup_aws_credentials,
    get_requester_balance,
    check_aws_credentials,
    find_or_create_qualification as find_or_create_mturk_qualification,
)
from mephisto.abstractions.providers.mturk.provider_type import PROVIDER_TYPE

from typing import List, Optional, Mapping, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.providers.mturk.mturk_datastore import MTurkDatastore
    from argparse import _ArgumentGroup as ArgumentGroup


MAX_QUALIFICATION_ATTEMPTS = 300


@dataclass
class MTurkRequesterArgs(RequesterArgs):
    _group: str = field(
        default="MTurkRequester",
        metadata={
            "help": (
                "AWS is required to create a new Requester. "
                "Please create an IAM user with programmatic access and "
                "AmazonMechanicalTurkFullAccess policy at "
                'https://console.aws.amazon.com/iam/ (On the "Set permissions" '
                'page, choose "Attach existing policies directly" and then select '
                '"AmazonMechanicalTurkFullAccess" policy). After creating '
                "the IAM user, you should get an Access Key ID "
                "and Secret Access Key. "
            )
        },
    )
    access_key_id: str = field(
        default=MISSING, metadata={"required": True, "help": "IAM Access Key ID"}
    )
    secret_access_key: str = field(
        default=MISSING, metadata={"required": True, "help": "IAM Secret Access Key"}
    )


class MTurkRequester(Requester):
    """
    Wrapper for requester behavior as provided by MTurk. Makes
    all requests directly to MTurk through boto3.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE
    ArgsClass = MTurkRequesterArgs

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
        # Use _requester_name to preserve sandbox behavior which
        # utilizes a different requester_name
        self._requester_name = self.requester_name

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    # Required functions for a Requester implementation

    def register(self, args: Optional[DictConfig] = None) -> None:
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

    def get_available_budget(self) -> float:
        """Get the available budget from MTurk"""
        client = self._get_client(self._requester_name)
        return get_requester_balance(client)

    def _create_new_mturk_qualification(self, qualification_name: str) -> str:
        """
        Create a new qualification on MTurk owned by the requester provided
        """
        client = self._get_client(self._requester_name)
        qualification_desc = f"Equivalent qualification for {qualification_name}."
        use_qualification_name = qualification_name
        qualification_id = find_or_create_mturk_qualification(
            client, qualification_name, qualification_desc, must_be_owned=True
        )
        if qualification_id is None:
            # Try to append time to make the qualification unique
            use_qualification_name = f"{qualification_name}_{time.time()}"
            qualification_id = find_or_create_mturk_qualification(
                client, use_qualification_name, qualification_desc, must_be_owned=True
            )
            attempts = 0
            while qualification_id is None:
                # Append something somewhat random
                use_qualification_name = f"{qualification_name}_{str(uuid4())}"
                qualification_id = find_or_create_mturk_qualification(
                    client,
                    use_qualification_name,
                    qualification_desc,
                    must_be_owned=True,
                )
                attempts += 1
                if attempts > MAX_QUALIFICATION_ATTEMPTS:
                    raise Exception(
                        "Something has gone extremely wrong with creating qualification "
                        f"{qualification_name} for requester {self.requester_name}"
                    )
        # Store the new qualification in the datastore
        self.datastore.create_qualification_mapping(
            qualification_name, self.db_id, use_qualification_name, qualification_id
        )
        return qualification_id

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return MTurkRequester._register_requester(db, requester_name, PROVIDER_TYPE)
