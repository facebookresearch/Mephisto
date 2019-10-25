#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from mephisto.data_model.test.data_model_database_tester import BaseDatabaseTests
from mephisto.core.local_database import LocalMephistoDB


class TestLocalMephistoDB(BaseDatabaseTests):
    """
    Unit testing for the LocalMephistoDB

    Inherits all tests directly from BaseDataModelTests, and
    writes no additional tests.
    """

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)

    def tearDown(self):
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    # TODO are there any other unit tests we'd like to have?


if __name__ == "__main__":
    unittest.main()
