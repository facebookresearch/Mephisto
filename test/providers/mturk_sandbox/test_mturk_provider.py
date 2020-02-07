#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from typing import Type
from mephisto.data_model.test.crowd_provider_tester import CrowdProviderTests
from mephisto.data_model.crowd_provider import CrowdProvider
from mephisto.providers.mturk_sandbox.sandbox_mturk_provider import SandboxMTurkProvider


class TestSandboxMTurkCrowdProvider(CrowdProviderTests):
    """
    Unit testing for the SandboxMTurkCrowdProvider

    Requires setting up an account to be the tester,
    """

    CrowdProviderClass: Type[CrowdProvider] = SandboxMTurkProvider

    def get_test_worker_name(self) -> str:
        """Return a worker name that is usable for testing with this crowdprovider"""
        # TODO get this from somewhere else!
        return "ALNAP8V96IIO0"

    def get_test_requester_name(self) -> str:
        """Return a requester name that is usable for testing with this crowdprovider"""
        # TODO this requester must be registered!!
        return "UNIT_TEST_REQUESTER"

    def get_test_requester_balance(self, worker_name: str) -> float:
        """Return the account balance we expect for a requester on sandbox"""
        return 10000

    # TODO are there any other unit tests we'd like to have?


if __name__ == "__main__":
    unittest.main()
