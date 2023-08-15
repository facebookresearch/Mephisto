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
from mephisto.tools.data_browser import DataBrowser
from mephisto.data_model.worker import Worker
from mephisto.utils.qualifications import find_or_create_qualification


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

    def get_named_test_worker(self, worker_name: str) -> Worker:
        """Create a test worker with the given worker name"""
        worker_id = self.db.new_worker(worker_name, "mock")
        return Worker.get(self.db, worker_id)

    def test_find_workers_by_quals(self) -> None:
        """Ensure we can find a worker by an assigned qualification"""
        db = self.db
        WORKER_1_NAME = "worker_1"
        WORKER_2_NAME = "worker_2"
        WORKER_3_NAME = "worker_3"
        QUAL_NAME = "test_qualification"
        worker_1 = self.get_named_test_worker(WORKER_1_NAME)
        worker_2 = self.get_named_test_worker(WORKER_2_NAME)
        worker_3 = self.get_named_test_worker(WORKER_3_NAME)

        find_or_create_qualification(db, QUAL_NAME)

        worker_1.grant_qualification(QUAL_NAME, skip_crowd=True)
        worker_3.grant_qualification(QUAL_NAME, skip_crowd=True)

        data_browser = DataBrowser(db)

        qualified_workers = data_browser.get_workers_with_qualification(QUAL_NAME)
        qualified_ids = [w.db_id for w in qualified_workers]
        self.assertEqual(
            len(qualified_workers),
            2,
            f"Should only be two qualified workers, found {qualified_ids}",
        )

        self.assertIn(
            worker_1.db_id,
            qualified_ids,
            f"Worker 1 not in qualified list, found {qualified_ids}",
        )
        self.assertIn(
            worker_3.db_id,
            qualified_ids,
            f"Worker 3 not in qualified list, found {qualified_ids}",
        )
        self.assertNotIn(worker_2.db_id, qualified_ids, "Worker 2 should not be in qualified list")


if __name__ == "__main__":
    unittest.main()
