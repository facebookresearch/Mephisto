#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Optional

import surge
from surge.errors import SurgeMissingAPIKeyError
from surge.errors import SurgeRequestError

from mephisto.utils.logger_core import get_logger

SURGE_AI_BUDGET = 100000.0

logger = get_logger(name=__name__)

surge.api_key = os.environ.get('SURGE_API_KEY', 'dev')


def check_credentials() -> bool:
    """Check whether API KEY is correct"""
    try:
        # Make a simple request to the API
        surge.Project.list(page=1)
        return True
    except (SurgeMissingAPIKeyError, SurgeRequestError) as e:
        return False


def check_balance(balance_needed: Optional[float] = None):
    """
    Checks to see if there is at least balance_needed amount in the
    requester account, returns True if the balance is greater than
    balance_needed
    """
    # TODO: Change this later.
    #  Surge AI does not return account budget, so we always return positive value
    return SURGE_AI_BUDGET
