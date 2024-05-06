#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import shutil
import tempfile
import unittest
import zipfile
from typing import ClassVar
from typing import Type
from unittest.mock import patch

import pytest

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.db_data_porter import DBDataPorter
from mephisto.utils import db as db_utils
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_requester
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from mephisto.utils.testing import make_completed_unit

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

        # Test fiels
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

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        task_run_id_1 = get_test_task_run(self.db, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        # Create dump
        export_results = self.porter.export_dump()
        dump_archive_file_path = export_results["dump_path"]

        # Clear db
        db_utils.delete_entire_exported_data(self.db)

        # Test clear database
        table_names = db_utils.get_list_of_tables_to_export(self.db)
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            self.assertEqual(len(rows), 0)

        # Import dump
        results = self.porter.import_dump(dump_archive_file_name_or_path=dump_archive_file_path)

        # Test imported data into clear database
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
                self.assertEqual(rows[0]["task_run_id"], task_run_id_1)
            elif table_name == "requesters":
                self.assertEqual(rows[0]["requester_id"], requester_id)
            elif table_name == "workers":
                self.assertEqual(rows[0]["worker_id"], worker_id)
            elif table_name == "qualifications":
                self.assertEqual(rows[0]["qualification_id"], qualification_id)
            elif table_name == "units":
                self.assertEqual(rows[0]["unit_id"], unit_id)
