#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import io
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import pytest

from mephisto.tools.db_data_porter.backups import make_backup_file_path_by_timestamp
from mephisto.tools.db_data_porter.backups import make_full_data_dir_backup
from mephisto.tools.db_data_porter.backups import restore_from_backup


@pytest.mark.db_data_porter
class TestBackups(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_make_backup_file_path_by_timestamp(self, *args):
        timestamp = "2001_01_01_01_01_01"
        path = make_backup_file_path_by_timestamp(
            backup_dir=self.data_dir,
            timestamp=timestamp,
        )

        self.assertEqual(path, os.path.join(self.data_dir, f"{timestamp}_mephisto_backup.zip"))

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    def test_make_full_data_dir_backup(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        test_file_name = "test_backup.zip"
        backup_file_path = os.path.join(self.data_dir, test_file_name)

        self.assertFalse(os.path.exists(backup_file_path))

        make_full_data_dir_backup(backup_file_path)

        self.assertTrue(os.path.exists(backup_file_path))

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    def test_restore_from_backup_without_deleting_backup(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        test_file_name = "test_backup.zip"
        restore_dir_name = "test_restore"
        backup_file_path = os.path.join(self.data_dir, test_file_name)
        extract_dir = os.path.join(self.data_dir, restore_dir_name)

        make_full_data_dir_backup(backup_file_path)

        self.assertFalse(os.path.exists(extract_dir))

        restore_from_backup(backup_file_path, extract_dir)

        self.assertTrue(os.path.exists(extract_dir))
        self.assertTrue(os.path.exists(backup_file_path))

    @patch("mephisto.tools.db_data_porter.backups.get_data_dir")
    def test_restore_from_backup_with_deleting_backup(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        test_file_name = "test_backup.zip"
        restore_dir_name = "test_restore"
        backup_file_path = os.path.join(self.data_dir, test_file_name)
        extract_dir = os.path.join(self.data_dir, restore_dir_name)

        make_full_data_dir_backup(backup_file_path)

        self.assertFalse(os.path.exists(extract_dir))

        restore_from_backup(backup_file_path, extract_dir, remove_backup=True)

        self.assertTrue(os.path.exists(extract_dir))
        self.assertFalse(os.path.exists(backup_file_path))

    def test_restore_from_backup_error(self, *args):
        test_file_name = "test_backup.zip"
        restore_dir_name = "test_restore"
        backup_file_path = os.path.join(self.data_dir, test_file_name)
        extract_dir = os.path.join(self.data_dir, restore_dir_name)

        self.assertFalse(os.path.exists(extract_dir))

        with self.assertRaises(SystemExit) as cm:
            captured_print_output = io.StringIO()
            sys.stdout = captured_print_output
            restore_from_backup(backup_file_path, extract_dir, remove_backup=True)
            sys.stdout = sys.__stdout__

        self.assertEqual(cm.exception.code, None)
        self.assertFalse(os.path.exists(extract_dir))
        self.assertFalse(os.path.exists(backup_file_path))
        self.assertIn("Could not restore backup", captured_print_output.getvalue())
        self.assertIn(backup_file_path, captured_print_output.getvalue())
