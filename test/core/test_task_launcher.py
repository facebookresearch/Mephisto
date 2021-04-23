#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile
from typing import List, Iterable
import time

from mephisto.abstractions.test.utils import get_test_task_run
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.operations.task_launcher import TaskLauncher
from mephisto.data_model.assignment import InitializationData
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task_run import TaskRun

from mephisto.abstractions.providers.mock.mock_provider import MockProvider
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner

MAX_WAIT_TIME_UNIT_LAUNCH = 15
NUM_GENERATED_ASSIGNMENTS = 10
WAIT_TIME_TILL_NEXT_ASSIGNMENT = 1
WAIT_TIME_TILL_NEXT_UNIT = 0.01


class LimitedDict(dict):
    def __init__(self, limit):
        self.limit = limit
        self.exceed_limit = False
        super().__init__()

    def __setitem__(self, key, value):
        if len(self.keys()) > self.limit:
            self.exceed_limit = True
        super().__setitem__(key, value)


class BaseTestTaskLauncher:
    """
    Unit testing for the Mephisto TaskLauncher
    """

    DB_CLASS = None

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)
        self.task_run_id = get_test_task_run(self.db)
        self.task_run = TaskRun(self.db, self.task_run_id)

    def tearDown(self):
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    @staticmethod
    def get_mock_assignment_data_array() -> List[InitializationData]:
        return [MockTaskRunner.get_mock_assignment_data()]

    @staticmethod
    def get_mock_assignment_data_generator() -> Iterable[InitializationData]:
        for _ in range(NUM_GENERATED_ASSIGNMENTS):
            yield MockTaskRunner.get_mock_assignment_data()
            time.sleep(WAIT_TIME_TILL_NEXT_ASSIGNMENT)

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
            len(mock_data_array) * len(mock_data_array[0].unit_data),
            "Inequal number of units created than were expected",
        )

        for unit in launcher.units:
            self.assertEqual(unit.get_db_status(), AssignmentState.CREATED)
        for assignment in launcher.assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.CREATED)

        launcher.launch_units("dummy-url:3000")

        for unit in launcher.units:
            self.assertEqual(unit.get_db_status(), AssignmentState.LAUNCHED)
            time.sleep(WAIT_TIME_TILL_NEXT_UNIT)
        for assignment in launcher.assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.LAUNCHED)

        launcher.expire_units()

        for unit in launcher.units:
            self.assertEqual(unit.get_db_status(), AssignmentState.EXPIRED)
        for assignment in launcher.assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.EXPIRED)

    def test_launch_assignments_with_concurrent_unit_cap(self):
        """Initialize a launcher on a task run, then create the assignments"""
        cap_values = [1, 2, 3, 4, 5]
        for max_num_units in cap_values:
            mock_data_array = self.get_mock_assignment_data_array()
            launcher = TaskLauncher(
                self.db,
                self.task_run,
                mock_data_array,
                max_num_concurrent_units=max_num_units,
            )
            launcher.launched_units = LimitedDict(launcher.max_num_concurrent_units)
            launcher.create_assignments()
            launcher.launch_units("dummy-url:3000")

            start_time = time.time()
            while set([u.get_status() for u in launcher.units]) != {
                AssignmentState.COMPLETED
            }:
                for unit in launcher.units:
                    if unit.get_status() == AssignmentState.LAUNCHED:
                        unit.set_db_status(AssignmentState.COMPLETED)
                    time.sleep(0.1)
                self.assertEqual(launcher.launched_units.exceed_limit, False)
                curr_time = time.time()
                self.assertLessEqual(curr_time - start_time, MAX_WAIT_TIME_UNIT_LAUNCH)
            launcher.expire_units()
            self.tearDown()
            self.setUp()

    def test_assignments_generator(self):
        """Initialize a launcher on a task run, then try generate the assignments"""
        mock_data_array = self.get_mock_assignment_data_generator()

        start_time = time.time()
        launcher = TaskLauncher(self.db, self.task_run, mock_data_array)
        launcher.create_assignments()
        end_time = time.time()
        self.assertLessEqual(
            end_time - start_time,
            (NUM_GENERATED_ASSIGNMENTS * WAIT_TIME_TILL_NEXT_ASSIGNMENT) / 2,
        )


class TestTaskLauncherLocal(BaseTestTaskLauncher, unittest.TestCase):
    DB_CLASS = LocalMephistoDB


class TestTaskLauncherSingleton(BaseTestTaskLauncher, unittest.TestCase):
    DB_CLASS = MephistoSingletonDB


if __name__ == "__main__":
    unittest.main()
