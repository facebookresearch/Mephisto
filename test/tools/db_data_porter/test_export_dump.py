#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import ClassVar
from typing import Type
from unittest.mock import patch

import pytest

from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner
from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import Agent
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.task_run import TaskRun
from mephisto.tools.db_data_porter.dumps import prepare_full_dump_data
from mephisto.tools.db_data_porter.export_dump import _export_data_dir_for_task_runs
from mephisto.tools.db_data_porter.export_dump import _rename_dirs_with_new_pks
from mephisto.tools.db_data_porter.export_dump import _rename_single_dir_with_new_pk
from mephisto.tools.db_data_porter.export_dump import archive_and_copy_data_files
from mephisto.tools.db_data_porter.export_dump import get_export_options_for_metadata
from mephisto.tools.db_data_porter.export_dump import make_tmp_export_dir
from mephisto.tools.db_data_porter.export_dump import unarchive_data_files
from mephisto.utils import db as db_utils
from mephisto.utils.testing import get_test_agent
from mephisto.utils.testing import get_test_assignment
from mephisto.utils.testing import get_test_requester
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_unit
from mephisto.utils.testing import get_test_worker


class MockClickContext:
    class Command:
        class Param:
            def __init__(self, data: dict):
                for k, v in data.items():
                    setattr(self, k, v)

        def __init__(self):
            params_dicts = [
                {
                    "opts": ["-d", "--debug"],
                    "name": "debug",
                },
                {
                    "opts": ["-tn", "--export-tasks-by-names"],
                    "name": "export_tasks_by_names",
                },
            ]

            self.params = [self.Param(p) for p in params_dicts]

    command = Command()


@pytest.mark.db_data_porter
class TestExportDump(unittest.TestCase):
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

    @patch("mephisto.tools.db_data_porter.export_dump.get_mephisto_tmp_dir")
    def test_make_tmp_export_dir(self, mock_get_mephisto_tmp_dir, *args):
        mock_get_mephisto_tmp_dir.return_value = self.data_dir

        result = make_tmp_export_dir()

        self.assertEqual(result, os.path.join(self.data_dir, "export"))
        self.assertTrue(os.path.exists(result))

    def test__rename_single_dir_with_new_pk(self, *args):
        original_id = "1"
        substitution_id = "999"

        original_dir_path = os.path.join(self.data_dir, str(original_id))
        expected_dir_path = os.path.join(self.data_dir, str(substitution_id))
        os.makedirs(original_dir_path, exist_ok=True)

        self.assertTrue(os.path.exists(original_dir_path))
        self.assertFalse(os.path.exists(expected_dir_path))

        result = _rename_single_dir_with_new_pk(original_dir_path, {original_id: substitution_id})

        self.assertFalse(os.path.exists(original_dir_path))
        self.assertTrue(os.path.exists(expected_dir_path))
        self.assertEqual(result, expected_dir_path)

    @patch("mephisto.tools.db_data_porter.export_dump._rename_single_dir_with_new_pk")
    def test__rename_dirs_with_new_pks_no_substitutions(
        self, mock__rename_single_dir_with_new_pk, *args,
    ):
        result = _rename_dirs_with_new_pks(task_run_dirs=[], pk_substitutions={})

        self.assertFalse(result)
        mock__rename_single_dir_with_new_pk.assert_not_called()

    def test__rename_dirs_with_new_pks_success(self, *args):
        pk_substitutions = {
            "mephisto": {
                "task_runs": {},
                "assignments": {},
                "agents": {},
            }
        }

        task_run_1_id_substitution = "1111"
        task_run_2_id_substitution = "2222"
        assignment_1_id_substitution = "3333"
        assignment_2_id_substitution = "4444"
        agent_1_id_substitution = "5555"
        agent_2_id_substitution = "6666"

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_id = get_test_task(self.db)
        _, worker_id = get_test_worker(self.db)
        task_run_1_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        assignment_1_id = get_test_assignment(self.db, task_run=task_run_1)
        assignment_2_id = get_test_assignment(self.db, task_run=task_run_2)
        assignment_1 = Assignment.get(self.db, assignment_1_id)
        assignment_2 = Assignment.get(self.db, assignment_2_id)
        unit_1_id = get_test_unit(self.db, 0, assignment=assignment_1)
        unit_2_id = get_test_unit(self.db, 0, assignment=assignment_2)
        agent_1_id = get_test_agent(self.db, unit_id=unit_1_id, worker_id=worker_id)
        agent_2_id = get_test_agent(self.db, unit_id=unit_2_id, worker_id=worker_id)
        agent_1 = Agent.get(self.db, agent_1_id)
        agent_2 = Agent.get(self.db, agent_2_id)

        pk_substitutions["mephisto"]["task_runs"][task_run_1_id] = task_run_1_id_substitution
        pk_substitutions["mephisto"]["task_runs"][task_run_2_id] = task_run_2_id_substitution
        pk_substitutions["mephisto"]["assignments"][assignment_1_id] = assignment_1_id_substitution
        pk_substitutions["mephisto"]["assignments"][assignment_2_id] = assignment_2_id_substitution
        pk_substitutions["mephisto"]["agents"][agent_1_id] = agent_1_id_substitution
        pk_substitutions["mephisto"]["agents"][agent_2_id] = agent_2_id_substitution

        # Create TaskRun dirs
        task_run_1_dir_before = task_run_1.get_run_dir()
        task_run_2_dir_before = task_run_2.get_run_dir()
        # Create Assignment dirs
        assignment_data = MockTaskRunner.get_mock_assignment_data()
        assignment_1.write_assignment_data(assignment_data)
        assignment_2.write_assignment_data(assignment_data)
        assignmen_1_dir_before = os.path.join(task_run_1_dir_before, assignment_1_id)
        assignmen_2_dir_before = os.path.join(task_run_2_dir_before, assignment_2_id)
        # Create Agent dirs
        agent_1.state.save_data()
        agent_2.state.save_data()
        agent_1_dir_before = os.path.join(assignmen_1_dir_before, agent_1_id)
        agent_2_dir_before = os.path.join(assignmen_2_dir_before, agent_2_id)

        self.assertTrue(os.path.exists(agent_1_dir_before))
        self.assertTrue(os.path.exists(agent_2_dir_before))

        result = _rename_dirs_with_new_pks(
            task_run_dirs=[
                task_run_1_dir_before,
                task_run_2_dir_before,
            ],
            pk_substitutions=pk_substitutions,
        )

        runs_dir = os.path.dirname(task_run_1_dir_before)

        agent_1_dir_after = os.path.join(
            runs_dir,
            task_run_1_id_substitution,
            assignment_1_id_substitution,
            agent_1_id_substitution,
        )
        agent_2_dir_after = os.path.join(
            runs_dir,
            task_run_2_id_substitution,
            assignment_2_id_substitution,
            agent_2_id_substitution,
        )

        self.assertTrue(result)
        self.assertFalse(os.path.exists(task_run_1_dir_before))
        self.assertFalse(os.path.exists(task_run_2_dir_before))
        self.assertFalse(os.path.exists(assignmen_1_dir_before))
        self.assertFalse(os.path.exists(assignmen_2_dir_before))
        self.assertFalse(os.path.exists(agent_1_dir_before))
        self.assertFalse(os.path.exists(agent_2_dir_before))
        self.assertTrue(os.path.exists(agent_1_dir_after))
        self.assertTrue(os.path.exists(agent_2_dir_after))

    @patch("mephisto.tools.db_data_porter.export_dump._rename_dirs_with_new_pks")
    @patch("mephisto.tools.db_data_porter.export_dump.make_tmp_export_dir")
    def test__export_data_dir_for_task_runs_no_task_runs(
        self, mock_make_tmp_export_dir, mock__rename_dirs_with_new_pks, *args,
    ):
        tmp_export_dir = os.path.join(self.data_dir, "tmp")
        input_dir_path = os.path.join(self.data_dir, "data")
        archive_file_path_without_ext = os.path.join(self.data_dir, "test_archive")

        os.makedirs(tmp_export_dir, exist_ok=True)

        mock_make_tmp_export_dir.return_value = tmp_export_dir

        result = _export_data_dir_for_task_runs(
            input_dir_path=input_dir_path,
            archive_file_path_without_ext=archive_file_path_without_ext,
            task_runs=[],
            pk_substitutions={},
        )

        self.assertFalse(result)
        mock__rename_dirs_with_new_pks.assert_not_called()

    @patch("mephisto.tools.db_data_porter.export_dump.make_tmp_export_dir")
    def test__export_data_dir_for_task_runs_with_pk_substitutions(
        self, mock_make_tmp_export_dir, *args,
    ):
        pk_substitutions = {
            "mephisto": {
                "task_runs": {},
                "assignments": {},
                "agents": {},
            }
        }

        task_run_1_id_substitution = "1111"
        task_run_2_id_substitution = "2222"

        tmp_export_dir = os.path.join(self.data_dir, "tmp")
        input_dir_path = os.path.join(self.data_dir, "data")
        archive_file_path_without_ext = os.path.join(self.data_dir, "test_archive")
        archive_file_path = f'{archive_file_path_without_ext}.zip'

        os.makedirs(tmp_export_dir, exist_ok=True)

        mock_make_tmp_export_dir.return_value = tmp_export_dir

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_id = get_test_task(self.db)
        task_run_1_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)

        task_run_1_dir_before = task_run_1.get_run_dir()
        task_run_2_dir_before = task_run_2.get_run_dir()

        pk_substitutions["mephisto"]["task_runs"][task_run_1_id] = task_run_1_id_substitution
        pk_substitutions["mephisto"]["task_runs"][task_run_2_id] = task_run_2_id_substitution

        self.assertTrue(os.path.exists(tmp_export_dir))
        self.assertFalse(os.path.exists(archive_file_path))

        result = _export_data_dir_for_task_runs(
            input_dir_path=input_dir_path,
            archive_file_path_without_ext=archive_file_path_without_ext,
            task_runs=[task_run_1, task_run_2],
            pk_substitutions=pk_substitutions,
        )

        self.assertTrue(result)
        self.assertFalse(os.path.exists(tmp_export_dir))
        self.assertTrue(os.path.exists(archive_file_path))
        self.assertTrue(os.path.exists(task_run_1_dir_before))
        self.assertTrue(os.path.exists(task_run_2_dir_before))

        with zipfile.ZipFile(archive_file_path) as archive:
            archive_runs_dir = Path(task_run_1_dir_before).relative_to(input_dir_path).parent
            archive_dirs = archive.namelist()

            archive_task_run_1_dir = f"{archive_runs_dir / task_run_1_id_substitution}/"
            archive_task_run_2_dir = f"{archive_runs_dir / task_run_2_id_substitution}/"

            self.assertIn(archive_task_run_1_dir, archive_dirs)
            self.assertIn(archive_task_run_2_dir, archive_dirs)

    @patch("mephisto.tools.db_data_porter.export_dump.make_tmp_export_dir")
    def test__export_data_dir_for_task_runs_without_pk_substitutions(
        self, mock_make_tmp_export_dir, *args,
    ):
        tmp_export_dir = os.path.join(self.data_dir, "tmp")
        input_dir_path = os.path.join(self.data_dir, "data")
        archive_file_path_without_ext = os.path.join(self.data_dir, "test_archive")
        archive_file_path = f'{archive_file_path_without_ext}.zip'

        os.makedirs(tmp_export_dir, exist_ok=True)

        mock_make_tmp_export_dir.return_value = tmp_export_dir

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_id = get_test_task(self.db)
        task_run_1_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)

        task_run_1_dir_before = task_run_1.get_run_dir()
        task_run_2_dir_before = task_run_2.get_run_dir()

        self.assertTrue(os.path.exists(tmp_export_dir))
        self.assertFalse(os.path.exists(archive_file_path))

        result = _export_data_dir_for_task_runs(
            input_dir_path=input_dir_path,
            archive_file_path_without_ext=archive_file_path_without_ext,
            task_runs=[task_run_1, task_run_2],
            pk_substitutions={},
        )

        self.assertTrue(result)
        self.assertFalse(os.path.exists(tmp_export_dir))
        self.assertTrue(os.path.exists(archive_file_path))
        self.assertTrue(os.path.exists(task_run_1_dir_before))
        self.assertTrue(os.path.exists(task_run_2_dir_before))

        with zipfile.ZipFile(archive_file_path) as archive:
            archive_dirs = archive.namelist()

            archive_task_run_1_dir = f"{Path(task_run_1_dir_before).relative_to(input_dir_path)}/"
            archive_task_run_2_dir = f"{Path(task_run_1_dir_before).relative_to(input_dir_path)}/"

            self.assertIn(archive_task_run_1_dir, archive_dirs)
            self.assertIn(archive_task_run_2_dir, archive_dirs)

    @patch("mephisto.tools.db_data_porter.export_dump.get_data_dir")
    def test_archive_and_copy_data_files_full(self, mock_get_data_dir, *args):
        pk_substitutions = {
            "mephisto": {
                "task_runs": {},
                "assignments": {},
                "agents": {},
            }
        }

        task_run_1_id_substitution = "1111"
        task_run_2_id_substitution = "2222"
        assignment_1_id_substitution = "3333"
        assignment_2_id_substitution = "4444"
        agent_1_id_substitution = "5555"
        agent_2_id_substitution = "6666"

        dump_name = "test_dump_name"

        data_dir = os.path.join(self.data_dir, "data")
        export_dir = os.path.join(self.data_dir, "export")

        mock_get_data_dir.return_value = self.data_dir

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_id = get_test_task(self.db)
        _, worker_id = get_test_worker(self.db)
        task_run_1_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        assignment_1_id = get_test_assignment(self.db, task_run=task_run_1)
        assignment_2_id = get_test_assignment(self.db, task_run=task_run_2)
        assignment_1 = Assignment.get(self.db, assignment_1_id)
        assignment_2 = Assignment.get(self.db, assignment_2_id)
        unit_1_id = get_test_unit(self.db, 0, assignment=assignment_1)
        unit_2_id = get_test_unit(self.db, 0, assignment=assignment_2)
        agent_1_id = get_test_agent(self.db, unit_id=unit_1_id, worker_id=worker_id)
        agent_2_id = get_test_agent(self.db, unit_id=unit_2_id, worker_id=worker_id)
        agent_1 = Agent.get(self.db, agent_1_id)
        agent_2 = Agent.get(self.db, agent_2_id)

        pk_substitutions["mephisto"]["task_runs"][task_run_1_id] = task_run_1_id_substitution
        pk_substitutions["mephisto"]["task_runs"][task_run_2_id] = task_run_2_id_substitution
        pk_substitutions["mephisto"]["assignments"][assignment_1_id] = assignment_1_id_substitution
        pk_substitutions["mephisto"]["assignments"][assignment_2_id] = assignment_2_id_substitution
        pk_substitutions["mephisto"]["agents"][agent_1_id] = agent_1_id_substitution
        pk_substitutions["mephisto"]["agents"][agent_2_id] = agent_2_id_substitution

        # Create TaskRun dirs
        task_run_1_dir_before = task_run_1.get_run_dir()
        task_run_2_dir_before = task_run_2.get_run_dir()
        # Create Assignment dirs
        assignment_data = MockTaskRunner.get_mock_assignment_data()
        assignment_1.write_assignment_data(assignment_data)
        assignment_2.write_assignment_data(assignment_data)
        # Create Agent dirs
        agent_1.state.save_data()
        agent_2.state.save_data()

        provider_datastores = db_utils.get_providers_datastores(self.db)
        full_dump = prepare_full_dump_data(db=self.db, provider_datastores=provider_datastores)

        result = archive_and_copy_data_files(
            db=self.db,
            export_dir=export_dir,
            dump_name=dump_name,
            dump_data=full_dump,
            pk_substitutions=pk_substitutions,
        )

        archive_file_path = os.path.join(export_dir, f"{dump_name}.zip")

        self.assertTrue(result)
        self.assertTrue(os.path.exists(archive_file_path))

        with zipfile.ZipFile(archive_file_path) as archive:
            archive_runs_dir = Path(task_run_1_dir_before).relative_to(data_dir).parent
            archive_dirs = archive.namelist()

            archive_agent_1_dir = str(
                archive_runs_dir /
                task_run_1_id_substitution /
                assignment_1_id_substitution /
                agent_1_id_substitution
            ) + "/"
            archive_agent_2_dir = str(
                archive_runs_dir /
                task_run_2_id_substitution /
                assignment_2_id_substitution /
                agent_2_id_substitution
            ) + "/"

            self.assertIn(archive_agent_1_dir, archive_dirs)
            self.assertIn(archive_agent_2_dir, archive_dirs)

    def test_unarchive_data_files(self, *args):
        dump_name = "test_dump_name"

        export_dir = os.path.join(self.data_dir, "export")

        # Create entries in Mephisto DB
        _, requester_id = get_test_requester(self.db)
        _, task_id = get_test_task(self.db)
        _, worker_id = get_test_worker(self.db)
        task_run_1_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_2_id = get_test_task_run(self.db, task_id=task_id, requester_id=requester_id)
        task_run_1 = TaskRun.get(self.db, task_run_1_id)
        task_run_2 = TaskRun.get(self.db, task_run_2_id)
        assignment_1_id = get_test_assignment(self.db, task_run=task_run_1)
        assignment_2_id = get_test_assignment(self.db, task_run=task_run_2)
        assignment_1 = Assignment.get(self.db, assignment_1_id)
        assignment_2 = Assignment.get(self.db, assignment_2_id)
        unit_1_id = get_test_unit(self.db, 0, assignment=assignment_1)
        unit_2_id = get_test_unit(self.db, 0, assignment=assignment_2)
        agent_1_id = get_test_agent(self.db, unit_id=unit_1_id, worker_id=worker_id)
        agent_2_id = get_test_agent(self.db, unit_id=unit_2_id, worker_id=worker_id)
        agent_1 = Agent.get(self.db, agent_1_id)
        agent_2 = Agent.get(self.db, agent_2_id)

        # Create TaskRun dirs
        task_run_1_dir_before = task_run_1.get_run_dir()
        task_run_2_dir_before = task_run_2.get_run_dir()
        # Create Assignment dirs
        assignment_data = MockTaskRunner.get_mock_assignment_data()
        assignment_1.write_assignment_data(assignment_data)
        assignment_2.write_assignment_data(assignment_data)
        # Create Agent dirs
        agent_1.state.save_data()
        agent_2.state.save_data()

        # Prepare archive
        provider_datastores = db_utils.get_providers_datastores(self.db)
        full_dump = prepare_full_dump_data(db=self.db, provider_datastores=provider_datastores)
        with patch("mephisto.tools.db_data_porter.export_dump.get_data_dir") as mock_get_data_dir:
            mock_get_data_dir.return_value = self.data_dir
            archive_and_copy_data_files(
                db=self.db,
                export_dir=export_dir,
                dump_name=dump_name,
                dump_data=full_dump,
                pk_substitutions={},
            )

        archive_file_path = os.path.join(export_dir, f"{dump_name}.zip")
        unarchive_data_dir = os.path.join(self.data_dir, "unarchive")

        os.makedirs(unarchive_data_dir, exist_ok=True)

        self.assertTrue(os.path.exists(archive_file_path))
        self.assertEqual(os.listdir(unarchive_data_dir), [])

        with (
            patch("mephisto.tools.db_data_porter.export_dump.get_data_dir") as mock_get_data_dir,
            patch(
                "mephisto.tools.db_data_porter.export_dump.get_mephisto_tmp_dir"
            ) as mock_get_mephisto_tmp_dir,
        ):
            tmp_dir = os.path.join(self.data_dir, "tmp")
            mock_get_mephisto_tmp_dir.return_value = tmp_dir
            mock_get_data_dir.return_value = unarchive_data_dir

            relative_runs_dir = Path(task_run_1_dir_before).relative_to(self.data_dir).parent

            archive_agent_1_dir = os.path.join(
                unarchive_data_dir,
                relative_runs_dir,
                task_run_1_id,
                assignment_1_id,
                agent_1_id,
            )
            archive_agent_2_dir = os.path.join(
                unarchive_data_dir,
                relative_runs_dir,
                task_run_2_id,
                assignment_2_id,
                agent_2_id,
            )

            self.assertFalse(os.path.exists(archive_agent_1_dir))
            self.assertFalse(os.path.exists(archive_agent_2_dir))
            self.assertFalse(os.path.exists(os.path.join(tmp_dir, "unarchive")))

            unarchive_data_files(dump_file_path=archive_file_path)

            self.assertTrue(os.path.exists(archive_agent_1_dir))
            self.assertTrue(os.path.exists(archive_agent_2_dir))
            self.assertFalse(os.path.exists(os.path.join(tmp_dir, "unarchive")))

    def test_get_export_options_for_metadata(self, *args):
        click_context = MockClickContext()
        options = dict(
            debug=True,
            export_tasks_by_names=["task_name_1", "task_name_2"],
        )

        result = get_export_options_for_metadata(click_context, options)

        self.assertEqual(
            result,
            {
                "-d/--debug": True,
                "-tn/--export-tasks-by-names": ["task_name_1", "task_name_2"],
            },
        )
