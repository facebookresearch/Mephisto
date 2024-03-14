#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import tempfile
import unittest

from mephisto.data_model.constants.assignment_state import AssignmentState

from mephisto.data_model.assignment import Assignment
from mephisto.operations.unit_prioritizer import RandomAssignmentUnitPrioritizer
from mephisto.operations.unit_prioritizer import RandomUnitPrioritizer

from mephisto.utils.testing import get_test_assignment

from mephisto.data_model.unit import Unit
from mephisto.operations.unit_prioritizer import LIFOUnitPrioritizer

from mephisto.utils.testing import get_test_task_run

from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun
from mephisto.operations.unit_prioritizer import FIFOUnitPrioritizer
from mephisto.utils.testing import get_test_unit


class TestUnitPrioritizer(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.task_id = self.db.new_task("test_mock", MockBlueprint.BLUEPRINT_TYPE)
        self.task_run_id = get_test_task_run(self.db)
        self.task_run = TaskRun.get(self.db, self.task_run_id)

    def tearDown(self):
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_fifo(self):
        assignment_id = get_test_assignment(self.db, task_run=self.task_run)
        assignment = Assignment.get(self.db, assignment_id)

        units = [
            Unit.get(self.db, get_test_unit(self.db, unit_index=i, assignment=assignment))
            for i in range(5)
        ]
        first_unit_id = units[0].db_id
        reserved_unit = FIFOUnitPrioritizer(task_run=self.task_run).reserve_unit(units)

        self.assertEqual(reserved_unit.db_id, first_unit_id)

    def test_lifo(self):
        assignment_id = get_test_assignment(self.db, task_run=self.task_run)
        assignment = Assignment.get(self.db, assignment_id)

        units = [
            Unit.get(self.db, get_test_unit(self.db, unit_index=i, assignment=assignment))
            for i in range(5)
        ]
        last_unit_id = units[-1].db_id
        reserved_unit = LIFOUnitPrioritizer(task_run=self.task_run).reserve_unit(units)

        self.assertEqual(reserved_unit.db_id, last_unit_id)

    def test_random(self):
        assignment_id = get_test_assignment(self.db, task_run=self.task_run)
        assignment = Assignment.get(self.db, assignment_id)

        random_unit_indices = []
        for y in range(10):
            units = [
                Unit.get(self.db, get_test_unit(self.db, unit_index=y*10+i, assignment=assignment))
                for i in range(5)
            ]
            unit_ids = [u.db_id for u in units]
            reserved_unit = RandomUnitPrioritizer(task_run=self.task_run).reserve_unit(units)
            random_unit_indices.append(unit_ids.index(reserved_unit.db_id))

        self.assertNotEqual(len(set(random_unit_indices)), 1)
        self.assertTrue(any([i != 0 for i in random_unit_indices]))

    def test_random_assignment(self):
        assignments = [
            Assignment.get(self.db, get_test_assignment(self.db, task_run=self.task_run))
            for _ in range(5)
        ]
        assignment_ids = [a.db_id for a in assignments]
        unit_ids_by_assignments = {}

        all_units = []

        random_assignment_indices = []
        unit_indices = []

        # Create all available units for all assignments
        for y, assignment in enumerate(assignments):
            units = [
                Unit.get(self.db, get_test_unit(self.db, unit_index=y*10+i, assignment=assignment))
                for i in range(5)
            ]
            for unit in units:
                unit: Unit
                unit.set_db_status(AssignmentState.LAUNCHED)

            unit_ids_by_assignments[assignment.db_id] = [u.db_id for u in units]

            all_units += units

        # Reserve units
        for _ in range(10):
            reserved_unit = RandomAssignmentUnitPrioritizer(
                task_run=self.task_run,
            ).reserve_unit(all_units)
            random_assignment_indices.append(
                assignment_ids.index(reserved_unit.get_assignment().db_id)
            )
            assignment_id = reserved_unit.get_assignment().db_id

            unit_indices.append(
                unit_ids_by_assignments[assignment_id].index(reserved_unit.db_id)
            )

        # As Assignments are getting randomly,
        # they can be repeated and their Units can be reserved more than one time.
        # In this case, index of Unit in the Assignment Units equals
        # the amount of Assignment ID appearance
        expected_unit_indices = []
        for i, assignment_index in enumerate(random_assignment_indices):
            expected_unit_indices.append(random_assignment_indices[:i].count(assignment_index))

        self.assertTrue(any([i != 0 for i in random_assignment_indices]))
        self.assertEqual(unit_indices, expected_unit_indices)


if __name__ == "__main__":
    unittest.main()
