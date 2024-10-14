#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import sqlite3
import tempfile
import unittest
from datetime import timedelta
from typing import ClassVar
from typing import Type
from unittest.mock import patch

import pytest

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import is_unique_failure
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.mock.mock_datastore import MockDatastore
from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.utils import db as db_utils
from mephisto.utils.db import EntryAlreadyExistsException
from mephisto.utils.misc import serialize_date_to_python
from mephisto.utils.testing import get_test_assignment
from mephisto.utils.testing import get_test_project
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_requester
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_unit
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from mephisto.utils.testing import make_completed_unit


@pytest.mark.utils
class TestUtilsDB(unittest.TestCase):
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

    def test__select_rows_from_table_related_to_task(self, *args):
        task_1_name = "task_1"
        task_2_name = "task_2"

        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_1_name)
        _, task_2_id = get_test_task(self.db, task_2_name)
        get_test_task_run(self.db, task_1_id, requester_id)
        get_test_task_run(self.db, task_2_id, requester_id)
        get_test_task_run(self.db, task_2_id, requester_id)

        rows_for_task_1 = db_utils._select_rows_from_table_related_to_task(
            self.db,
            "task_runs",
            [task_1_id],
        )
        rows_for_task_2 = db_utils._select_rows_from_table_related_to_task(
            self.db,
            "task_runs",
            [task_2_id],
        )

        self.assertEqual(len(rows_for_task_1), 1)
        self.assertEqual(len(rows_for_task_2), 2)

    def test_select_rows_from_table_related_to_task_run(self, *args):
        task_1_name = "task_1"
        task_2_name = "task_2"

        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_1_name)
        _, task_2_id = get_test_task(self.db, task_2_name)
        task_run_1_id = get_test_task_run(self.db, task_1_id, requester_id)
        task_run_2_id = get_test_task_run(self.db, task_2_id, requester_id)

        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        get_test_assignment(self.db, task_run_1)
        get_test_assignment(self.db, task_run_1)
        get_test_assignment(self.db, task_run_2)

        rows_for_task_run_1 = db_utils.select_rows_from_table_related_to_task_run(
            self.db,
            "assignments",
            [task_run_1_id],
        )
        rows_for_task_run_2 = db_utils.select_rows_from_table_related_to_task_run(
            self.db,
            "assignments",
            [task_run_2_id],
        )

        self.assertEqual(len(rows_for_task_run_1), 2)
        self.assertEqual(len(rows_for_task_run_2), 1)

    def test_serialize_data_for_table(self, *args):
        task_id = "111111111111111111"
        task_name = "task_1"
        task_type = "mock"
        rows = [
            {
                "task_id": task_id,
                "task_name": task_name,
                "task_type": task_type,
                "project_id": None,
                "parent_task_id": None,
                "creation_date": "2001-01-01 01:01:01.001",
            },
        ]

        serialized_rows = db_utils.serialize_data_for_table(rows)

        self.assertEqual(
            serialized_rows,
            [
                {
                    "task_id": task_id,
                    "task_name": task_name,
                    "task_type": task_type,
                    "project_id": None,
                    "parent_task_id": None,
                    "creation_date": "2001-01-01T01:01:01.001000",
                },
            ],
        )

    def test_make_randomized_int_id(self, *args):
        value_1 = db_utils.make_randomized_int_id()
        value_2 = db_utils.make_randomized_int_id()

        self.assertNotEqual(value_1, value_2)
        self.assertGreater(value_1, db_utils.SQLITE_ID_MIN)
        self.assertGreater(value_2, db_utils.SQLITE_ID_MIN)
        self.assertLess(value_1, db_utils.SQLITE_ID_MAX)
        self.assertLess(value_2, db_utils.SQLITE_ID_MAX)

    def test_get_task_ids_by_task_names(self, *args):
        task_1_name = "task_1"
        task_2_name = "task_2"

        _, task_1_id = get_test_task(self.db, task_1_name)
        _, task_2_id = get_test_task(self.db, task_2_name)

        task_ids = db_utils.get_task_ids_by_task_names(self.db, [task_1_name, task_2_name])

        self.assertEqual(task_ids, [task_1_id, task_2_id])

    def test_get_task_run_ids_by_task_ids(self, *args):
        task_1_name = "task_1"
        task_2_name = "task_2"

        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_1_name)
        _, task_2_id = get_test_task(self.db, task_2_name)
        task_run_1_id = get_test_task_run(self.db, task_1_id, requester_id)
        task_run_2_id = get_test_task_run(self.db, task_2_id, requester_id)
        task_run_3_id = get_test_task_run(self.db, task_2_id, requester_id)

        task_run_ids = db_utils.get_task_run_ids_by_task_ids(self.db, [task_1_id, task_2_id])

        self.assertEqual(
            sorted(task_run_ids),
            sorted([task_run_1_id, task_run_2_id, task_run_3_id]),
        )

    def test_get_task_run_ids_ids_by_labels(self, *args):
        test_label = "test_label"

        task_1_name = "task_1"
        task_2_name = "task_2"

        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_1_name)
        _, task_2_id = get_test_task(self.db, task_2_name)
        task_run_1_id = get_test_task_run(self.db, task_1_id, requester_id)
        task_run_2_id = get_test_task_run(self.db, task_2_id, requester_id)
        task_run_3_id = get_test_task_run(self.db, task_2_id, requester_id)

        db_utils.insert_new_row_in_table(
            db=self.db,
            table_name="imported_data",
            row=dict(
                source_file_name="test",
                data_labels=f'["{test_label}"]',
                table_name="task_runs",
                unique_field_names='["task_run_id"]',
                unique_field_values=f'["{task_run_1_id}", "{task_run_3_id}"]',
            ),
        )

        task_run_ids = db_utils.get_task_run_ids_by_labels(self.db, [test_label])

        self.assertEqual(sorted(task_run_ids), sorted([task_run_1_id, task_run_3_id]))

    def test_get_table_pk_field_name(self, *args):
        table_names = ["tasks", "task_runs", "units", "worker_review"]
        pk_fields = [db_utils.get_table_pk_field_name(self.db, t) for t in table_names]

        self.assertEqual(pk_fields, ["task_id", "task_run_id", "unit_id", "id"])

    def test_select_all_table_rows(self, *args):
        # Empty table
        rows = db_utils.select_all_table_rows(self.db, "projects", order_by="creation_date")
        self.assertEqual(len(rows), 0)

        # Table with 2 entries
        get_test_project(self.db, "project_1")
        get_test_project(self.db, "project_2")
        rows = db_utils.select_all_table_rows(self.db, "projects", order_by="creation_date")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["project_name"], "project_1")
        self.assertEqual(rows[1]["project_name"], "project_2")

    def test_select_rows_by_list_of_field_values(self, *args):
        qualification_1_id = get_test_qualification(self.db, "qual_1")
        qualification_2_id = get_test_qualification(self.db, "qual_2")
        _, worker_1_id = get_test_worker(self.db, worker_name="worker_1")
        _, worker_2_id = get_test_worker(self.db, worker_name="worker_2")
        grant_test_qualification(
            self.db,
            worker_id=worker_1_id,
            qualification_id=qualification_2_id,
            value=1,
        )
        grant_test_qualification(
            self.db,
            worker_id=worker_1_id,
            qualification_id=qualification_1_id,
            value=2,
        )
        grant_test_qualification(
            self.db,
            worker_id=worker_2_id,
            qualification_id=qualification_2_id,
            value=3,
        )

        rows = db_utils.select_rows_by_list_of_field_values(
            self.db,
            "granted_qualifications",
            field_names=["worker_id", "qualification_id"],
            field_values=[
                [worker_1_id, worker_2_id],
                [qualification_2_id],
            ],
            order_by="creation_date",
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["value"], 1)
        self.assertEqual(rows[1]["value"], 3)

    def test_delete_exported_data_without_fk_constraints(self, *args):
        task_1_name = "task_1"

        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_1_name)
        get_test_task_run(self.db, task_1_id, requester_id)

        task_rows = db_utils.select_all_table_rows(self.db, "tasks")
        task_run_rows = db_utils.select_all_table_rows(self.db, "task_runs")
        task_rows_len_before = len(task_rows)
        task_runs_rows_len_before = len(task_run_rows)

        dump = {
            "tasks": db_utils.serialize_data_for_table(task_rows),
            "task_runs": db_utils.serialize_data_for_table(task_run_rows),
        }

        db_utils.delete_exported_data_without_fk_constraints(
            self.db,
            db_dump=dump,
            table_names_can_be_cleaned=["tasks"],
        )

        task_rows_len_after = len(db_utils.select_all_table_rows(self.db, "tasks"))
        task_runs_rows_len_after = len(db_utils.select_all_table_rows(self.db, "task_runs"))

        self.assertEqual(task_rows_len_before, 1)
        self.assertEqual(task_runs_rows_len_before, 1)
        self.assertEqual(task_rows_len_after, 0)
        self.assertEqual(task_runs_rows_len_after, 1)

    def test_delete_entire_exported_data(self, *args):
        get_test_unit(self.db)

        db_utils.delete_entire_exported_data(self.db)

        table_names = db_utils.get_list_of_db_table_names(self.db)

        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name == "migrations":
                self.assertGreater(len(rows), 0)
            else:
                self.assertEqual(len(rows), 0)

    def test_get_list_of_provider_types(self, *args):
        requester_name_1 = "requester_1"
        requester_name_2 = "requester_2"
        provider_type_1 = "mock"
        provider_type_2 = "prolific"

        get_test_requester(self.db, requester_name_1, provider_type_1)
        get_test_requester(self.db, requester_name_2, provider_type_2)

        provider_types = db_utils.get_list_of_provider_types(self.db)

        self.assertEqual(sorted(provider_types), sorted([provider_type_1, provider_type_2]))

    def test_get_latest_row_from_table(self, *args):
        task_1_name = "task_1"
        task_2_name = "task_2"

        _, task_1_id = get_test_task(self.db, task_1_name)
        _, task_2_id = get_test_task(self.db, task_2_name)

        task_2 = Task.get(self.db, task_2_id)

        latest_task_row = db_utils.get_latest_row_from_table(self.db, "tasks", "creation_date")

        self.assertEqual(latest_task_row["task_id"], task_2_id)
        self.assertEqual(
            serialize_date_to_python(latest_task_row["creation_date"]),
            task_2.creation_date,
        )

    def test_apply_migrations(self, *args):
        new_table_name = "TEST_TABLE"
        test_migration_name = "test_migration"
        migrations = {
            test_migration_name: f"""
            CREATE TABLE {new_table_name} (
                id INTEGER PRIMARY KEY,
                creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        }

        db_utils.apply_migrations(self.db, migrations)

        table_names = db_utils.get_list_of_db_table_names(self.db)
        migration_rows = db_utils.select_all_table_rows(self.db, "migrations")
        migration_names = [m["name"] for m in migration_rows]

        self.assertIn(new_table_name, table_names)
        self.assertIn(test_migration_name, migration_names)

    def test_get_list_of_db_table_names(self, *args):
        table_names = db_utils.get_list_of_db_table_names(self.db)

        self.assertEqual(
            sorted(table_names),
            sorted(
                [
                    "agents",
                    "assignments",
                    "granted_qualifications",
                    "imported_data",
                    "migrations",
                    "onboarding_agents",
                    "projects",
                    "qualifications",
                    "requesters",
                    "sqlite_sequence",
                    "task_runs",
                    "tasks",
                    "worker_review",
                    "units",
                    "workers",
                ]
            ),
        )

    def test_get_list_of_tables_to_export(self, *args):
        table_names = db_utils.get_list_of_tables_to_export(self.db)

        self.assertEqual(
            sorted(table_names),
            sorted(
                [
                    "agents",
                    "assignments",
                    "granted_qualifications",
                    "imported_data",
                    "onboarding_agents",
                    "projects",
                    "qualifications",
                    "requesters",
                    "task_runs",
                    "tasks",
                    "worker_review",
                    "units",
                    "workers",
                ]
            ),
        )

    def test_get_list_of_available_labels(self, *args):
        label_1 = "test_label_1"
        label_2 = "test_label_2"
        label_3 = "test_label_3"

        db_utils.insert_new_row_in_table(
            db=self.db,
            table_name="imported_data",
            row=dict(
                source_file_name="test",
                data_labels=f'["{label_1}"]',
                table_name="task_runs",
                unique_field_names='["task_run_id"]',
                unique_field_values=f'["1","2"]',
            ),
        )
        db_utils.insert_new_row_in_table(
            db=self.db,
            table_name="imported_data",
            row=dict(
                source_file_name="test",
                data_labels=f'["{label_1}","{label_2}","{label_3}"]',
                table_name="tasks",
                unique_field_names='["task_id"]',
                unique_field_values=f'["1","2"]',
            ),
        )

        available_labels = db_utils.get_list_of_available_labels(self.db)

        self.assertEqual(sorted(available_labels), sorted([label_1, label_2, label_3]))

    def test_check_if_row_with_params_exists(self, *args):
        requester_name_1 = "requester_1"
        provider_type_1 = "mock"

        _, requester_id = get_test_requester(self.db, requester_name_1, provider_type_1)

        already_exists = db_utils.check_if_row_with_params_exists(
            db=self.db,
            table_name="requesters",
            params={
                "requester_id": requester_id,
                "provider_type": provider_type_1,
            },
            select_field="requester_id",
        )

        not_exists = db_utils.check_if_row_with_params_exists(
            db=self.db,
            table_name="requesters",
            params={
                "requester_id": "wrong_id",
                "provider_type": provider_type_1,
            },
            select_field="requester_id",
        )

        self.assertTrue(already_exists)
        self.assertFalse(not_exists)

    def test_get_providers_datastores(self, *args):
        requester_name_1 = "requester_1"
        requester_name_2 = "requester_2"
        provider_type_1 = "mock"
        provider_type_2 = "prolific"

        get_test_requester(self.db, requester_name_1, provider_type_1)
        get_test_requester(self.db, requester_name_2, provider_type_2)

        datastores = db_utils.get_providers_datastores(self.db)

        self.assertEqual(len(datastores.keys()), 2)
        self.assertIn(provider_type_1, datastores)
        self.assertIn(provider_type_2, datastores)
        self.assertTrue(isinstance(datastores[provider_type_1], MockDatastore))
        self.assertTrue(isinstance(datastores[provider_type_2], ProlificDatastore))

    def test_db_or_datastore_to_dict(self, *args):
        get_test_requester(self.db)
        get_test_worker(self.db)

        db_dump = db_utils.db_or_datastore_to_dict(self.db)

        table_names = db_utils.get_list_of_tables_to_export(self.db)

        for table_name in table_names:
            self.assertIn(table_name, db_dump)
            table_data = db_dump[table_name]
            if table_name in ["requesters", "workers"]:
                self.assertEqual(len(table_data), 1)
                self.assertGreater(len(table_data[0].keys()), 0)
            else:
                self.assertEqual(len(table_data), 0)

    def test_mephisto_db_to_dict_for_task_runs(self, *args):
        tables_without_task_run_id = [
            "workers",
            "tasks",
            "requesters",
            "qualifications",
            "granted_qualifications",
        ]

        _, requester_id = get_test_requester(self.db)

        table_names = db_utils.get_list_of_tables_to_export(self.db)

        # First TaskRun
        task_run_id_1 = get_test_task_run(self.db, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        db_dump_for_task_run_1 = db_utils.mephisto_db_to_dict_for_task_runs(
            self.db,
            task_run_ids=[task_run_id_1],
        )
        for table_name in table_names:
            if table_name == "imported_data":
                continue

            table_data = db_dump_for_task_run_1[table_name]
            if table_name in ["onboarding_agents", "worker_review", "projects"]:
                self.assertEqual(len(table_data), 0)
            else:
                if table_name not in tables_without_task_run_id:
                    self.assertEqual(table_data[0]["task_run_id"], task_run_id_1)
                self.assertEqual(len(table_data), 1)

        # Second TaskRun
        _, task_2_id = get_test_task(self.db, "task_2")
        task_run_id_2 = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)

        db_dump_for_task_run_2 = db_utils.mephisto_db_to_dict_for_task_runs(
            self.db,
            task_run_ids=[task_run_id_2],
        )
        for table_name in table_names:
            if table_name == "imported_data":
                continue

            table_data = db_dump_for_task_run_2[table_name]
            if table_name in ["task_runs", "tasks", "requesters"]:
                if table_name not in tables_without_task_run_id:
                    self.assertEqual(table_data[0]["task_run_id"], task_run_id_2)
                self.assertEqual(len(table_data), 1)
            else:
                self.assertEqual(len(table_data), 0)

    def test_select_task_run_ids_since_date(self, *args):
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, "task_1")
        task_run_1_id = get_test_task_run(self.db, task_1_id, requester_id)
        task_run_2_id = get_test_task_run(self.db, task_1_id, requester_id)

        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)

        since_task_run_1_created = task_run_1.creation_date - timedelta(milliseconds=1)
        since_task_run_2_created = task_run_2.creation_date - timedelta(milliseconds=1)

        task_run_ids_since_task_run_1_created = db_utils.select_task_run_ids_since_date(
            self.db,
            since_task_run_1_created,
        )
        task_run_ids_since_task_run_2_created = db_utils.select_task_run_ids_since_date(
            self.db,
            since_task_run_2_created,
        )

        self.assertEqual(
            sorted(task_run_ids_since_task_run_1_created),
            sorted([task_run_1_id, task_run_2_id]),
        )
        self.assertEqual(
            sorted(task_run_ids_since_task_run_2_created),
            sorted([task_run_2_id]),
        )

    def test_select_fk_mappings_for_table(self, *args):
        units_mappings = db_utils.select_fk_mappings_for_single_table(self.db, "units")

        self.assertEqual(
            units_mappings,
            {
                "agents": {"from": "agent_id", "to": "agent_id"},
                "assignments": {"from": "assignment_id", "to": "assignment_id"},
                "requesters": {"from": "requester_id", "to": "requester_id"},
                "task_runs": {"from": "task_run_id", "to": "task_run_id"},
                "tasks": {"from": "task_id", "to": "task_id"},
                "workers": {"from": "worker_id", "to": "worker_id"},
            },
        )

    def test_select_fk_mappings_for_tables(self, *args):
        fk_mappings = db_utils.select_fk_mappings_for_tables(self.db, ["units", "tasks"])

        self.assertEqual(
            fk_mappings,
            {
                "tasks": {
                    "projects": {"from": "project_id", "to": "project_id"},
                    "tasks": {"from": "parent_task_id", "to": "task_id"},
                },
                "units": {
                    "agents": {"from": "agent_id", "to": "agent_id"},
                    "assignments": {"from": "assignment_id", "to": "assignment_id"},
                    "requesters": {"from": "requester_id", "to": "requester_id"},
                    "task_runs": {"from": "task_run_id", "to": "task_run_id"},
                    "tasks": {"from": "task_id", "to": "task_id"},
                    "workers": {"from": "worker_id", "to": "worker_id"},
                },
            },
        )

    def test_insert_new_row_in_table(self, *args):
        rows_count_before = len(db_utils.select_all_table_rows(self.db, "workers"))

        _, requester_id = get_test_requester(self.db)
        requester = Requester.get(self.db, requester_id)

        db_utils.insert_new_row_in_table(
            self.db,
            "workers",
            {
                "worker_name": "test_worker",
                "provider_type": requester.provider_type,
            },
        )

        rows_count_after = len(db_utils.select_all_table_rows(self.db, "workers"))

        self.assertEqual(rows_count_before, 0)
        self.assertEqual(rows_count_after, 1)

    def test_update_row_in_table(self, *args):
        updated_requester_name = "updated_requester_name"

        _, requester_id = get_test_requester(self.db)
        row_before = self.db.get_requester(requester_id)

        db_utils.update_row_in_table(
            self.db, "requesters", {**row_before, **{"requester_name": updated_requester_name}}
        )

        row_after = self.db.get_requester(requester_id)

        self.assertNotEqual(row_before["requester_name"], updated_requester_name)
        self.assertEqual(row_after["requester_name"], updated_requester_name)

    def test_retry_generate_id(self, *args):

        # Function to simulate methods in Mephisto DB and provider-specific datastores
        @db_utils.retry_generate_id(caught_excs=[EntryAlreadyExistsException])
        def _insert_new_row_in_projects(db: "MephistoDB", name: str):
            with db.table_access_condition, db.get_connection() as conn:
                c = conn.cursor()

                try:
                    c.execute(
                        f"""
                        INSERT INTO projects(
                            project_id, project_name
                        ) VALUES (?, ?);
                        """,
                        (
                            db_utils.make_randomized_int_id(),
                            name,
                        ),
                    )
                except sqlite3.IntegrityError as e:
                    if is_unique_failure(e):
                        raise EntryAlreadyExistsException(
                            e,
                            db=db,
                            table_name="projects",
                            original_exc=e,
                        )

        project_id_1 = 1
        project_id_2 = project_id_1
        project_id_3 = project_id_1
        project_id_4 = db_utils.make_randomized_int_id()
        mock_randomized_ids = [
            project_id_1,  # Correct first id
            project_id_2,  # Conflicting id
            project_id_3,  # Conflicting id
            project_id_4,  # Random id that must be called after conflict
        ]

        project_names = ["project_name_1", "project_name_2"]

        with patch("mephisto.utils.db.make_randomized_int_id") as mock_make_randomized_int_id:
            mock_make_randomized_int_id.side_effect = mock_randomized_ids

            # 1. We call function only TWICE (for each project_name).
            # 2. First call creates project for first name
            # 3. Second call raises exception and decorator retries to call function again twice
            # where mocked `make_randomized_int_id` returns randomized id
            # (3d value in `mock_randomized_ids` var)
            for project_name in project_names:
                # Call function wrapped with decorator `retry_generate_id`
                _insert_new_row_in_projects(self.db, project_name)

        rows = db_utils.select_all_table_rows(self.db, "projects", order_by="creation_date")

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["project_id"], str(project_id_1))
        self.assertEqual(rows[1]["project_id"], str(project_id_4))
