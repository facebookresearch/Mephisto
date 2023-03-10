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
import surge
from surge.errors import SurgeRequestError

from mephisto.abstractions.providers.surge_ai.surge_ai_utils import check_credentials
from mephisto.abstractions.providers.surge_ai.surge_ai_utils import create_project
from mephisto.abstractions.providers.surge_ai.surge_ai_utils import find_or_create_qualification
from mephisto.abstractions.providers.surge_ai.surge_ai_utils import find_qualification
from mephisto.abstractions.providers.surge_ai.surge_ai_utils import setup_credentials
from mephisto.data_model.requester import RequesterArgs
from mephisto.data_model.task_run import TaskRunArgs

MOCK_SURGE_AI_CONFIG_DIR = '/tmp/'
MOCK_SURGE_AI_CONFIG_PATH = '/tmp/test_conf_credentials'


@dataclass
class MockSurgeAIRequesterArgs(RequesterArgs):
    name: str = field(
        default='surge_ai',
    )
    api_key: str = field(
        default='test_key',
    )


mock_task_run_args = TaskRunArgs(
    task_title='title',
    task_description='This is a description',
    task_reward=0.3,
    task_tags='1,2,3',
    maximum_units_per_worker=2,
    allowed_concurrent=1,
    task_name='max-unit-test',
)


@pytest.mark.surge_ai
class TestSurgeAIUtils(unittest.TestCase):
    """Unit testing for Aurge AI Utils"""
    @staticmethod
    def remove_credentials_file():
        if os.path.exists(MOCK_SURGE_AI_CONFIG_PATH):
            os.remove(MOCK_SURGE_AI_CONFIG_PATH)

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Project.list')
    def test_check_credentials_true(self, mock_surge_project_list, *args):
        mock_surge_project_list.return_value = []
        result = check_credentials()
        self.assertTrue(result)

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Project.list')
    def test_check_credentials_false(self, mock_surge_project_list, *args):
        mock_surge_project_list.side_effect = SurgeRequestError()
        result = check_credentials()
        self.assertFalse(result)

    @patch(
        'mephisto.abstractions.providers.surge_ai.surge_ai_utils.SURGE_AI_CONFIG_DIR',
        MOCK_SURGE_AI_CONFIG_DIR,
    )
    @patch(
        'mephisto.abstractions.providers.surge_ai.surge_ai_utils.SURGE_AI_CONFIG_PATH',
        MOCK_SURGE_AI_CONFIG_PATH,
    )
    def test_setup_credentials(self, *args):
        self.remove_credentials_file()
        self.assertFalse(os.path.exists(MOCK_SURGE_AI_CONFIG_PATH))
        cfg = MockSurgeAIRequesterArgs()
        setup_credentials('name', cfg)
        self.assertTrue(os.path.exists(MOCK_SURGE_AI_CONFIG_PATH))
        self.remove_credentials_file()

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Team.list')
    def test_find_qualification_success(self, mock_surge_team_list, *args):
        qualification_name = 'test'
        qualification_description = 'test'
        expected_qualification_id = uuid4()
        mock_surge_team_list.return_value = [
            surge.Team(
                id=str(expected_qualification_id),
                name=qualification_name,
                description=qualification_description,
            )
        ]
        result = find_qualification(surge, qualification_name)
        self.assertEqual(result, (True, str(expected_qualification_id)))

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Team.list')
    def test_find_qualification_no_qualification(self, mock_surge_team_list, *args):
        qualification_name = 'test'
        mock_surge_team_list.return_value = []
        result = find_qualification(surge, qualification_name)
        self.assertEqual(result, (True, None))

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Team.list')
    def test_find_qualification_error(self, mock_surge_team_list, *args):
        qualification_name = 'test'
        exception_message = 'Error'
        mock_surge_team_list.side_effect = SurgeRequestError(exception_message)
        with self.assertRaises(SurgeRequestError) as cm:
            find_qualification(surge, qualification_name)
        self.assertEqual(cm.exception.message, exception_message)

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.find_qualification')
    def test_find_or_create_qualification_found_one(self, mock_find_qualification, *args):
        qualification_name = 'test'
        qualification_description = 'test'
        expected_qualification_id = uuid4()
        mock_find_qualification.return_value = (True, str(expected_qualification_id))
        result = find_or_create_qualification(surge, qualification_name, qualification_description)
        self.assertEqual(result, str(expected_qualification_id))

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Team.create')
    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.find_qualification')
    def test_find_or_create_qualification_created_new(
        self, mock_find_qualification, mock_surge_team_create, *args,
    ):
        qualification_name = 'test'
        qualification_description = 'test'
        expected_qualification_id = uuid4()
        mock_find_qualification.return_value = (False, None)
        mock_surge_team_create.return_value = surge.Team(
            id=str(expected_qualification_id),
            name=qualification_name,
            description=qualification_description,
        )
        result = find_or_create_qualification(surge, qualification_name, qualification_description)
        self.assertEqual(result, str(expected_qualification_id))

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Team.create')
    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.find_qualification')
    def test_find_or_create_qualification_error(
        self, mock_find_qualification, mock_surge_team_create, *args,
    ):
        qualification_name = 'test'
        qualification_description = 'test'
        mock_find_qualification.return_value = (False, None)
        exception_message = 'Error'
        mock_surge_team_create.side_effect = SurgeRequestError(exception_message)
        with self.assertRaises(SurgeRequestError) as cm:
            find_or_create_qualification(surge, qualification_name, qualification_description)
        self.assertEqual(cm.exception.message, exception_message)

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Project.create')
    def test_create_project_success(self, mock_surge_project_create, *args):
        expected_project_id = uuid4()
        mock_surge_project_create.return_value = surge.Project(
            id=str(expected_project_id),
            name='test'
        )
        result = create_project(
            client=surge,
            task_args=mock_task_run_args,
            qualifications=[{'surge_ai_qualification_id': str(uuid4())}],
        )
        self.assertEqual(result, str(expected_project_id))

    @patch('mephisto.abstractions.providers.surge_ai.surge_ai_utils.surge.Project.create')
    def test_create_project_error(self, mock_surge_project_create, *args):
        exception_message = 'Error'
        mock_surge_project_create.side_effect = SurgeRequestError(exception_message)
        with self.assertRaises(SurgeRequestError) as cm:
            create_project(
                client=surge,
                task_args=mock_task_run_args,
                qualifications=[{'surge_ai_qualification_id': str(uuid4())}],
            )
        self.assertEqual(cm.exception.message, exception_message)


if __name__ == "__main__":
    unittest.main()
