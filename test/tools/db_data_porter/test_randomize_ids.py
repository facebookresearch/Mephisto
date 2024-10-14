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
from unittest.mock import ANY
from unittest.mock import patch

import pytest

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.randomize_ids import _randomize_ids_for_mephisto
from mephisto.tools.db_data_porter.randomize_ids import _randomize_ids_for_provider
from mephisto.tools.db_data_porter.randomize_ids import get_old_pk_from_substitutions
from mephisto.tools.db_data_porter.randomize_ids import randomize_ids
from mephisto.utils.db import SQLITE_ID_MAX
from mephisto.utils.db import SQLITE_ID_MIN
from mephisto.abstractions.providers.prolific.provider_type import (
    PROVIDER_TYPE as PROLIFIC_PROVIDER_TYPE,
)


@pytest.mark.db_data_porter
class TestRandomizeIds(unittest.TestCase):
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

    def test__randomize_ids_for_mephisto_legacy_only_true(self, *args):
        task_1_id = "1"
        task_2_id = "2222222222222222222"
        requester_id = "3"

        mephisto_dump = {
            "imported_data": [],
            "projects": [],
            "tasks": [
                {
                    "task_id": task_1_id,
                    "task_name": "test_task_1",
                    "task_type": "mock",
                    "project_id": None,
                    "parent_task_id": None,
                    "creation_date": "2024-05-01T00:00:00.000000",
                },
                {
                    "task_id": task_2_id,
                    "task_name": "test_task_2",
                    "task_type": "mock",
                    "project_id": None,
                    "parent_task_id": None,
                    "creation_date": "2024-05-01T00:00:00.000000",
                },
            ],
            "requesters": [
                {
                    "requester_id": requester_id,
                    "requester_name": "test_requester",
                    "provider_type": "mock",
                    "creation_date": "2024-05-01T00:00:00.000000",
                }
            ],
            "task_runs": [],
            "assignments": [],
            "units": [],
            "workers": [],
            "agents": [],
            "onboarding_agents": [],
            "qualifications": [],
            "granted_qualifications": [],
            "worker_review": [],
        }
        legacy_only = True

        result = _randomize_ids_for_mephisto(
            db=self.db,
            mephisto_dump=mephisto_dump,
            legacy_only=legacy_only,
        )

        new_task_1_id = int(result["tasks"][task_1_id])

        self.assertEqual(
            result,
            {
                "agents": {},
                "assignments": {},
                "granted_qualifications": {},
                "onboarding_agents": {},
                "projects": {},
                "qualifications": {},
                "requesters": {requester_id: ANY},
                "task_runs": {},
                "tasks": {task_1_id: ANY},
                "worker_review": {},
                "units": {},
                "workers": {},
            },
        )
        self.assertGreater(new_task_1_id, SQLITE_ID_MIN)
        self.assertLess(new_task_1_id, SQLITE_ID_MAX)
        self.assertEqual(len(result["tasks"].keys()), 1)
        self.assertEqual(len(result["requesters"].keys()), 1)

    def test__randomize_ids_for_mephisto_legacy_only_false(self, *args):
        task_1_id = "1"
        task_2_id = "2222222222222222222"
        requester_id = "3"

        mephisto_dump = {
            "imported_data": [],
            "projects": [],
            "tasks": [
                {
                    "task_id": task_1_id,
                    "task_name": "test_task_1",
                    "task_type": "mock",
                    "project_id": None,
                    "parent_task_id": None,
                    "creation_date": "2024-05-01T00:00:00.000000",
                },
                {
                    "task_id": task_2_id,
                    "task_name": "test_task_2",
                    "task_type": "mock",
                    "project_id": None,
                    "parent_task_id": None,
                    "creation_date": "2024-05-01T00:00:00.000000",
                },
            ],
            "requesters": [
                {
                    "requester_id": requester_id,
                    "requester_name": "test_requester",
                    "provider_type": "mock",
                    "creation_date": "2024-05-01T00:00:00.000000",
                }
            ],
            "task_runs": [],
            "assignments": [],
            "units": [],
            "workers": [],
            "agents": [],
            "onboarding_agents": [],
            "qualifications": [],
            "granted_qualifications": [],
            "worker_review": [],
        }
        legacy_only = False

        result = _randomize_ids_for_mephisto(
            db=self.db,
            mephisto_dump=mephisto_dump,
            legacy_only=legacy_only,
        )

        new_task_1_id = int(result["tasks"][task_1_id])

        self.assertEqual(
            result,
            {
                "agents": {},
                "assignments": {},
                "granted_qualifications": {},
                "onboarding_agents": {},
                "projects": {},
                "qualifications": {},
                "requesters": {requester_id: ANY},
                "task_runs": {},
                "tasks": {task_1_id: ANY, task_2_id: ANY},
                "worker_review": {},
                "units": {},
                "workers": {},
            },
        )
        self.assertGreater(new_task_1_id, SQLITE_ID_MIN)
        self.assertLess(new_task_1_id, SQLITE_ID_MAX)
        self.assertEqual(len(result["tasks"].keys()), 2)
        self.assertNotEqual(result["tasks"][task_2_id], task_2_id)
        self.assertEqual(len(result["requesters"].keys()), 1)

    @patch("mephisto.utils.db.make_randomized_int_id")
    def test__randomize_ids_for_provider_no_provider_dump(self, mock_make_randomized_int_id, *args):
        provider_type = PROLIFIC_PROVIDER_TYPE
        provider_dump = {}
        mephisto_pk_substitutions = {}

        result = _randomize_ids_for_provider(
            provider_type=provider_type,
            provider_dump=provider_dump,
            mephisto_pk_substitutions=mephisto_pk_substitutions,
        )

        self.assertIsNone(result)
        mock_make_randomized_int_id.assert_not_called()

    @patch("mephisto.utils.db.make_randomized_int_id")
    def test__randomize_ids_for_provider_undefined_provider_type(
        self,
        mock_make_randomized_int_id,
        *args,
    ):
        provider_type = "undefined_provider_type"
        provider_dump = {"test": "test"}
        mephisto_pk_substitutions = {}

        result = _randomize_ids_for_provider(
            provider_type=provider_type,
            provider_dump=provider_dump,
            mephisto_pk_substitutions=mephisto_pk_substitutions,
        )

        self.assertIsNone(result)
        mock_make_randomized_int_id.assert_not_called()

    def test__randomize_ids_for_provider_success(self, *args):
        provider_type = PROLIFIC_PROVIDER_TYPE

        task_id = "1"
        task_id_substitution = "1111111111111111111"
        task_run_id = "2"
        task_run_id_substitution = "2222222222222222222"
        unit_id = "3"
        unit_id_substitution = "3333333333333333333"
        prolific_unit_id = "4"

        init_provider_dump = {
            "units": [
                {
                    "id": prolific_unit_id,
                    "unit_id": unit_id,
                    "task_run_id": task_run_id,
                    "prolific_study_id": "test_study_id",
                    "prolific_submission_id": "test_submission_id",
                    "is_expired": False,
                    "creation_date": "2024-05-01T00:00:00.000000",
                },
            ],
            "participant_groups": [],
            "qualifications": [],
            "run_mappings": [],
            "runs": [],
            "studies": [],
            "submissions": [],
            "workers": [],
        }

        mephisto_pk_substitutions = {
            "agents": {},
            "assignments": {},
            "granted_qualifications": {},
            "onboarding_agents": {},
            "projects": {},
            "qualifications": {},
            "requesters": {},
            "task_runs": {task_run_id: task_run_id_substitution},
            "tasks": {task_id: task_id_substitution},
            "worker_review": {},
            "units": {unit_id: unit_id_substitution},
            "workers": {},
        }

        provider_dump = deepcopy(init_provider_dump)

        self.assertEqual(provider_dump, init_provider_dump)

        result = _randomize_ids_for_provider(
            provider_type=provider_type,
            provider_dump=provider_dump,
            mephisto_pk_substitutions=mephisto_pk_substitutions,
        )

        self.assertNotEqual(provider_dump, init_provider_dump)
        self.assertNotEqual(provider_dump["units"][0]["id"], unit_id)
        self.assertEqual(provider_dump["units"][0]["unit_id"], unit_id_substitution)
        self.assertEqual(provider_dump["units"][0]["task_run_id"], task_run_id_substitution)
        self.assertEqual(
            result,
            {
                "participant_groups": {},
                "qualifications": {},
                "run_mappings": {},
                "runs": {},
                "studies": {},
                "submissions": {},
                "units": {prolific_unit_id: ANY},
                "workers": {},
            },
        )
        self.assertNotEqual(result["units"][prolific_unit_id], prolific_unit_id)

    def test_randomize_ids_success(self, *args):
        task_id = "1"
        task_run_id = "2"
        unit_id = "3"
        requester_id = "4"
        prolific_unit_id = "5"

        full_dump = {
            MEPHISTO_DUMP_KEY: {
                "imported_data": [],
                "projects": [],
                "tasks": [
                    {
                        "task_id": task_id,
                        "task_name": "test_task_1",
                        "task_type": "mock",
                        "project_id": None,
                        "parent_task_id": None,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    },
                ],
                "requesters": [
                    {
                        "requester_id": requester_id,
                        "requester_name": "test_requester",
                        "provider_type": PROLIFIC_PROVIDER_TYPE,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    },
                ],
                "task_runs": [
                    {
                        "task_run_id": task_run_id,
                        "task_id": task_id,
                        "requester_id": requester_id,
                        "init_params": "",
                        "is_completed": 0,
                        "provider_type": PROLIFIC_PROVIDER_TYPE,
                        "task_type": "mock",
                        "sandbox": 1,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    },
                ],
                "assignments": [],
                "units": [
                    {
                        "unit_id": unit_id,
                        "assignment_id": "1",
                        "unit_index": 0,
                        "pay_amount": 10,
                        "provider_type": PROLIFIC_PROVIDER_TYPE,
                        "status": "completed",
                        "agent_id": None,
                        "worker_id": "1",
                        "task_type": "mock",
                        "task_id": task_id,
                        "task_run_id": task_run_id,
                        "sandbox": 1,
                        "requester_id": requester_id,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    },
                ],
                "workers": [],
                "agents": [],
                "onboarding_agents": [],
                "qualifications": [],
                "granted_qualifications": [],
                "worker_review": [],
            },
            PROLIFIC_PROVIDER_TYPE: {
                "units": [
                    {
                        "id": prolific_unit_id,
                        "unit_id": unit_id,
                        "task_run_id": task_run_id,
                        "prolific_study_id": "test_study_id",
                        "prolific_submission_id": "test_submission_id",
                        "is_expired": False,
                        "creation_date": "2024-05-01T00:00:00.000000",
                    },
                ],
                "participant_groups": [],
                "qualifications": [],
                "run_mappings": [],
                "runs": [],
                "studies": [],
                "submissions": [],
                "workers": [],
            },
        }

        result = randomize_ids(
            db=self.db,
            full_dump=full_dump,
            legacy_only=True,
        )

        mephisto_pk_substitutions = result["pk_substitutions"][MEPHISTO_DUMP_KEY]
        prolific_pk_substitutions = result["pk_substitutions"][PROLIFIC_PROVIDER_TYPE]
        mephisto_updated_dump = result["updated_dump"][MEPHISTO_DUMP_KEY]
        prolific_updated_dump = result["updated_dump"][PROLIFIC_PROVIDER_TYPE]

        self.assertEqual(
            result,
            {
                "pk_substitutions": {
                    MEPHISTO_DUMP_KEY: {
                        "projects": {},
                        "tasks": {task_id: ANY},
                        "requesters": {requester_id: ANY},
                        "task_runs": {task_run_id: ANY},
                        "assignments": {},
                        "units": {unit_id: ANY},
                        "workers": {},
                        "agents": {},
                        "onboarding_agents": {},
                        "qualifications": {},
                        "granted_qualifications": {},
                        "worker_review": {},
                    },
                    PROLIFIC_PROVIDER_TYPE: {
                        "participant_groups": {},
                        "qualifications": {},
                        "run_mappings": {},
                        "runs": {},
                        "studies": {},
                        "submissions": {},
                        "units": {prolific_unit_id: ANY},
                        "workers": {},
                    },
                },
                "updated_dump": {
                    MEPHISTO_DUMP_KEY: {
                        "imported_data": [],
                        "projects": [],
                        "tasks": [
                            {
                                "task_id": ANY,
                                "task_name": "test_task_1",
                                "task_type": "mock",
                                "project_id": None,
                                "parent_task_id": None,
                                "creation_date": "2024-05-01T00:00:00.000000",
                            }
                        ],
                        "requesters": [
                            {
                                "requester_id": ANY,
                                "requester_name": "test_requester",
                                "provider_type": PROLIFIC_PROVIDER_TYPE,
                                "creation_date": "2024-05-01T00:00:00.000000",
                            }
                        ],
                        "task_runs": [
                            {
                                "task_run_id": ANY,
                                "task_id": ANY,
                                "requester_id": ANY,
                                "init_params": "",
                                "is_completed": 0,
                                "provider_type": PROLIFIC_PROVIDER_TYPE,
                                "task_type": "mock",
                                "sandbox": 1,
                                "creation_date": "2024-05-01T00:00:00.000000",
                            }
                        ],
                        "assignments": [],
                        "units": [
                            {
                                "unit_id": ANY,
                                "assignment_id": "1",
                                "unit_index": 0,
                                "pay_amount": 10,
                                "provider_type": PROLIFIC_PROVIDER_TYPE,
                                "status": "completed",
                                "agent_id": None,
                                "worker_id": "1",
                                "task_type": "mock",
                                "task_id": ANY,
                                "task_run_id": ANY,
                                "sandbox": 1,
                                "requester_id": ANY,
                                "creation_date": "2024-05-01T00:00:00.000000",
                            }
                        ],
                        "workers": [],
                        "agents": [],
                        "onboarding_agents": [],
                        "qualifications": [],
                        "granted_qualifications": [],
                        "worker_review": [],
                    },
                    PROLIFIC_PROVIDER_TYPE: {
                        "units": [
                            {
                                "id": ANY,
                                "unit_id": ANY,
                                "task_run_id": ANY,
                                "prolific_study_id": "test_study_id",
                                "prolific_submission_id": "test_submission_id",
                                "is_expired": False,
                                "creation_date": "2024-05-01T00:00:00.000000",
                            }
                        ],
                        "participant_groups": [],
                        "qualifications": [],
                        "run_mappings": [],
                        "runs": [],
                        "studies": [],
                        "submissions": [],
                        "workers": [],
                    },
                },
            },
        )
        self.assertNotEqual(mephisto_pk_substitutions["tasks"][task_id], task_id)
        self.assertNotEqual(mephisto_pk_substitutions["task_runs"][task_run_id], task_run_id)
        self.assertNotEqual(mephisto_pk_substitutions["requesters"][requester_id], requester_id)
        self.assertNotEqual(mephisto_pk_substitutions["units"][unit_id], unit_id)

        self.assertNotEqual(prolific_pk_substitutions["units"][prolific_unit_id], prolific_unit_id)

        self.assertNotEqual(mephisto_updated_dump["tasks"][0]["task_id"], task_id)
        self.assertNotEqual(mephisto_updated_dump["task_runs"][0]["task_run_id"], task_run_id)
        self.assertNotEqual(mephisto_updated_dump["requesters"][0]["requester_id"], requester_id)
        self.assertNotEqual(mephisto_updated_dump["units"][0]["unit_id"], unit_id)

        self.assertNotEqual(prolific_updated_dump["units"][0]["id"], prolific_unit_id)

    def test_get_old_pk_from_substitutions(self, *args):
        task_id = "1"
        task_id_substitution = "1111111111111111111"
        pk_substitutions = {
            MEPHISTO_DUMP_KEY: {
                "tasks": {task_id: task_id_substitution},
            },
        }

        result = get_old_pk_from_substitutions(
            pk=task_id_substitution,
            pk_substitutions=pk_substitutions,
            table_name="tasks",
        )

        self.assertEqual(result, task_id)
