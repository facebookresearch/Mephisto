#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import unittest
from dataclasses import dataclass
from dataclasses import field
from unittest.mock import patch
from uuid import uuid4

import pytest

from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.api.data_models import User
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificRequestError
from mephisto.abstractions.providers.prolific.prolific_utils import _find_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import check_credentials
from mephisto.abstractions.providers.prolific.prolific_utils import create_study
from mephisto.abstractions.providers.prolific.prolific_utils import find_or_create_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import setup_credentials
from mephisto.data_model.requester import RequesterArgs
from mephisto.data_model.task_run import TaskRunArgs

MOCK_PROLIFIC_CONFIG_DIR = '/tmp/'
MOCK_PROLIFIC_CONFIG_PATH = '/tmp/test_conf_credentials'


@dataclass
class MockProlificRequesterArgs(RequesterArgs):
    name: str = field(
        default='prolific',
    )
    api_key: str = field(
        default='prolific',
    )


mock_task_run_args = TaskRunArgs(
    task_title='title',
    task_description='This is a description',
    task_reward=0.3,
    task_tags='1,2,3',
    task_lifetime_in_seconds=1,
)


@pytest.mark.prolific
class TestProlificUtils(unittest.TestCase):
    """Unit testing for Prolific Utils"""
    @staticmethod
    def remove_credentials_file():
        if os.path.exists(MOCK_PROLIFIC_CONFIG_PATH):
            os.remove(MOCK_PROLIFIC_CONFIG_PATH)

    @patch('mephisto.abstractions.providers.prolific.api.users.Users.me')
    def test_check_credentials_true(self, mock_prolific_users_me, *args):
        mock_prolific_users_me.return_value = User(id='test')
        result = check_credentials()
        self.assertTrue(result)

    @patch('mephisto.abstractions.providers.prolific.api.users.Users.me')
    def test_check_credentials_false(self, mock_prolific_users_me, *args):
        mock_prolific_users_me.side_effect = ProlificRequestError()
        result = check_credentials()
        self.assertFalse(result)

    @patch(
        'mephisto.abstractions.providers.prolific.prolific_utils.CREDENTIALS_CONFIG_DIR',
        MOCK_PROLIFIC_CONFIG_DIR,
    )
    @patch(
        'mephisto.abstractions.providers.prolific.prolific_utils.CREDENTIALS_CONFIG_PATH',
        MOCK_PROLIFIC_CONFIG_PATH,
    )
    def test_setup_credentials(self, *args):
        self.remove_credentials_file()
        self.assertFalse(os.path.exists(MOCK_PROLIFIC_CONFIG_PATH))
        cfg = MockProlificRequesterArgs()
        setup_credentials('name', cfg)
        self.assertTrue(os.path.exists(MOCK_PROLIFIC_CONFIG_PATH))
        self.remove_credentials_file()

    @patch('mephisto.abstractions.providers.prolific.api.participant_groups.ParticipantGroups.list')
    def test_find_qualification_success(self, mock_participant_groups_list, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = 'test'
        qualification_description = 'test'
        expected_qualification_id = uuid4().hex[:24]
        mock_participant_groups_list.return_value = [
            ParticipantGroup(
                project_id=prolific_project_id,
                id=expected_qualification_id,
                name=qualification_name,
                description=qualification_description,
            )
        ]
        _, q = _find_qualification(prolific_api, prolific_project_id, qualification_name)
        self.assertEqual(q.id, expected_qualification_id)

    @patch('mephisto.abstractions.providers.prolific.api.participant_groups.ParticipantGroups.list')
    def test_find_qualification_no_qualification(self, mock_participant_groups_list, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = 'test'
        mock_participant_groups_list.return_value = []
        result = _find_qualification(prolific_api, prolific_project_id, qualification_name)
        self.assertEqual(result, (True, None))

    @patch('mephisto.abstractions.providers.prolific.api.participant_groups.ParticipantGroups.list')
    def test_find_qualification_error(self, mock_participant_groups_list, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = 'test'
        exception_message = 'Error'
        mock_participant_groups_list.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            _find_qualification(prolific_api, prolific_project_id, qualification_name)
        self.assertEqual(cm.exception.message, exception_message)

    @patch('mephisto.abstractions.providers.prolific.prolific_utils._find_qualification')
    def test_find_or_create_qualification_found_one(self, mock_find_qualification, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = 'test'
        expected_qualification_id = uuid4().hex[:24]
        mock_find_qualification.return_value = (True, expected_qualification_id)
        result = find_or_create_qualification(
            prolific_api, prolific_project_id, qualification_name,
        )
        self.assertEqual(result.id, expected_qualification_id)

    @patch(
        'mephisto.abstractions.providers.prolific.api.participant_groups.ParticipantGroups.create'
    )
    @patch('mephisto.abstractions.providers.prolific.prolific_utils._find_qualification')
    def test_find_or_create_qualification_created_new(
        self, mock_find_qualification, mock_participant_groups_create, *args,
    ):
        qualification_name = 'test'
        qualification_description = 'test'
        expected_qualification_id = uuid4().hex[:24]
        mock_find_qualification.return_value = (False, None)
        mock_participant_groups_create.return_value = ParticipantGroup(
            id=expected_qualification_id,
            name=qualification_name,
            description=qualification_description,
        )
        result = find_or_create_qualification(
            prolific_api, qualification_name, qualification_description,
        )
        self.assertEqual(result.id, expected_qualification_id)

    @patch(
        'mephisto.abstractions.providers.prolific.api.participant_groups.ParticipantGroups.create'
    )
    @patch('mephisto.abstractions.providers.prolific.prolific_utils._find_qualification')
    def test_find_or_create_qualification_error(
        self, mock_find_qualification, mock_participant_groups_create, *args,
    ):
        qualification_name = 'test'
        qualification_description = 'test'
        mock_find_qualification.return_value = (False, None)
        exception_message = 'Error'
        mock_participant_groups_create.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            find_or_create_qualification(
                prolific_api, qualification_name, qualification_description,
            )
        self.assertEqual(cm.exception.message, exception_message)

    @patch('mephisto.abstractions.providers.prolific.api.studies.Studies.create')
    def test_create_study_success(self, mock_study_create, *args):
        project_id = uuid4().hex[:24]
        expected_task_id = uuid4().hex[:24]
        mock_study_create.return_value = Study(
            project=project_id,
            id=expected_task_id,
            name='test',
        )
        study = create_study(
            client=prolific_api,
            task_run_config=mock_task_run_args,
            prolific_project_id=project_id,
        )
        self.assertEqual(study.id, expected_task_id)

    @patch('mephisto.abstractions.providers.prolific.api.studies.Studies.create')
    def test_create_study_error(self, mock_study_create, *args):
        project_id = uuid4().hex[:24]
        exception_message = 'Error'
        mock_study_create.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            create_study(
                client=prolific_api,
                task_run_config=mock_task_run_args,
                prolific_project_id=project_id,
            )
        self.assertEqual(cm.exception.message, exception_message)


if __name__ == "__main__":
    unittest.main()
