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

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.mturk.mturk_worker import MTurkWorker
from mephisto.data_model.worker import Worker

from typing import cast


class TestMTurkComponents(unittest.TestCase):
    """
    Unit testing for components of the MTurk crowd provider
    """

    def setUp(self) -> None:
        """
        Initialize a temporary database
        """
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)

    def tearDown(self) -> None:
        """
        Delete the temporary database
        """
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    @pytest.mark.req_creds
    def test_create_and_find_worker(self) -> None:
        """Ensure we can find a worker by MTurk id"""
        db = self.db
        TEST_MTURK_WORKER_ID = "ABCDEFGHIJ"

        test_worker = MTurkWorker.new(db, TEST_MTURK_WORKER_ID)
        test_worker_2 = Worker.get(db, test_worker.db_id)
        self.assertEqual(
            test_worker.worker_name,
            test_worker_2.worker_name,
            "Worker gotten from db not same as first init",
        )

        test_worker_3 = MTurkWorker.get_from_mturk_worker_id(db, TEST_MTURK_WORKER_ID)
        assert test_worker_3 is not None
        self.assertEqual(
            test_worker.worker_name,
            test_worker_3.worker_name,
            "Worker gotten from db not same as first init",
        )

        failed_worker = MTurkWorker.get_from_mturk_worker_id(db, "FAKE_ID")
        self.assertIsNone(failed_worker, f"Found worker {failed_worker} from a fake id")

    def test_mturk_qual_create_mapping(self) -> None:
        """Ensure that qualification creation is idempotent, loosely"""
        db = self.db
        TEST_MTURK_WORKER_ID = "ABCDEFGHIJ"

        test_worker = cast(MTurkWorker, MTurkWorker.new(db, TEST_MTURK_WORKER_ID))

        datastore = test_worker.datastore
        qualification_name = "test-qual-name"
        requester_id = "test-requester-id"
        mturk_qualification_name = "test-requester-name"
        mturk_qualification_id = "test-qualification-id"

        # test store and retrieve
        datastore.create_qualification_mapping(
            qualification_name,
            requester_id,
            mturk_qualification_name,
            mturk_qualification_id,
        )

        stored_qual = datastore.get_qualification_mapping(qualification_name)
        assert stored_qual is not None, "We just created this qualification!"
        self.assertEqual(
            stored_qual["qualification_name"],
            qualification_name,
            "Stored did not have same name",
        )
        self.assertEqual(
            stored_qual["requester_id"],
            requester_id,
            "Stored did not have same requester",
        )
        self.assertEqual(
            stored_qual["mturk_qualification_name"],
            mturk_qualification_name,
            "Stored did not have same mturk name",
        )
        self.assertEqual(
            stored_qual["mturk_qualification_id"],
            mturk_qualification_id,
            "Stored did not have same mturk id",
        )

        # Test idempotency
        datastore.create_qualification_mapping(
            qualification_name,
            requester_id,
            mturk_qualification_name,
            mturk_qualification_id,
        )

        # Test near-idempotency (with warning)
        datastore.create_qualification_mapping(
            qualification_name,
            requester_id + "-but-not-really",
            mturk_qualification_name + "-but-not-really",
            mturk_qualification_id,
        )

        # Test empty load
        self.assertIsNone(datastore.get_qualification_mapping("fake_id"))


if __name__ == "__main__":
    unittest.main()
