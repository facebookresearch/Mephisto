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
from datetime import timedelta
from typing import ClassVar
from typing import Type
from unittest.mock import patch

import pytest

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import TABLE_NAMES_RELATED_TO_QUALIFICATIONS
from mephisto.tools.db_data_porter.dumps import _make_options_error_message
from mephisto.tools.db_data_porter.dumps import delete_exported_data
from mephisto.tools.db_data_porter.dumps import prepare_full_dump_data
from mephisto.tools.db_data_porter.dumps import prepare_partial_dump_data
from mephisto.tools.db_data_porter.dumps import prepare_qualification_related_dump_data
from mephisto.utils import db as db_utils
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_requester
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from mephisto.utils.testing import make_completed_unit


@pytest.mark.db_data_porter
class TestDumps(unittest.TestCase):
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

    def test__make_options_error_message_without_available_values(self, *args):
        title = "Test title"
        values = ["Value 1", "Value 2"]
        not_found_values = ["Not found value 1", "Not found value 2"]
        available_values = None
        result = _make_options_error_message(
            title=title,
            values=values,
            not_found_values=not_found_values,
            available_values=available_values,
        )

        self.assertEqual(
            result,
            (
                f"[red]"
                f"You provided incorrect {title}. \n"
                f"Provided {len(values)} values: "
                f"{values[0]}, {values[1]}. \n"
                f"Not found {len(not_found_values)} values: "
                f"{not_found_values[0]}, {not_found_values[1]}."
                f"[/red]"
            ),
        )

    def test__make_options_error_message_with_available_values(self, *args):
        title = "Test title"
        values = ["Value 1", "Value 2"]
        not_found_values = ["Not found value 1", "Not found value 2"]
        available_values = ["Available value 1", "Available value 2"]
        result = _make_options_error_message(
            title=title,
            values=values,
            not_found_values=not_found_values,
            available_values=available_values,
        )

        self.assertEqual(
            result,
            (
                f"[red]"
                f"You provided incorrect {title}. \n"
                f"Provided {len(values)} values: "
                f"{values[0]}, {values[1]}. \n"
                f"Not found {len(not_found_values)} values: "
                f"{not_found_values[0]}, {not_found_values[1]}.\n"
                f"There are {len(available_values)} available values: "
                f"{available_values[0]}, {available_values[1]}"
                f"[/red]"
            ),
        )

    def test_prepare_partial_dump_data_task_names_task_with_all_relations(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_partial_dump_data(
            db=self.db,
            task_names=[task_name_2],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 1)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["units"]), 1)
        self.assertEqual(result["mephisto"]["units"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["agents"]), 1)
        self.assertEqual(result["mephisto"]["agents"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_2)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 1)
        self.assertEqual(result["mephisto"]["workers"][0]["worker_id"], worker_id)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 1)
        self.assertEqual(result["mephisto"]["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertEqual(
            result["mephisto"]["granted_qualifications"][0]["qualification_id"],
            qualification_id,
        )

        self.assertEqual(len(result["mephisto"]["qualifications"]), 1)
        self.assertEqual(
            result["mephisto"]["qualifications"][0]["qualification_id"],
            qualification_id,
        )

    def test_prepare_partial_dump_data_task_names_task_with_no_relations(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_partial_dump_data(
            db=self.db,
            task_names=[task_name_1],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_1_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_1_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 0)

        self.assertEqual(len(result["mephisto"]["units"]), 0)

        self.assertEqual(len(result["mephisto"]["agents"]), 0)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_1_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_1)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 0)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 0)

        self.assertEqual(len(result["mephisto"]["qualifications"]), 0)

    def test_prepare_partial_dump_data_task_ids_task_with_all_relations(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_partial_dump_data(
            db=self.db,
            task_ids=[task_2_id],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 1)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["units"]), 1)
        self.assertEqual(result["mephisto"]["units"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["agents"]), 1)
        self.assertEqual(result["mephisto"]["agents"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_2)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 1)
        self.assertEqual(result["mephisto"]["workers"][0]["worker_id"], worker_id)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 1)
        self.assertEqual(result["mephisto"]["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertEqual(
            result["mephisto"]["granted_qualifications"][0]["qualification_id"],
            qualification_id,
        )

        self.assertEqual(len(result["mephisto"]["qualifications"]), 1)
        self.assertEqual(
            result["mephisto"]["qualifications"][0]["qualification_id"],
            qualification_id,
        )

    def test_prepare_partial_dump_data_task_ids_task_with_no_relations(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_partial_dump_data(
            db=self.db,
            task_ids=[task_1_id],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_1_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_1_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 0)

        self.assertEqual(len(result["mephisto"]["units"]), 0)

        self.assertEqual(len(result["mephisto"]["agents"]), 0)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_1_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_1)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 0)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 0)

        self.assertEqual(len(result["mephisto"]["qualifications"]), 0)

    def test_prepare_partial_dump_data_task_run_ids_task_with_all_relations(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_partial_dump_data(
            db=self.db,
            task_run_ids=[task_run_2_id],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 1)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["units"]), 1)
        self.assertEqual(result["mephisto"]["units"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["agents"]), 1)
        self.assertEqual(result["mephisto"]["agents"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_2)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 1)
        self.assertEqual(result["mephisto"]["workers"][0]["worker_id"], worker_id)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 1)
        self.assertEqual(result["mephisto"]["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertEqual(
            result["mephisto"]["granted_qualifications"][0]["qualification_id"],
            qualification_id,
        )

        self.assertEqual(len(result["mephisto"]["qualifications"]), 1)
        self.assertEqual(
            result["mephisto"]["qualifications"][0]["qualification_id"],
            qualification_id,
        )

    def test_prepare_partial_dump_data_task_run_ids_task_with_no_relations(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_partial_dump_data(
            db=self.db,
            task_run_ids=[task_run_1_id],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_1_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_1_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 0)

        self.assertEqual(len(result["mephisto"]["units"]), 0)

        self.assertEqual(len(result["mephisto"]["agents"]), 0)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_1_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_1)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 0)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 0)

        self.assertEqual(len(result["mephisto"]["qualifications"]), 0)

    def test_prepare_partial_dump_data_task_run_labels(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
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
                unique_field_values=f'["{task_run_2_id}"]',
            ),
        )

        result = prepare_partial_dump_data(
            db=self.db,
            task_run_labels=[test_label],
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 1)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["units"]), 1)
        self.assertEqual(result["mephisto"]["units"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["agents"]), 1)
        self.assertEqual(result["mephisto"]["agents"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_2)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 1)
        self.assertEqual(result["mephisto"]["workers"][0]["worker_id"], worker_id)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 1)
        self.assertEqual(result["mephisto"]["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertEqual(
            result["mephisto"]["granted_qualifications"][0]["qualification_id"],
            qualification_id,
        )

        self.assertEqual(len(result["mephisto"]["qualifications"]), 1)
        self.assertEqual(
            result["mephisto"]["qualifications"][0]["qualification_id"],
            qualification_id,
        )

    def test_prepare_partial_dump_data_since_datetime(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        since_task_run_2_created = task_run_2.creation_date - timedelta(milliseconds=1)

        result = prepare_partial_dump_data(
            db=self.db,
            since_datetime=since_task_run_2_created,
        )

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
            [
                "agents",
                "assignments",
                "granted_qualifications",
                "onboarding_agents",
                "projects",
                "qualifications",
                "requesters",
                "task_runs",
                "tasks",
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        self.assertEqual(len(result["mephisto"]["task_runs"]), 1)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["task_run_id"], task_run_2_id)
        self.assertEqual(result["mephisto"]["task_runs"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["assignments"]), 1)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["units"]), 1)
        self.assertEqual(result["mephisto"]["units"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["agents"]), 1)
        self.assertEqual(result["mephisto"]["agents"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["tasks"]), 1)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["tasks"][0]["task_name"], task_name_2)

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 1)
        self.assertEqual(result["mephisto"]["workers"][0]["worker_id"], worker_id)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 1)
        self.assertEqual(result["mephisto"]["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertEqual(
            result["mephisto"]["granted_qualifications"][0]["qualification_id"],
            qualification_id,
        )

        self.assertEqual(len(result["mephisto"]["qualifications"]), 1)
        self.assertEqual(
            result["mephisto"]["qualifications"][0]["qualification_id"],
            qualification_id,
        )

    def test_prepare_full_dump_data(self, *args):
        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)
        provider_datastores = db_utils.get_providers_datastores(self.db)

        result = prepare_full_dump_data(db=self.db, provider_datastores=provider_datastores)

        self.assertIn("mephisto", result)
        self.assertIn("mephisto", result)
        self.assertEqual(
            sorted(list(result["mephisto"].keys())),
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
                "unit_review",
                "units",
                "workers",
            ],
        )
        self.assertEqual(sorted(list(result["mock"].keys())), ["requesters", "units", "workers"])

        task_runs = result["mephisto"]["task_runs"]
        self.assertEqual(len(task_runs), 2)
        self.assertEqual(
            sorted([task_runs[0]["task_id"], task_runs[1]["task_id"]]),
            sorted([task_1_id, task_2_id]),
        )
        self.assertEqual(
            sorted([task_runs[0]["task_run_id"], task_runs[1]["task_run_id"]]),
            sorted([task_run_1_id, task_run_2_id]),
        )
        self.assertEqual(
            {task_runs[0]["requester_id"], task_runs[1]["requester_id"]}, {requester_id}
        )

        self.assertEqual(len(result["mephisto"]["assignments"]), 1)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["assignments"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["units"]), 1)
        self.assertEqual(result["mephisto"]["units"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["units"][0]["task_run_id"], task_run_2_id)

        self.assertEqual(len(result["mephisto"]["agents"]), 1)
        self.assertEqual(result["mephisto"]["agents"][0]["unit_id"], unit_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_id"], task_2_id)
        self.assertEqual(result["mephisto"]["agents"][0]["task_run_id"], task_run_2_id)

        tasks = result["mephisto"]["tasks"]
        self.assertEqual(len(tasks), 2)
        self.assertEqual(
            sorted([tasks[0]["task_id"], tasks[1]["task_id"]]), sorted([task_1_id, task_2_id])
        )
        self.assertEqual(
            sorted([tasks[0]["task_name"], tasks[1]["task_name"]]),
            sorted([task_name_1, task_name_2]),
        )

        self.assertEqual(len(result["mephisto"]["requesters"]), 1)
        self.assertEqual(result["mephisto"]["requesters"][0]["requester_id"], requester_id)

        self.assertEqual(len(result["mephisto"]["workers"]), 1)
        self.assertEqual(result["mephisto"]["workers"][0]["worker_id"], worker_id)

        self.assertEqual(len(result["mephisto"]["granted_qualifications"]), 1)
        self.assertEqual(result["mephisto"]["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertEqual(
            result["mephisto"]["granted_qualifications"][0]["qualification_id"],
            qualification_id,
        )

        self.assertEqual(len(result["mephisto"]["qualifications"]), 1)
        self.assertEqual(
            result["mephisto"]["qualifications"][0]["qualification_id"],
            qualification_id,
        )

    @patch("mephisto.tools.db_data_porter.dumps.get_data_dir")
    def test_delete_exported_data_full(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        partial = False
        pk_substitutions = {}

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        # Create TaskRun dirs
        task_run_1.get_run_dir()
        task_run_2.get_run_dir()

        provider_datastores = db_utils.get_providers_datastores(self.db)

        full_dump = prepare_full_dump_data(db=self.db, provider_datastores=provider_datastores)

        table_names = db_utils.get_list_of_tables_to_export(self.db)

        self.assertIn("data", os.listdir(self.data_dir))
        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertTrue(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["imported_data", "onboarding_agents", "projects", "unit_review"]:
                self.assertEqual(len(rows), 0)
            else:
                self.assertGreater(len(rows), 0)

        delete_exported_data(
            db=self.db,
            pk_substitutions=pk_substitutions,
            dump_data_to_export=full_dump,
            partial=partial,
        )

        self.assertFalse(os.path.exists(task_run_1.get_run_dir()))
        self.assertFalse(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            self.assertEqual(len(rows), 0)

    @patch("mephisto.tools.db_data_porter.dumps.get_data_dir")
    def test_delete_exported_data_partial(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        partial = True
        delete_tasks = False
        pk_substitutions = {}

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        # Create TaskRun dirs
        task_run_1.get_run_dir()
        task_run_2.get_run_dir()

        partial_dump = prepare_partial_dump_data(db=self.db, task_run_ids=[task_run_2_id])

        table_names = db_utils.get_list_of_tables_to_export(self.db)

        self.assertIn("data", os.listdir(self.data_dir))
        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertTrue(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["imported_data", "onboarding_agents", "projects", "unit_review"]:
                self.assertEqual(len(rows), 0)
            else:
                self.assertGreater(len(rows), 0)

        delete_exported_data(
            db=self.db,
            pk_substitutions=pk_substitutions,
            dump_data_to_export=partial_dump,
            partial=partial,
            delete_tasks=delete_tasks,
        )

        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertFalse(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["requesters", "workers", "qualifications", "granted_qualifications"]:
                self.assertGreater(len(rows), 0)
            elif table_name == "tasks":
                self.assertEqual(len(rows), 2)  # Both Tasks were saved
            elif table_name == "task_runs":
                self.assertEqual(len(rows), 1)
            else:
                self.assertEqual(len(rows), 0)

    @patch("mephisto.tools.db_data_porter.dumps.get_data_dir")
    def test_delete_exported_data_delete_tasks(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        partial = True
        delete_tasks = True
        pk_substitutions = {}

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        # Create TaskRun dirs
        task_run_1.get_run_dir()
        task_run_2.get_run_dir()

        partial_dump = prepare_partial_dump_data(db=self.db, task_run_ids=[task_run_2_id])

        table_names = db_utils.get_list_of_tables_to_export(self.db)

        self.assertIn("data", os.listdir(self.data_dir))
        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertTrue(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["imported_data", "onboarding_agents", "projects", "unit_review"]:
                self.assertEqual(len(rows), 0)
            else:
                self.assertGreater(len(rows), 0)

        delete_exported_data(
            db=self.db,
            pk_substitutions=pk_substitutions,
            dump_data_to_export=partial_dump,
            partial=partial,
            delete_tasks=delete_tasks,
        )

        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertFalse(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["requesters", "workers", "qualifications", "granted_qualifications"]:
                self.assertGreater(len(rows), 0)
            elif table_name == "tasks":
                self.assertEqual(len(rows), 1)  # One related Task to the TaskRun was deleted
            elif table_name == "task_runs":
                self.assertEqual(len(rows), 1)
            else:
                self.assertEqual(len(rows), 0)

    @patch("mephisto.tools.db_data_porter.dumps.get_data_dir")
    def test_delete_exported_data_pk_substitutions(self, mock_get_data_dir, *args):
        mock_get_data_dir.return_value = self.data_dir

        partial = True
        delete_tasks = False
        pk_substitutions = {
            "mephisto": {
                "task_runs": {},
            }
        }

        task_run_1_id_substitution = "1"
        task_run_2_id_substitution = "2"

        task_name_1 = "task_name_1"
        task_name_2 = "task_name_2"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_1_id = get_test_task(self.db, task_name=task_name_1)
        _, task_2_id = get_test_task(self.db, task_name=task_name_2)
        task_run_1_id = get_test_task_run(self.db, task_id=task_1_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_2_id, requester_id=requester_id)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        pk_substitutions["mephisto"]["task_runs"][task_run_1_id] = task_run_1_id_substitution
        pk_substitutions["mephisto"]["task_runs"][task_run_2_id] = task_run_2_id_substitution

        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        # Create TaskRun dirs
        task_run_1.get_run_dir()
        task_run_2.get_run_dir()

        partial_dump = prepare_partial_dump_data(db=self.db, task_run_ids=[task_run_2_id])
        for task_run in partial_dump["mephisto"]["task_runs"]:
            task_run_id = task_run["task_run_id"]
            task_run["task_run_id"] = pk_substitutions["mephisto"]["task_runs"][task_run_id]

        table_names = db_utils.get_list_of_tables_to_export(self.db)

        self.assertIn("data", os.listdir(self.data_dir))
        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertTrue(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["imported_data", "onboarding_agents", "projects", "unit_review"]:
                self.assertEqual(len(rows), 0)
            else:
                self.assertGreater(len(rows), 0)

        delete_exported_data(
            db=self.db,
            pk_substitutions=pk_substitutions,
            dump_data_to_export=partial_dump,
            partial=partial,
            delete_tasks=delete_tasks,
        )

        self.assertTrue(os.path.exists(task_run_1.get_run_dir()))
        self.assertFalse(os.path.exists(task_run_2.get_run_dir()))
        for table_name in table_names:
            rows = db_utils.select_all_table_rows(self.db, table_name)
            if table_name in ["requesters", "workers", "qualifications", "granted_qualifications"]:
                self.assertGreater(len(rows), 0)
            elif table_name == "tasks":
                self.assertEqual(len(rows), 2)  # Both Tasks were saved
            elif table_name == "task_runs":
                self.assertEqual(len(rows), 1)
            else:
                self.assertEqual(len(rows), 0)

    def test_prepare_qualification_related_dump_data_without_qualification_names(self):
        _, worker_id = get_test_worker(self.db)
        qualification_id = get_test_qualification(self.db, "qual_1")
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        result = prepare_qualification_related_dump_data(self.db, qualification_names=None)

        self.assertIn(MEPHISTO_DUMP_KEY, result)
        self.assertEqual(
            len(result[MEPHISTO_DUMP_KEY].keys()), len(TABLE_NAMES_RELATED_TO_QUALIFICATIONS)
        )
        for _, table_value in result[MEPHISTO_DUMP_KEY].items():
            self.assertEqual(len(table_value), 1)

    def test_prepare_qualification_related_dump_data_with_qualification_names(self):
        qualification_1_name = "qual_1"
        qualification_2_name = "qual_2"

        _, worker_1_id = get_test_worker(self.db, "worker_1")
        _, worker_2_id = get_test_worker(self.db, "worker_2")
        qualification_1_id = get_test_qualification(self.db, qualification_1_name)
        qualification_2_id = get_test_qualification(self.db, qualification_2_name)
        grant_test_qualification(
            self.db, worker_id=worker_1_id, qualification_id=qualification_2_id
        )
        grant_test_qualification(
            self.db, worker_id=worker_2_id, qualification_id=qualification_2_id
        )

        # By first qualification
        result_1 = prepare_qualification_related_dump_data(
            self.db, qualification_names=[qualification_1_name]
        )

        self.assertIn(MEPHISTO_DUMP_KEY, result_1)
        self.assertEqual(
            len(result_1[MEPHISTO_DUMP_KEY].keys()), len(TABLE_NAMES_RELATED_TO_QUALIFICATIONS)
        )
        self.assertEqual(len(result_1[MEPHISTO_DUMP_KEY]["workers"]), 0)
        self.assertEqual(len(result_1[MEPHISTO_DUMP_KEY]["qualifications"]), 1)
        self.assertEqual(len(result_1[MEPHISTO_DUMP_KEY]["granted_qualifications"]), 0)

        # By second qualification
        result_2 = prepare_qualification_related_dump_data(
            self.db, qualification_names=[qualification_2_name]
        )

        self.assertIn(MEPHISTO_DUMP_KEY, result_2)
        self.assertEqual(
            len(result_2[MEPHISTO_DUMP_KEY].keys()), len(TABLE_NAMES_RELATED_TO_QUALIFICATIONS)
        )
        self.assertEqual(len(result_2[MEPHISTO_DUMP_KEY]["workers"]), 2)
        self.assertEqual(len(result_2[MEPHISTO_DUMP_KEY]["qualifications"]), 1)
        self.assertEqual(len(result_2[MEPHISTO_DUMP_KEY]["granted_qualifications"]), 2)

    def test_prepare_qualification_related_dump_data_non_existing_qualification_names(self):
        qualification_name = "qual_1"
        non_existing_qualification_name = "non_existing_qual"

        _, worker_id = get_test_worker(self.db)
        qualification_id = get_test_qualification(self.db, qualification_name)
        grant_test_qualification(self.db, worker_id=worker_id, qualification_id=qualification_id)

        with self.assertRaises(SystemExit) as cm:
            captured_print_output = io.StringIO()
            sys.stdout = captured_print_output
            prepare_qualification_related_dump_data(
                self.db, qualification_names=[qualification_name, non_existing_qualification_name]
            )
            sys.stdout = sys.__stdout__

        self.assertEqual(cm.exception.code, None)
        self.assertIn(
            "You passed non-existing qualification names", captured_print_output.getvalue()
        )
        self.assertIn(non_existing_qualification_name, captured_print_output.getvalue())
