#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mephisto.abstractions.architects.ec2.ec2_helpers as ec2_helpers
import boto3  # type: ignore
import os
import json

from typing import Dict, Any


# TODO Hydrize
def main():
    iam_role_name = input("Please enter local profile name for IAM role\n>> ")
    ec2_helpers.cleanup_fallback_server(iam_role_name)


if __name__ == "__main__":
    main()
