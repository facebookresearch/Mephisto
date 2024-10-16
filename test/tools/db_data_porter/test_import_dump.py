#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import tempfile
import unittest
from copy import deepcopy
from typing import ClassVar
from typing import Type
from unittest.mock import patch

import pytest
from mephisto.tools.db_data_porter.import_dump import import_table_imported_data_from_dump

from mephisto.tools.db_data_porter.import_dump import fill_imported_data_with_imported_dump

from mephisto.tools.db_data_porter.constants import DEFAULT_CONFLICT_RESOLVER
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.import_dump import import_single_db

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.db_data_porter.import_dump import _update_row_with_pks_from_resolvings_mappings
from mephisto.utils import db as db_utils


@pytest.mark.db_data_porter
class TestImportDump(unittest.TestCase):
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

    @patch("mephisto.utils.db.select_fk_mappings_for_single_table")
    def test__update_row_with_pks_from_resolvings_mappings(
        self,
        mock_select_fk_mappings_for_single_table,
        *args,
    ):
        mock_select_fk_mappings_for_single_table.return_value = {
            "requesters": {"from": "requester_id", "to": "requester_id"},
            "tasks": {"from": "task_id", "to": "task_id"},
        }

        existing_task_id = "2"
        resolved_task_id = "22"
        existing_requester_id = "3"

        row = {
            "task_run_id": "1",
            "task_id": existing_task_id,
            "requester_id": existing_requester_id,
            "init_params": "",
            "is_completed": 0,
            "provider_type": "mock",
            "task_type": "mock",
            "sandbox": 1,
            "creation_date": "2024-05-01 00:00:00.000",
        }

        resolvings_mapping = {
            "tasks": {
                existing_task_id: resolved_task_id,
            },
            "requesters": {},  # Nothing to update
        }

        exprcted_updated_row = deepcopy(row)
        exprcted_updated_row["task_id"] = resolved_task_id

        result = _update_row_with_pks_from_resolvings_mappings(
            self.db,
            "task_runs",
            row,
            resolvings_mapping,
        )

        self.assertEqual(result, exprcted_updated_row)

    def test_import_single_db_success(self, *args):
        label = "test_label"

        task_id = "1111111111111111111"
        requester_id = "2222222222222222222"
        task_run_id = "3333333333333333333"

        full_dump_data = {
            "mephisto": {
                "imported_data": [],
                "projects": [],
                "tasks": [
                    {
                        "task_id": task_id,
                        "task_name": "test_task",
                        "task_type": "mock",
                        "project_id": None,
                        "parent_task_id": None,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    }
                ],
                "requesters": [
                    {
                        "requester_id": requester_id,
                        "requester_name": "test_requester",
                        "provider_type": "mock",
                        "creation_date": "2024-05-01T00:00:00.000000",
                    }
                ],
                "task_runs": [
                    {
                        "task_run_id": task_run_id,
                        "task_id": task_id,
                        "requester_id": requester_id,
                        "init_params": "",
                        "is_completed": 0,
                        "provider_type": "mock",
                        "task_type": "mock",
                        "sandbox": 1,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    }
                ],
                "assignments": [],
                "units": [],
                "workers": [],
                "agents": [],
                "onboarding_agents": [],
                "qualifications": [],
                "granted_qualifications": [],
                "worker_review": [],
            },
            "mock": {"requesters": [], "units": [], "workers": []},
        }

        self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 0)
        self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 0)
        self.assertEqual(len(db_utils.select_all_table_rows(self.db, "requesters")), 0)

        result = import_single_db(
            db=self.db,
            dump_data=full_dump_data[MEPHISTO_DUMP_KEY],
            provider_type=MEPHISTO_DUMP_KEY,
            conflict_resolver_name=DEFAULT_CONFLICT_RESOLVER,
            labels=[label],
        )

        task_rows = db_utils.select_all_table_rows(self.db, "tasks")
        task_run_rows = db_utils.select_all_table_rows(self.db, "task_runs")
        requester_rows = db_utils.select_all_table_rows(self.db, "requesters")

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(task_rows), 1)
        self.assertEqual(len(task_run_rows), 1)
        self.assertEqual(len(requester_rows), 1)
        self.assertEqual(task_rows[0]["task_id"], task_id)
        self.assertEqual(task_run_rows[0]["task_run_id"], task_run_id)
        self.assertEqual(requester_rows[0]["requester_id"], requester_id)

    def test_import_single_db_pk_error(self, *args):
        label = "test_label"

        task_id = "1111111111111111111"
        requester_id = "2222222222222222222"
        task_run_id = "3333333333333333333"

        full_dump_data = {
            "mephisto": {
                "imported_data": [],
                "projects": [],
                "tasks": [
                    {
                        "task_id": task_id,
                        "task_name": "test_task",
                        "task_type": "mock",
                        "project_id": None,
                        "parent_task_id": None,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    }
                ],
                "requesters": [
                    {
                        "requester_id": requester_id,
                        "requester_name": "test_requester",
                        "provider_type": "mock",
                        "creation_date": "2024-05-01T00:00:00.000000",
                    }
                ],
                "task_runs": [
                    {
                        "task_run_id": task_run_id,
                        "task_id": task_id,
                        "requester_id": requester_id,
                        "init_params": "",
                        "is_completed": 0,
                        "provider_type": "mock",
                        "task_type": "mock",
                        "sandbox": 1,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    }
                ],
                "assignments": [],
                "units": [],
                "workers": [],
                "agents": [],
                "onboarding_agents": [],
                "qualifications": [],
                "granted_qualifications": [],
                "worker_review": [],
            },
            "mock": {"requesters": [], "units": [], "workers": []},
        }

        dump_data = full_dump_data[MEPHISTO_DUMP_KEY]
        db_utils.insert_new_row_in_table(self.db, "requesters", dump_data["requesters"][0])
        db_utils.insert_new_row_in_table(self.db, "tasks", dump_data["tasks"][0])
        db_utils.insert_new_row_in_table(self.db, "task_runs", dump_data["task_runs"][0])

        self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 1)
        self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 1)
        self.assertEqual(len(db_utils.select_all_table_rows(self.db, "requesters")), 1)

        result = import_single_db(
            db=self.db,
            dump_data=dump_data,
            provider_type=MEPHISTO_DUMP_KEY,
            conflict_resolver_name=DEFAULT_CONFLICT_RESOLVER,
            labels=[label],
        )

        task_rows = db_utils.select_all_table_rows(self.db, "tasks")
        task_run_rows = db_utils.select_all_table_rows(self.db, "task_runs")
        requester_rows = db_utils.select_all_table_rows(self.db, "requesters")

        self.assertEqual(len(result["errors"]), 1)
        self.assertIn(
            (
                "UNIQUE constraint failed: task_runs.task_run_id. "
                f"Local database already has Primary Key '{task_run_id}' in table 'task_runs'."
            ),
            result["errors"][0],
        )
        self.assertIn("Possible issue", result["errors"][0])
        self.assertEqual(len(task_rows), 1)
        self.assertEqual(len(task_run_rows), 1)
        self.assertEqual(len(requester_rows), 1)

    def test_fill_imported_data_with_imported_dump(self, *args):
        data_labels = '["test_label"]'
        imported_data = {
            "task_runs": {
                data_labels: [
                    {
                        "unique_field_names": ["task_run_id"],
                        "unique_field_values": ["3333333333333333333"],
                    }
                ],
                '["_", "test_label"]': [],
            },
        }
        source_file_name = "test_source_file_name"

        imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")

        self.assertEqual(len(imported_data_rows), 0)

        fill_imported_data_with_imported_dump(
            db=self.db,
            imported_data=imported_data,
            source_file_name=source_file_name,
        )

        imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")

        self.assertEqual(len(imported_data_rows), 1)
        self.assertEqual(imported_data_rows[0]["source_file_name"], source_file_name)
        self.assertEqual(imported_data_rows[0]["data_labels"], data_labels)
        self.assertEqual(imported_data_rows[0]["table_name"], "task_runs")
        self.assertEqual(imported_data_rows[0]["unique_field_names"], '["task_run_id"]')
        self.assertEqual(imported_data_rows[0]["unique_field_values"], '["3333333333333333333"]')

    def test_import_table_imported_data_from_dump_without_existing_row(self, *args):
        imported_data_rows = [
            {
                "id": 1,
                "source_file_name": "test_source_file_name",
                "data_labels": '["test_label"]',
                "table_name": "task_runs",
                "unique_field_names": '["task_run_id"]',
                "unique_field_values": '["3333333333333333333"]',
                "creation_date": "2024-05-01 00:00:00",
            }
        ]

        existing_imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")

        self.assertEqual(len(existing_imported_data_rows), 0)

        import_table_imported_data_from_dump(
            db=self.db,
            imported_data_rows=imported_data_rows,
        )

        created_imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")

        self.assertEqual(len(created_imported_data_rows), 1)
        self.assertEqual(
            created_imported_data_rows[0]["source_file_name"],
            imported_data_rows[0]["source_file_name"],
        )
        self.assertEqual(
            created_imported_data_rows[0]["data_labels"],
            imported_data_rows[0]["data_labels"],
        )
        self.assertEqual(
            created_imported_data_rows[0]["table_name"],
            imported_data_rows[0]["table_name"],
        )
        self.assertEqual(
            created_imported_data_rows[0]["unique_field_names"],
            imported_data_rows[0]["unique_field_names"],
        )
        self.assertEqual(
            created_imported_data_rows[0]["unique_field_values"],
            imported_data_rows[0]["unique_field_values"],
        )

    def test_import_table_imported_data_from_dump_with_existing_row(self, *args):
        importing_label = "test_label"
        imported_data_row = {
            "id": 1,
            "source_file_name": "test_source_file_name",
            "data_labels": f'["{importing_label}"]',
            "table_name": "task_runs",
            "unique_field_names": '["task_run_id"]',
            "unique_field_values": '["3333333333333333333"]',
            "creation_date": "2024-05-01 00:00:00",
        }
        imported_data_rows = [imported_data_row]

        existing_label = "existing_label"
        existing_source_file_name = "existing_source_file_name"
        existing_imported_data_row = deepcopy(imported_data_row)
        existing_imported_data_row["source_file_name"] = existing_source_file_name
        existing_imported_data_row["data_labels"] = f'["{existing_label}"]'

        db_utils.insert_new_row_in_table(self.db, "imported_data", existing_imported_data_row)

        existing_imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")

        self.assertEqual(len(existing_imported_data_rows), 1)

        import_table_imported_data_from_dump(
            db=self.db,
            imported_data_rows=imported_data_rows,
        )

        created_imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")

        self.assertEqual(len(created_imported_data_rows), 1)
        self.assertEqual(
            created_imported_data_rows[0]["source_file_name"],
            existing_source_file_name,
        )
        self.assertEqual(
            created_imported_data_rows[0]["data_labels"],
            f'["{existing_label}", "{importing_label}"]',
        )
        self.assertEqual(
            created_imported_data_rows[0]["table_name"],
            imported_data_rows[0]["table_name"],
        )
        self.assertEqual(
            created_imported_data_rows[0]["unique_field_names"],
            imported_data_rows[0]["unique_field_names"],
        )
        self.assertEqual(
            created_imported_data_rows[0]["unique_field_values"],
            imported_data_rows[0]["unique_field_values"],
        )
