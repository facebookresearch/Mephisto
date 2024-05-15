#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from datetime import timedelta
from typing import ClassVar
from typing import Type
from unittest.mock import patch

import pytest
from omegaconf import OmegaConf

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun
from mephisto.tools.db_data_porter import DBDataPorter
from mephisto.tools.db_data_porter.constants import EXAMPLE_CONFLICT_RESOLVER
from mephisto.utils import db as db_utils
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_requester
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from mephisto.utils.testing import make_completed_unit
from mephisto.utils.testing import MOCK_CONFIG

FILE_TIMESTAMP = "2001_01_01_01_01_01"


@pytest.mark.db_data_porter
class TestDBDataPorter(unittest.TestCase):
    DB_CLASS: ClassVar[Type["MephistoDB"]] = LocalMephistoDB

    def setUp(self):
        # Configure test database
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "test_mephisto.db")

        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)

        # Backup dir
        self.backup_dir = os.path.join(self.data_dir, "backup")
        os.makedirs(self.backup_dir, exist_ok=True)

        # Restore dir
        self.restore_dir = os.path.join(self.data_dir, "restore")
        os.makedirs(self.restore_dir, exist_ok=True)

        # Export dir
        self.export_dir = os.path.join(self.data_dir, "export")
        os.makedirs(self.export_dir, exist_ok=True)

        # Init db data porter instance
        self.porter = DBDataPorter(self.db)

    def tearDown(self):
        # Clean test database
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def _prepare_dump_for_importing(self, with_imported_data: bool = False) -> dict:
        # Create entries in Mephisto DB
        prev_imported_data_label = "existing_label"
        task_name = "test_task_name"
        _, requester_id = get_test_requester(self.db)
        _, task_id = get_test_task(self.db, task_name=task_name)
        task_run_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        if with_imported_data:
            db_utils.insert_new_row_in_table(
                db=self.db,
                table_name="imported_data",
                row=dict(
                    source_file_name="test",
                    data_labels=f'["{prev_imported_data_label}"]',
                    table_name="task_runs",
                    unique_field_names='["task_run_id"]',
                    unique_field_values=f'["{task_run_id}"]',
                ),
            )

        # Create dump
        export_results = self.porter.export_dump()
        dump_archive_file_path = export_results["dump_path"]

        # Clear db (removing data that was made for export)
        db_utils.delete_entire_exported_data(self.db)

        return {
            "prev_imported_data_label": prev_imported_data_label,
            "requester_id": requester_id,
            "task_name": task_name,
            "task_id": task_id,
            "task_run_id": task_run_id,
            "worker_id": worker_id,
            "unit_id": unit_id,
            "qualification_id": qualification_id,
            "dump_archive_file_path": dump_archive_file_path,
        }

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    def test_create_backup(self, mock__make_export_timestamp, mock_get_data_dir, *args):
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        mock_get_data_dir.return_value = self.data_dir

        with patch(
            "mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_backup_dir"
        ) as mock__get_backup_dir:
            mock__get_backup_dir.return_value = self.backup_dir

            files_count_before = len([fn for fn in os.listdir(self.backup_dir)])

            self.porter.create_backup()

            backup_filenames = os.listdir(self.backup_dir)
            files_count_after = len([fn for fn in backup_filenames])

            self.assertEqual(files_count_before, 0)
            self.assertEqual(files_count_after, 1)
            self.assertEqual(backup_filenames[0], f"{FILE_TIMESTAMP}_mephisto_backup.zip")

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_restore_from_backup(
        self,
        mock__ask_user_if_they_are_sure,
        mock_get_data_dir,
        mock_backups_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock_get_data_dir.return_value = self.restore_dir
        mock_backups_get_data_dir.return_value = self.data_dir

        files_count_before = len([fn for fn in os.listdir(self.restore_dir)])
        backup_file_path = self.porter.create_backup()

        self.porter.restore_from_backup(backup_file_name_or_path=backup_file_path)

        files_count_after = len([fn for fn in os.listdir(self.restore_dir)])

        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 4)

    @patch("mephisto.tools.db_data_porter.db_data_porter.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_restore_from_backup_no_option_file(
        self,
        mock__ask_user_if_they_are_sure,
        mock_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock_get_data_dir.return_value = self.restore_dir

        with self.assertRaises(SystemExit):
            captured_print_output = io.StringIO()
            sys.stdout = captured_print_output
            self.porter.restore_from_backup(backup_file_name_or_path=None)
            sys.stdout = sys.__stdout__

        self.assertIn("Option `-f/--file` is required.", captured_print_output.getvalue())
        mock__ask_user_if_they_are_sure.assert_not_called()
        mock_get_data_dir.assert_not_called()

    @patch("mephisto.tools.db_data_porter.db_data_porter.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_restore_from_backup_option_file_incorrect(
        self,
        mock__ask_user_if_they_are_sure,
        mock_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock_get_data_dir.return_value = self.restore_dir

        file_name = "incorrect_path"

        with self.assertRaises(SystemExit):
            captured_print_output = io.StringIO()
            sys.stdout = captured_print_output
            self.porter.restore_from_backup(backup_file_name_or_path=file_name)
            sys.stdout = sys.__stdout__

        self.assertIn("Could not find backup file", captured_print_output.getvalue())
        self.assertIn(f"outputs/backup/{file_name}", captured_print_output.getvalue())
        mock__ask_user_if_they_are_sure.assert_not_called()
        mock_get_data_dir.assert_not_called()

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_full(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        task_run_id_1 = get_test_task_run(self.db, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump()

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)
        self.assertIn(f"export/{FILE_TIMESTAMP}_mephisto_dump.zip", export_results["dump_path"])
        self.assertEqual(export_results["backup_path"], None)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())

                # Test main keys
                self.assertIn("dump_metadata", dump_file_data)
                self.assertIn("mephisto", dump_file_data)

                # Test `dump_metadata`
                self.assertEqual(dump_file_data["dump_metadata"]["export_options"], None)
                self.assertEqual(
                    dump_file_data["dump_metadata"]["migrations"],
                    {"mephisto": "20240418_data_porter_feature"},
                )
                self.assertEqual(dump_file_data["dump_metadata"]["pk_substitutions"], {})
                self.assertEqual(dump_file_data["dump_metadata"]["timestamp"], FILE_TIMESTAMP)

                # Test `mephisto`
                mephisto_dump = dump_file_data["mephisto"]

                tables_without_task_run_id = [
                    "workers",
                    "tasks",
                    "requesters",
                    "qualifications",
                    "granted_qualifications",
                ]

                for table_name in mephisto_dump.keys():
                    if table_name == "imported_data":
                        continue

                    table_data = mephisto_dump[table_name]
                    if table_name in ["onboarding_agents", "unit_review", "projects"]:
                        self.assertEqual(len(table_data), 0)
                    else:
                        if table_name not in tables_without_task_run_id:
                            self.assertEqual(table_data[0]["task_run_id"], task_run_id_1)
                        self.assertEqual(len(table_data), 1)

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_task_names(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump(task_names=[task_name_1])

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]

                self.assertEqual(len(mephisto_dump["tasks"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 2)
                self.assertEqual(mephisto_dump["tasks"][0]["task_id"], task_1_id)
                self.assertEqual(len(mephisto_dump["task_runs"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 2)
                self.assertEqual(mephisto_dump["task_runs"][0]["task_run_id"], task_run_1_id)
                self.assertEqual(len(mephisto_dump["workers"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "workers")), 1)
                self.assertEqual(len(mephisto_dump["units"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "units")), 1)
                self.assertEqual(len(mephisto_dump["qualifications"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "qualifications")), 1)
                self.assertEqual(len(mephisto_dump["granted_qualifications"]), 0)
                self.assertEqual(
                    len(db_utils.select_all_table_rows(self.db, "granted_qualifications")),
                    1,
                )

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_task_ids(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump(task_ids=[task_1_id])

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]

                self.assertEqual(len(mephisto_dump["tasks"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 2)
                self.assertEqual(mephisto_dump["tasks"][0]["task_id"], task_1_id)
                self.assertEqual(len(mephisto_dump["task_runs"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 2)
                self.assertEqual(mephisto_dump["task_runs"][0]["task_run_id"], task_run_1_id)
                self.assertEqual(len(mephisto_dump["workers"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "workers")), 1)
                self.assertEqual(len(mephisto_dump["units"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "units")), 1)
                self.assertEqual(len(mephisto_dump["qualifications"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "qualifications")), 1)
                self.assertEqual(len(mephisto_dump["granted_qualifications"]), 0)
                self.assertEqual(
                    len(db_utils.select_all_table_rows(self.db, "granted_qualifications")),
                    1,
                )

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_task_run_ids(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump(task_run_ids=[task_run_1_id])

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]

                self.assertEqual(len(mephisto_dump["tasks"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 2)
                self.assertEqual(mephisto_dump["tasks"][0]["task_id"], task_1_id)
                self.assertEqual(len(mephisto_dump["task_runs"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 2)
                self.assertEqual(mephisto_dump["task_runs"][0]["task_run_id"], task_run_1_id)
                self.assertEqual(len(mephisto_dump["workers"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "workers")), 1)
                self.assertEqual(len(mephisto_dump["units"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "units")), 1)
                self.assertEqual(len(mephisto_dump["qualifications"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "qualifications")), 1)
                self.assertEqual(len(mephisto_dump["granted_qualifications"]), 0)
                self.assertEqual(
                    len(db_utils.select_all_table_rows(self.db, "granted_qualifications")),
                    1,
                )

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_task_runs_since_date(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        since_task_run_2_created = (
            task_run_2.creation_date - timedelta(milliseconds=1)
        ).isoformat()

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump(task_runs_since_date=since_task_run_2_created)

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]

                self.assertEqual(len(mephisto_dump["tasks"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 2)
                self.assertEqual(mephisto_dump["tasks"][0]["task_id"], task_2_id)
                self.assertEqual(len(mephisto_dump["task_runs"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 2)
                self.assertEqual(mephisto_dump["task_runs"][0]["task_run_id"], task_run_2_id)

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_task_runs_labels(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        test_label = "test_label"
        db_utils.insert_new_row_in_table(
            db=self.db,
            table_name="imported_data",
            row=dict(
                source_file_name="test",
                data_labels=f'["{test_label}"]',
                table_name="task_runs",
                unique_field_names='["task_run_id"]',
                unique_field_values=f'["{task_run_1_id}"]',
            ),
        )

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump(task_run_labels=[test_label])

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]

                self.assertEqual(len(mephisto_dump["tasks"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "tasks")), 2)
                self.assertEqual(mephisto_dump["tasks"][0]["task_id"], task_1_id)
                self.assertEqual(len(mephisto_dump["task_runs"]), 1)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "task_runs")), 2)
                self.assertEqual(mephisto_dump["task_runs"][0]["task_run_id"], task_run_1_id)
                self.assertEqual(len(mephisto_dump["workers"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "workers")), 1)
                self.assertEqual(len(mephisto_dump["units"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "units")), 1)
                self.assertEqual(len(mephisto_dump["qualifications"]), 0)
                self.assertEqual(len(db_utils.select_all_table_rows(self.db, "qualifications")), 1)
                self.assertEqual(len(mephisto_dump["granted_qualifications"]), 0)
                self.assertEqual(
                    len(db_utils.select_all_table_rows(self.db, "granted_qualifications")),
                    1,
                )

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_delete_exported_data(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        mock_backups_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        mock_backups_get_data_dir.return_value = self.data_dir

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])
        task_run_rows_before = db_utils.select_all_table_rows(self.db, "task_runs")
        unit_rows_before = db_utils.select_all_table_rows(self.db, "units")
        task_rows_before = db_utils.select_all_table_rows(self.db, "tasks")
        worker_rows_before = db_utils.select_all_table_rows(self.db, "workers")
        qualification_rows_before = db_utils.select_all_table_rows(self.db, "qualifications")
        granted_qualification_rows_before = db_utils.select_all_table_rows(
            self.db,
            "granted_qualifications",
        )

        # Create dump
        export_results = self.porter.export_dump(
            task_run_ids=[task_run_2_id],
            delete_exported_data=True,
        )

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_called_once()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]

                # Tables where we deleted entries
                task_run_rows_after = db_utils.select_all_table_rows(self.db, "task_runs")
                unit_rows_after = db_utils.select_all_table_rows(self.db, "units")
                self.assertEqual(len(mephisto_dump["task_runs"]), 1)
                self.assertEqual(len(task_run_rows_before), 2)
                self.assertEqual(len(task_run_rows_after), 1)
                self.assertEqual(mephisto_dump["task_runs"][0]["task_run_id"], task_run_2_id)
                self.assertEqual(task_run_rows_after[0]["task_run_id"], task_run_1_id)
                self.assertEqual(len(mephisto_dump["units"]), 1)
                self.assertEqual(len(unit_rows_before), 1)
                self.assertEqual(len(unit_rows_after), 0)

                # Tables where we left entries untouched
                task_rows_after = db_utils.select_all_table_rows(self.db, "tasks")
                worker_rows_after = db_utils.select_all_table_rows(self.db, "workers")
                qualification_rows_after = db_utils.select_all_table_rows(self.db, "qualifications")
                granted_qualification_rows_after = db_utils.select_all_table_rows(
                    self.db,
                    "granted_qualifications",
                )
                self.assertEqual(len(mephisto_dump["tasks"]), 1)
                self.assertEqual(len(task_rows_before), 2)
                self.assertEqual(len(task_rows_after), 2)
                self.assertEqual(mephisto_dump["tasks"][0]["task_id"], task_2_id)
                self.assertEqual(len(mephisto_dump["workers"]), 1)
                self.assertEqual(len(worker_rows_before), 1)
                self.assertEqual(len(worker_rows_after), 1)
                self.assertEqual(len(mephisto_dump["qualifications"]), 1)
                self.assertEqual(len(qualification_rows_before), 1)
                self.assertEqual(len(qualification_rows_after), 1)
                self.assertEqual(len(mephisto_dump["granted_qualifications"]), 1)
                self.assertEqual(len(granted_qualification_rows_before), 1)
                self.assertEqual(len(granted_qualification_rows_after), 1)

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_randomize_legacy_ids(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        legacy_task_run_id = "1"
        db_utils.insert_new_row_in_table(
            db=self.db,
            table_name="task_runs",
            row=dict(
                task_run_id=legacy_task_run_id,
                task_id=task_1_id,
                requester_id=requester_id,
                task_type="mock",
                provider_type="mock",
                is_completed=False,
                sandbox=False,
                init_params=json.dumps(OmegaConf.to_yaml(OmegaConf.structured(MOCK_CONFIG))),
            ),
        )

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])
        task_run_rows_before = db_utils.select_all_table_rows(self.db, "task_runs", "creation_date")

        # Create dump
        export_results = self.porter.export_dump(randomize_legacy_ids=True)

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                dump_file_data = json.loads(f.read())
                mephisto_dump = dump_file_data["mephisto"]
                pk_substitutions = dump_file_data["dump_metadata"]["pk_substitutions"]["mephisto"][
                    "task_runs"
                ]
                task_runs_dump = sorted(
                    mephisto_dump["task_runs"],
                    key=lambda k: k["creation_date"],
                )

                self.assertEqual(task_run_rows_before[0]["task_run_id"], task_run_1_id)
                self.assertEqual(task_run_rows_before[1]["task_run_id"], legacy_task_run_id)
                self.assertEqual(
                    task_runs_dump[0]["task_run_id"],
                    task_run_1_id,
                )
                self.assertNotEqual(
                    task_runs_dump[1]["task_run_id"],
                    legacy_task_run_id,
                )
                self.assertEqual(
                    pk_substitutions,
                    {
                        legacy_task_run_id: task_runs_dump[1]["task_run_id"],
                    },
                )

    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_export_dump_option_json_indent(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        indentation = 8

        # Create entries in Mephisto DB
        get_test_task_run(self.db)

        files_count_before = len([fn for fn in os.listdir(self.export_dir)])

        # Create dump
        export_results = self.porter.export_dump(json_indent=indentation)

        files_count_after = len([fn for fn in os.listdir(self.export_dir)])

        # Test question
        mock__ask_user_if_they_are_sure.assert_not_called()

        # Test files
        self.assertEqual(files_count_before, 0)
        self.assertEqual(files_count_after, 1)

        # Test dump archive
        with zipfile.ZipFile(export_results["dump_path"]) as archive:
            dump_name = os.path.basename(os.path.splitext(export_results["dump_path"])[0])
            json_dump_file_name = f"{dump_name}.json"

            with archive.open(json_dump_file_name) as f:
                first_line = f.readline().decode("utf-8")
                second_line = f.readline().decode("utf-8")
                third_line = f.readline().decode("utf-8")

                spaces = lambda n: " " * n
                self.assertTrue(first_line.startswith(spaces(0 * indentation) + "{"))
                self.assertTrue(first_line.endswith("\n"))
                self.assertTrue(second_line.startswith(spaces(1 * indentation) + '"'))
                self.assertTrue(second_line.endswith("\n"))
                self.assertTrue(third_line.startswith(spaces(2 * indentation) + '"'))
                self.assertTrue(third_line.endswith("\n"))

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_import_dump_full(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        mock_backups_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        mock_backups_get_data_dir.return_value = self.data_dir

        # Make a dump
        dump_data = self._prepare_dump_for_importing()
        dump_archive_file_path = dump_data["dump_archive_file_path"]
        task_run_id = dump_data["task_run_id"]
        requester_id = dump_data["requester_id"]
        worker_id = dump_data["worker_id"]
        qualification_id = dump_data["qualification_id"]
        unit_id = dump_data["unit_id"]

        # Test that database is empty
        table_names = db_utils.get_list_of_tables_to_export(self.db)
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            self.assertEqual(len(rows), 0)

        # Import dump
        results = self.porter.import_dump(dump_archive_file_name_or_path=dump_archive_file_path)

        # Test imported data in database
        mock__ask_user_if_they_are_sure.assert_called_once()
        self.assertEqual(results["imported_task_runs_number"], 1)
        table_names = db_utils.get_list_of_tables_to_export(self.db)
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name == "imported_data":
                self.assertEqual(len(rows), 6)
            elif table_name in ["projects", "onboarding_agents", "unit_review"]:
                self.assertEqual(len(rows), 0)
            else:
                self.assertEqual(len(rows), 1)

            if table_name == "task_runs":
                self.assertEqual(rows[0]["task_run_id"], task_run_id)
            elif table_name == "requesters":
                self.assertEqual(rows[0]["requester_id"], requester_id)
            elif table_name == "workers":
                self.assertEqual(rows[0]["worker_id"], worker_id)
            elif table_name == "qualifications":
                self.assertEqual(rows[0]["qualification_id"], qualification_id)
            elif table_name == "units":
                self.assertEqual(rows[0]["unit_id"], unit_id)

    @patch("mephisto.tools.db_data_porter.db_data_porter.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_import_dump_no_option_file(
        self,
        mock__ask_user_if_they_are_sure,
        mock_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock_get_data_dir.return_value = self.restore_dir

        with self.assertRaises(SystemExit):
            captured_print_output = io.StringIO()
            sys.stdout = captured_print_output
            self.porter.import_dump(dump_archive_file_name_or_path=None)
            sys.stdout = sys.__stdout__

        self.assertIn("Option `-f/--file` is required.", captured_print_output.getvalue())
        mock__ask_user_if_they_are_sure.assert_not_called()
        mock_get_data_dir.assert_not_called()

    @patch("mephisto.tools.db_data_porter.db_data_porter.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_import_dump_option_file_incorrect(
        self,
        mock__ask_user_if_they_are_sure,
        mock_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock_get_data_dir.return_value = self.restore_dir

        file_name = "incorrect_path"

        with self.assertRaises(SystemExit):
            captured_print_output = io.StringIO()
            sys.stdout = captured_print_output
            self.porter.import_dump(dump_archive_file_name_or_path=file_name)
            sys.stdout = sys.__stdout__

        self.assertIn("Could not find dump file", captured_print_output.getvalue())
        self.assertIn(f"outputs/export/{file_name}", captured_print_output.getvalue())
        mock__ask_user_if_they_are_sure.assert_not_called()
        mock_get_data_dir.assert_not_called()

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_import_dump_option_labels(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        mock_backups_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        mock_backups_get_data_dir.return_value = self.data_dir

        labels = ["test_label_1", "test_label_2"]

        # Make a dump
        dump_data = self._prepare_dump_for_importing()
        dump_archive_file_path = dump_data["dump_archive_file_path"]

        # Test that database is empty
        table_names = db_utils.get_list_of_tables_to_export(self.db)
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            self.assertEqual(len(rows), 0)

        # Import dump
        results = self.porter.import_dump(
            dump_archive_file_name_or_path=dump_archive_file_path,
            labels=labels,
        )

        # Test imported data in database
        mock__ask_user_if_they_are_sure.assert_called_once()
        self.assertEqual(results["imported_task_runs_number"], 1)

        # Test labels
        available_labels = db_utils.get_list_of_available_labels(self.db)
        self.assertEqual(sorted(available_labels), sorted(labels))

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_import_dump_option_keep_import_metadata(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        mock_backups_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        mock_backups_get_data_dir.return_value = self.data_dir

        labels = ["test_label"]

        # Make a dump
        dump_data = self._prepare_dump_for_importing(with_imported_data=True)
        dump_archive_file_path = dump_data["dump_archive_file_path"]
        prev_imported_data_label = dump_data["prev_imported_data_label"]
        task_run_id = dump_data["task_run_id"]

        # Test that database is empty
        table_names = db_utils.get_list_of_tables_to_export(self.db)
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            self.assertEqual(len(rows), 0)

        # Import dump
        results = self.porter.import_dump(
            dump_archive_file_name_or_path=dump_archive_file_path,
            labels=labels,
            keep_import_metadata=True,
        )

        # Test imported data in database
        mock__ask_user_if_they_are_sure.assert_called_once()
        self.assertEqual(results["imported_task_runs_number"], 1)

        # Test labels
        available_labels = db_utils.get_list_of_available_labels(self.db)
        self.assertEqual(sorted(available_labels), sorted([*labels, prev_imported_data_label]))

        # Test that imported data was added
        imported_data_rows = db_utils.select_all_table_rows(self.db, "imported_data")
        self.assertEqual(len(imported_data_rows), 6)

        # Test that TaskRuns were merged and can we found by label from dump's `imported_data`
        task_run_ids = db_utils.get_task_run_ids_by_labels(self.db, [prev_imported_data_label])
        self.assertEqual(task_run_ids, [task_run_id])

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._make_export_timestamp")
    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._get_export_dir")
    @patch("mephisto.tools.db_data_porter.db_data_porter.DBDataPorter._ask_user_if_they_are_sure")
    def test_import_dump_option_conflict_resolver_name(
        self,
        mock__ask_user_if_they_are_sure,
        mock__get_export_dir,
        mock_get_data_dir,
        mock__make_export_timestamp,
        mock_backups_get_data_dir,
        *args,
    ):
        mock__ask_user_if_they_are_sure.return_value = True
        mock__get_export_dir.return_value = self.export_dir
        mock_get_data_dir.return_value = self.data_dir
        mock__make_export_timestamp.return_value = FILE_TIMESTAMP
        mock_backups_get_data_dir.return_value = self.data_dir

        # Make a dump
        dump_data = self._prepare_dump_for_importing()
        dump_archive_file_path = dump_data["dump_archive_file_path"]
        task_name = dump_data["task_name"]
        dump_task_id = dump_data["task_id"]

        # Test that database is empty
        table_names = db_utils.get_list_of_tables_to_export(self.db)
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            self.assertEqual(len(rows), 0)

        # Create conflicting task
        _, existing_task_id = get_test_task(self.db, task_name=task_name)

        # Import dump
        results = self.porter.import_dump(
            dump_archive_file_name_or_path=dump_archive_file_path,
            conflict_resolver_name=EXAMPLE_CONFLICT_RESOLVER,
        )

        # Test imported data in database
        mock__ask_user_if_they_are_sure.assert_called_once()
        self.assertEqual(results["imported_task_runs_number"], 1)

        # Test tasks were merged
        task_rows = db_utils.select_all_table_rows(self.db, "tasks")
        self.assertEqual(len(task_rows), 1)

        # Test conflict resolver results
        task = task_rows[0]
        self.assertEqual(task["task_id"], existing_task_id)
        self.assertNotEqual(task["task_id"], dump_task_id)
        self.assertEqual(task["task_name"], f"{task_name} + {task_name}")
        self.assertEqual(task["creation_date"], "2000-01-01 00:00:00")
