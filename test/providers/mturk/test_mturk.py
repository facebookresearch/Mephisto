#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile
import time

from mephisto.core.local_database import LocalMephistoDB
from mephisto.providers.mturk.mturk_worker import MTurkWorker
from mephisto.data_model.worker import Worker


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

    def test_create_and_find_worker(self) -> None:
        """Ensure we can find a worker by MTurk id"""
        db = self.db
        TEST_MTURK_WORKER_ID = "ABCDEFGHIJ"

        test_worker = MTurkWorker.new(db, TEST_MTURK_WORKER_ID)
        test_worker_2 = Worker(db, test_worker.db_id)
        self.assertEqual(
            test_worker.worker_name,
            test_worker_2.worker_name,
            "Worker gotten from db not same as first init",
        )

        test_worker_3 = MTurkWorker.get_from_mturk_worker_id(db, TEST_MTURK_WORKER_ID)
        self.assertEqual(
            test_worker.worker_name,
            test_worker_3.worker_name,
            "Worker gotten from db not same as first init",
        )

        failed_worker = MTurkWorker.get_from_mturk_worker_id(db, "FAKE_ID")
        self.assertIsNone(failed_worker, f"Found worker {failed_worker} from a fake id")

if __name__ == "__main__":
    unittest.main()
