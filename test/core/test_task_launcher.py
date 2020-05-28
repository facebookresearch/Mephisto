#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile
from typing import List

from mephisto.data_model.test.utils import get_test_task_run
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.task_launcher import TaskLauncher
from mephisto.data_model.assignment import InitializationData
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.task import TaskRun

from mephisto.providers.mock.mock_provider import MockProvider
from mephisto.server.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner


class TestTaskLauncher(unittest.TestCase):
    """
    Unit testing for the Mephisto TaskLauncher
    """

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.task_run_id = get_test_task_run(self.db)
        self.task_run = TaskRun(self.db, self.task_run_id)

    def tearDown(self):
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    def get_mock_assignment_data_array(self) -> List[InitializationData]:
        return [MockTaskRunner.get_mock_assignment_data()]

    def test_init_on_task_run(self):
        """Initialize a launcher on a task_run"""
        launcher = TaskLauncher(
            self.db, self.task_run, self.get_mock_assignment_data_array()
        )
        self.assertEqual(self.db, launcher.db)
        self.assertEqual(self.task_run, launcher.task_run)
        self.assertEqual(len(launcher.assignments), 0)
        self.assertEqual(len(launcher.units), 0)
        self.assertEqual(launcher.provider_type, MockProvider.PROVIDER_TYPE)

    def test_create_launch_expire_assignments(self):
        """Initialize a launcher on a task run, then create the assignments"""
        mock_data_array = self.get_mock_assignment_data_array()
        launcher = TaskLauncher(self.db, self.task_run, mock_data_array)
        launcher.create_assignments()

        self.assertEqual(
            len(launcher.assignments),
            len(mock_data_array),
            "Inequal number of assignments existed than were launched",
        )
        self.assertEqual(
            len(launcher.units),
            len(mock_data_array) * len(mock_data_array[0]["unit_data"]),
            "Inequal number of units created than were expected",
        )

        for unit in launcher.units:
            self.assertEqual(unit.get_db_status(), AssignmentState.CREATED)
        for assignment in launcher.assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.CREATED)

        launcher.launch_units("dummy-url:3000")

        for unit in launcher.units:
            self.assertEqual(unit.get_db_status(), AssignmentState.LAUNCHED)
        for assignment in launcher.assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.LAUNCHED)

        launcher.expire_units()

        for unit in launcher.units:
            self.assertEqual(unit.get_db_status(), AssignmentState.EXPIRED)
        for assignment in launcher.assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.EXPIRED)


if __name__ == "__main__":
    unittest.main()
