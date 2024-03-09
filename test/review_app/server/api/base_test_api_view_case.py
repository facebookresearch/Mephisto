#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import tempfile
import unittest
from typing import ClassVar
from typing import Type

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.review_app.server import create_app


class BaseTestApiViewCase(unittest.TestCase):
    """Unit testing for the Mephisto TaskReview app"""

    DB_CLASS: ClassVar[Type["MephistoDB"]] = LocalMephistoDB

    def setUp(self):
        # Configure test database
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "test_mephisto.db")
        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)

        # Configure test Flask client
        app = create_app(debug=True, database_path=database_path)
        app.config.update(
            {
                "TESTING": True,
            }
        )
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        # Clean test database
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

        # Clean Flask app context
        self.app_context.pop()
