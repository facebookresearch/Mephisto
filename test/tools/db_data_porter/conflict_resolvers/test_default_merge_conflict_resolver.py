#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime
from typing import ClassVar
from typing import Type

import pytest

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.db_data_porter.conflict_resolvers.default_merge_conflict_resolver import (
    DefaultMergeConflictResolver,
)


@pytest.mark.db_data_porter
class TestDefaultMergeConflictResolver(unittest.TestCase):
    DB_CLASS: ClassVar[Type["MephistoDB"]] = LocalMephistoDB

    def setUp(self):
        # Configure test database
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "test_mephisto.db")

        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)

        # Init conflict resolver instance
        self.conflict_resolver = DefaultMergeConflictResolver(self.db, "mephisto")

    def tearDown(self):
        # Clean test database
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_resolve_with_default(self, *args):
        db_row = {
            "project_id": 1,
            "project_name": "test_project_name",
            "creation_date": "2001-01-01 01:01:01.001",
        }
        dump_row = {
            "project_id": 2,
            "project_name": "test_project_name",
            "creation_date": "1999-01-01 01:01:01.001",
        }
        expecting_result = deepcopy(db_row)
        # Earlier data from two
        expecting_result["creation_date"] = datetime(1999, 1, 1, 1, 1, 1, 1000)

        result = self.conflict_resolver.resolve(
            table_name="project",
            table_pk_field_name="project_id",
            db_row=db_row,
            dump_row=dump_row,
        )

        self.assertEqual(result, expecting_result)

    def test_resolve_with_granted_qualifications(self, *args):
        db_row = {
            "granted_qualification_id": 1,
            "qualification_id": 1,
            "worker_id": 1,
            "value": 999,
            "creation_date": "2001-01-01 01:01:01.001",
            "update_date": "1999-01-01 01:01:01.001",
        }
        dump_row = {
            "granted_qualification_id": 2,
            "qualification_id": 1,
            "worker_id": 1,
            "value": 1,
            "creation_date": "1999-01-01 01:01:01.001",
            "update_date": "2001-01-01 01:01:01.001",
        }
        expecting_result = deepcopy(dump_row)
        # Original id
        expecting_result["granted_qualification_id"] = db_row["granted_qualification_id"]
        # Earlier data from two
        expecting_result["creation_date"] = datetime(1999, 1, 1, 1, 1, 1, 1000)
        # Greater data from two
        expecting_result["update_date"] = datetime(2001, 1, 1, 1, 1, 1, 1000)

        result = self.conflict_resolver.resolve(
            table_name="granted_qualifications",
            table_pk_field_name="granted_qualification_id",
            db_row=db_row,
            dump_row=dump_row,
        )

        self.assertEqual(result, expecting_result)

    def test_resolve_with_workers(self, *args):
        db_row = {
            "worker_id": 1,
            "worker_name": "test_worker_name",
            "is_blocked": 0,  # False
            "creation_date": "2001-01-01 01:01:01.001",
        }
        dump_row = {
            "worker_id": 2,
            "worker_name": "test_worker_name",
            "is_blocked": 1,  # True
            "creation_date": "1999-01-01 01:01:01.001",
        }
        expecting_result = deepcopy(dump_row)
        # Original id
        expecting_result["worker_id"] = db_row["worker_id"]
        # Blocked one
        expecting_result["is_blocked"] = dump_row["is_blocked"]
        # Earlier data from two
        expecting_result["creation_date"] = datetime(1999, 1, 1, 1, 1, 1, 1000)

        # Simulate Prolific datastore
        result = DefaultMergeConflictResolver(self.db, "prolific").resolve(
            table_name="workers",
            table_pk_field_name="worker_id",
            db_row=db_row,
            dump_row=dump_row,
        )

        self.assertEqual(result, expecting_result)
