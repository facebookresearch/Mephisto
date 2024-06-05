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

import pytest

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.validation import validate_dump_data


@pytest.mark.db_data_porter
class TestValidation(unittest.TestCase):
    DB_CLASS: ClassVar[Type["MephistoDB"]] = LocalMephistoDB

    def setUp(self):
        # Configure test database
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "test_mephisto.db")

        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)

    def tearDown(self):
        # Clean test database
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_validate_dump_data_incorrect_provider_name(self, *args):
        incorrect_provider_name = "incorrect_provider"
        dump_data = {
            incorrect_provider_name: {},
        }

        result = validate_dump_data(db=self.db, dump_data=dump_data)

        self.assertEqual(
            result,
            [f"Dump file cannot contain these database names: {incorrect_provider_name}."],
        )

    def test_validate_dump_data_db_values_are_not_dicts(self, *args):
        dump_data = {
            MEPHISTO_DUMP_KEY: [],
        }

        result = validate_dump_data(db=self.db, dump_data=dump_data)

        self.assertEqual(
            result,
            ["We found 1 values in the dump that are not JSON-objects."],
        )

    def test_validate_dump_data_incorrect_format_table_name(self, *args):
        table_name = 1
        dump_data = {
            MEPHISTO_DUMP_KEY: {
                table_name: [],
            },
        }

        result = validate_dump_data(db=self.db, dump_data=dump_data)

        self.assertEqual(
            result,
            [
                f"Expecting table name to be a string, not `{table_name}`.",
                (
                    f"Your local `{MEPHISTO_DUMP_KEY}` database does not have table '{table_name}'."
                    f" Possible issues:\n"
                    "        - local database has unapplied migrations\n"
                    "        - dump is too old and not compatible to your local database"
                ),
            ],
        )

    def test_validate_dump_data_incorrect_format_table_rows(self, *args):
        table_rows = "1"
        dump_data = {
            MEPHISTO_DUMP_KEY: {
                "tasks": table_rows,
            },
        }

        result = validate_dump_data(db=self.db, dump_data=dump_data)

        self.assertEqual(
            result,
            [
                f"Expecting table data to be a JSON-array, not `{table_rows}`.",
                f"Table `tasks`, row 0: expecting it to be a JSON-object, not `{table_rows}`.",
            ],
        )

    def test_validate_dump_data_incorrect_format_field_name(self, *args):
        field_name = 1
        dump_data = {
            MEPHISTO_DUMP_KEY: {
                "tasks": [
                    {field_name: ""},
                ],
            },
        }

        result = validate_dump_data(db=self.db, dump_data=dump_data)

        self.assertEqual(
            result,
            [f"Table `tasks`, row 1: names of these fields must be strings: {field_name}."],
        )

    def test_validate_dump_data_success(self, *args):
        dump_data = {
            MEPHISTO_DUMP_KEY: {
                "tasks": [
                    {
                        "task_id": "1",
                        "task_anem": "test",
                    },
                ],
            },
        }

        result = validate_dump_data(db=self.db, dump_data=dump_data)

        self.assertEqual(result, [])
