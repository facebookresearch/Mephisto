#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mephisto.abstractions.architects.ec2.ec2_helpers as ec2_helpers
import boto3  # type: ignore
import os

from mephisto.abstractions.architects.ec2.ec2_helpers import (
    DEFAULT_FALLBACK_FILE,
    DEFAULT_SERVER_DETAIL_LOCATION,
)
from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


# TODO Hydrize
def main():
    all_server_names = [
        os.path.splitext(s)[0]
        for s in os.listdir(DEFAULT_SERVER_DETAIL_LOCATION)
        if s not in ["README.md", os.path.basename(DEFAULT_FALLBACK_FILE)]
    ]

    if len(all_server_names) == 0:
        logger.warning("No server to clean up!")
        return

    server_name = input(
        f"Please enter server name you want to clean up (existing servers: {all_server_names})\n>> "
    )
    assert (
        os.path.join(DEFAULT_SERVER_DETAIL_LOCATION, f"{server_name}.json")
        != DEFAULT_FALLBACK_FILE
    ), "This is going to completely delete the fallback server for your EC2 architect."
    assert server_name in all_server_names, f"{server_name} does not exist"

    iam_role_name = input("Please enter local profile name for IAM role\n>> ")

    session = boto3.Session(profile_name=iam_role_name, region_name="us-east-2")
    ec2_helpers.remove_instance_and_cleanup(session, server_name)


if __name__ == "__main__":
    main()
