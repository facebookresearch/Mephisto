#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile
import time
import pytest

from mephisto.operations.config_handler import get_config_arg
from typing import Type
from mephisto.utils.testing import get_test_requester
from mephisto.abstractions.test.crowd_provider_tester import CrowdProviderTests
from mephisto.abstractions.crowd_provider import CrowdProvider
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_provider import (
    SandboxMTurkProvider,
)
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_requester import (
    SandboxMTurkRequester,
)
from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_worker import (
    SandboxMTurkWorker,
)

from mephisto.abstractions.providers.mturk.mturk_utils import (
    delete_qualification,
    find_qualification,
)


class TestSandboxMTurkCrowdProvider(CrowdProviderTests):
    """
    Unit testing for the SandboxMTurkCrowdProvider

    Requires setting up an account to be the tester,
    """

    CrowdProviderClass: Type[CrowdProvider] = SandboxMTurkProvider

    def get_test_worker_name(self) -> str:
        """Return a worker name that is usable for testing with this crowdprovider"""
        worker_id = get_config_arg("test", "mturk_worker_id")
        assert worker_id is not None, (
            "Test worker_id must be set with "
            "config_handler.add_config_arg('test', 'mturk_worker_id', '...')"
        )
        return worker_id

    def get_test_requester_name(self) -> str:
        """Return a requester name that is usable for testing with this crowdprovider"""
        # TODO(#97) this requester must be registered!!
        return "UNIT_TEST_REQUESTER"

    def get_test_requester_balance(self, worker_name: str) -> float:
        """Return the account balance we expect for a requester on sandbox"""
        return 10000

    @pytest.mark.req_creds
    def test_requester(self) -> None:
        super().test_requester()

    @pytest.mark.req_creds
    def test_worker(self) -> None:
        super().test_worker()

    @pytest.mark.req_creds
    def test_grant_and_revoke_qualifications(self) -> None:
        """Ensure we can grant and revoke qualifications for a worker"""
        db = self.db
        test_requester = SandboxMTurkRequester.new(db, self.get_test_requester_name())
        worker: SandboxMTurkWorker = SandboxMTurkWorker.new(  # type: ignore
            db, self.get_test_worker_name()
        )
        qualification_name = f"mephisto_test_qualification_{int(time.time())}"
        extended_qualification_name = f"{qualification_name}_sandbox"

        qual_mapping = worker.datastore.get_qualification_mapping(extended_qualification_name)
        self.assertIsNone(qual_mapping)

        mephisto_qual_id = db.make_qualification(qualification_name)

        self.assertTrue(worker.grant_qualification(qualification_name), "Qualification not granted")

        # ensure the qualification exists
        qual_mapping = worker.datastore.get_qualification_mapping(extended_qualification_name)
        self.assertIsNotNone(qual_mapping)
        assert qual_mapping is not None, "For typing, already asserted this isn't None"

        qualification_id = qual_mapping["mturk_qualification_id"]
        requester = SandboxMTurkRequester(db, qual_mapping["requester_id"])
        client = worker._get_client(requester._requester_name)

        def cleanup_qualification():
            try:
                delete_qualification(client, qual_mapping["mturk_qualification_id"])
            except:
                pass

        self.addCleanup(cleanup_qualification)

        self.assertTrue(
            worker.revoke_qualification(qualification_name), "Qualification not revoked"
        )

        owned, found_qual = find_qualification(client, qual_mapping["mturk_qualification_name"])
        start_time = time.time()
        while found_qual is None:
            time.sleep(1)
            owned, found_qual = find_qualification(client, qual_mapping["mturk_qualification_name"])
            self.assertFalse(
                time.time() - start_time > 20,
                "MTurk did not register qualification creation",
            )

        self.assertTrue(owned)
        self.assertIsNotNone(found_qual)
        self.assertEqual(found_qual, qualification_id)

        # TODO(#97) assert the worker does not have the qualification

        self.assertTrue(worker.grant_qualification(qualification_name), "Qualification not granted")

        # TODO(#97) assert that the worker has the qualification

        self.assertTrue(
            worker.revoke_qualification(qualification_name), "Qualification not revoked"
        )

        # TODO(#97) assert the worker no longer has the qualification again

        self.assertFalse(worker.revoke_qualification(qualification_name), "Can't revoke qual twice")

        db.delete_qualification(qualification_name)

        owned, found_qual = find_qualification(client, qual_mapping["mturk_qualification_name"])
        start_time = time.time()
        while found_qual is not None:
            time.sleep(1)
            owned, found_qual = find_qualification(client, qual_mapping["mturk_qualification_name"])
            self.assertFalse(
                time.time() - start_time > 20,
                "MTurk did not register qualification deletion",
            )


if __name__ == "__main__":
    unittest.main()
