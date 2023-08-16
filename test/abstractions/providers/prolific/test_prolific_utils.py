#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import unittest
from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from unittest.mock import patch
from uuid import uuid4

import pytest
from omegaconf import DictConfig

from mephisto.abstractions.providers.prolific.api import constants
from mephisto.abstractions.providers.prolific.api.data_models import BonusPayments
from mephisto.abstractions.providers.prolific.api.data_models import ListSubmission
from mephisto.abstractions.providers.prolific.api.data_models import Participant
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup
from mephisto.abstractions.providers.prolific.api.data_models import Project
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.api.data_models import Submission
from mephisto.abstractions.providers.prolific.api.data_models import User
from mephisto.abstractions.providers.prolific.api.data_models import Workspace
from mephisto.abstractions.providers.prolific.api.data_models import WorkspaceBalance
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificRequestError
from mephisto.abstractions.providers.prolific.prolific_utils import (
    _convert_eligibility_requirements,
)
from mephisto.abstractions.providers.prolific.prolific_utils import _ec2_external_url
from mephisto.abstractions.providers.prolific.prolific_utils import _find_prolific_project
from mephisto.abstractions.providers.prolific.prolific_utils import _find_prolific_workspace
from mephisto.abstractions.providers.prolific.prolific_utils import _find_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import _find_submission
from mephisto.abstractions.providers.prolific.prolific_utils import _get_block_list_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import _get_external_study_url
from mephisto.abstractions.providers.prolific.prolific_utils import _is_ec2_architect
from mephisto.abstractions.providers.prolific.prolific_utils import add_workers_to_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import approve_work
from mephisto.abstractions.providers.prolific.prolific_utils import block_worker
from mephisto.abstractions.providers.prolific.prolific_utils import calculate_pay_amount
from mephisto.abstractions.providers.prolific.prolific_utils import check_balance
from mephisto.abstractions.providers.prolific.prolific_utils import check_credentials
from mephisto.abstractions.providers.prolific.prolific_utils import create_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import create_study
from mephisto.abstractions.providers.prolific.prolific_utils import delete_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import expire_study
from mephisto.abstractions.providers.prolific.prolific_utils import find_or_create_prolific_project
from mephisto.abstractions.providers.prolific.prolific_utils import (
    find_or_create_prolific_workspace,
)
from mephisto.abstractions.providers.prolific.prolific_utils import find_or_create_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client
from mephisto.abstractions.providers.prolific.prolific_utils import get_study
from mephisto.abstractions.providers.prolific.prolific_utils import get_submission
from mephisto.abstractions.providers.prolific.prolific_utils import give_worker_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import (
    increase_total_available_places_for_study,
)
from mephisto.abstractions.providers.prolific.prolific_utils import is_study_expired
from mephisto.abstractions.providers.prolific.prolific_utils import is_worker_blocked
from mephisto.abstractions.providers.prolific.prolific_utils import pay_bonus
from mephisto.abstractions.providers.prolific.prolific_utils import publish_study
from mephisto.abstractions.providers.prolific.prolific_utils import reject_work
from mephisto.abstractions.providers.prolific.prolific_utils import remove_worker_qualification
from mephisto.abstractions.providers.prolific.prolific_utils import setup_credentials
from mephisto.abstractions.providers.prolific.prolific_utils import stop_study
from mephisto.abstractions.providers.prolific.prolific_utils import unblock_worker
from mephisto.data_model.requester import RequesterArgs

MOCK_PROLIFIC_CONFIG_DIR = "/tmp/"
MOCK_PROLIFIC_CONFIG_PATH = "/tmp/test_conf_credentials"

API_PATH = "mephisto.abstractions.providers.prolific.api"
UTILS_PATH = "mephisto.abstractions.providers.prolific.prolific_utils"


@dataclass
class MockProlificRequesterArgs(RequesterArgs):
    name: str = field(
        default="prolific",
    )
    api_key: str = field(
        default="prolific",
    )


mock_task_run_args = DictConfig(
    dict(
        architect=DictConfig(
            dict(
                _architect_type="local",
            )
        ),
        task=DictConfig(
            dict(
                task_title="title",
                task_description="This is a description",
                task_reward=0.3,
                task_tags="1,2,3",
                task_lifetime_in_seconds=1,
            )
        ),
        provider=DictConfig(
            dict(
                prolific_external_study_url=(
                    "https://example.com?"
                    "participant_id={{%PROLIFIC_PID%}}&"
                    "study_id={{%STUDY_ID%}}&"
                    "submission_id={{%SESSION_ID%}}"
                ),
                prolific_id_option="url_parameters",
                prolific_workspace_name="My Workspace",
                prolific_project_name="Project",
                prolific_allow_list_group_name="Allow list",
                prolific_block_list_group_name="Block list",
                prolific_estimated_completion_time_in_minutes=60,
            )
        ),
    )
)


@pytest.mark.prolific
class TestProlificUtils(unittest.TestCase):
    """Unit testing for Prolific Utils"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = get_authenticated_client("prolific")

    @staticmethod
    def remove_credentials_file():
        if os.path.exists(MOCK_PROLIFIC_CONFIG_PATH):
            os.remove(MOCK_PROLIFIC_CONFIG_PATH)

    @patch(f"{API_PATH}.users.Users.me")
    def test_check_credentials_true(self, mock_prolific_users_me, *args):
        mock_prolific_users_me.return_value = User(id="test")
        result = check_credentials()
        self.assertTrue(result)

    @patch(f"{API_PATH}.users.Users.me")
    def test_check_credentials_false(self, mock_prolific_users_me, *args):
        mock_prolific_users_me.side_effect = ProlificRequestError()
        result = check_credentials()
        self.assertFalse(result)

    @patch(f"{UTILS_PATH}.CREDENTIALS_CONFIG_DIR", MOCK_PROLIFIC_CONFIG_DIR)
    @patch(f"{UTILS_PATH}.CREDENTIALS_CONFIG_PATH", MOCK_PROLIFIC_CONFIG_PATH)
    def test_setup_credentials(self, *args):
        self.remove_credentials_file()
        self.assertFalse(os.path.exists(MOCK_PROLIFIC_CONFIG_PATH))
        cfg = MockProlificRequesterArgs()
        setup_credentials("name", cfg)
        self.assertTrue(os.path.exists(MOCK_PROLIFIC_CONFIG_PATH))
        self.remove_credentials_file()

    def test__convert_eligibility_requirements(self, *args):
        income_value = [
            {
                "name": "AgeRangeEligibilityRequirement",
                "min_age": 18,
                "max_age": 100,
            },
            {
                "name": "ApprovalNumbersEligibilityRequirement",
                "minimum_approvals": 1,
                "maximum_approvals": 100,
            },
            {
                "name": "ApprovalRateEligibilityRequirement",
                "minimum_approval_rate": 1,
                "maximum_approval_rate": 100,
            },
            {
                "name": "CustomBlacklistEligibilityRequirement",
                "black_list": ["54ac6ea9fdf99b2204feb893"],
            },
            {
                "name": "CustomWhitelistEligibilityRequirement",
                "white_list": ["54ac6ea9fdf99b2204feb893"],
            },
            {
                "name": "JoinedBeforeEligibilityRequirement",
                "joined_before": "2023‐08‐08T00:00:00Z",
            },
            {
                "name": "ParticipantGroupEligibilityRequirement",
                "id": "54ac6ea9fdf99b2204feb893",
            },
        ]
        result = _convert_eligibility_requirements(income_value)
        self.assertEqual(
            result,
            [
                {
                    "_cls": "web.eligibility.models.AgeRangeEligibilityRequirement",
                    "attributes": [
                        {"name": "min_age", "value": 18},
                        {"name": "max_age", "value": 100},
                    ],
                    "query": {"id": "54ac6ea9fdf99b2204feb893"},
                },
                {
                    "_cls": "web.eligibility.models.ApprovalNumbersEligibilityRequirement",
                    "attributes": [
                        {"name": "minimum_approvals", "value": 1},
                        {"name": "maximum_approvals", "value": 100},
                    ],
                },
                {
                    "_cls": "web.eligibility.models.ApprovalRateEligibilityRequirement",
                    "attributes": [
                        {"name": "minimum_approval_rate", "value": 1},
                        {"name": "maximum_approval_rate", "value": 100},
                    ],
                },
                {
                    "_cls": "web.eligibility.models.CustomBlacklistEligibilityRequirement",
                    "attributes": [
                        {"name": "black_list", "value": ["54ac6ea9fdf99b2204feb893"]},
                    ],
                },
                {
                    "_cls": "web.eligibility.models.CustomWhitelistEligibilityRequirement",
                    "attributes": [
                        {"name": "white_list", "value": ["54ac6ea9fdf99b2204feb893"]},
                    ],
                },
                {
                    "_cls": "web.eligibility.models.JoinedBeforeEligibilityRequirement",
                    "attributes": [
                        {"name": "joined_before", "value": "2023‐08‐08T00:00:00Z"},
                    ],
                },
                {
                    "_cls": "web.eligibility.models.ParticipantGroupEligibilityRequirement",
                    "attributes": [
                        {"id": "54ac6ea9fdf99b2204feb893", "value": True},
                    ],
                },
            ],
        )

    @patch(f"{API_PATH}.workspaces.Workspaces.get_balance")
    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_check_balance_success(self, mock__find_prolific_workspace, mock_get_balance, *args):
        expected_value = 9999

        mock_workspace = Workspace()
        mock_workspace.id = "test"
        mock_workspacebalance = WorkspaceBalance()
        mock_workspacebalance.available_balance = expected_value

        mock__find_prolific_workspace.return_value = (True, mock_workspace)
        mock_get_balance.return_value = mock_workspacebalance
        balance = check_balance(self.client, workspace_name="test")
        self.assertEqual(expected_value, balance)

    @patch(f"{API_PATH}.workspaces.Workspaces.get_balance")
    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_check_balance_no_workspace_name(self, *args):
        balance = check_balance(self.client)
        self.assertEqual(None, balance)

    @patch(f"{API_PATH}.workspaces.Workspaces.get_balance")
    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_check_balance_found_no_workspace(self, mock__find_prolific_workspace, *args):
        mock_workspace = Workspace()
        mock_workspace.id = "test"

        mock__find_prolific_workspace.return_value = (False, None)
        balance = check_balance(self.client, workspace_name="test")
        self.assertEqual(None, balance)

    @patch(f"{API_PATH}.workspaces.Workspaces.get_balance")
    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_check_balance_get_balance_exception(
        self,
        mock__find_prolific_workspace,
        mock_get_balance,
        *args,
    ):
        expected_value = 9999

        mock_workspace = Workspace()
        mock_workspace.id = "test"
        mock_workspacebalance = WorkspaceBalance()
        mock_workspacebalance.available_balance = expected_value

        mock__find_prolific_workspace.return_value = (True, mock_workspace)

        exception_message = "Error"
        mock_get_balance.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            check_balance(self.client, workspace_name="test")

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.workspaces.Workspaces.retrieve")
    def test__find_prolific_workspace_with_id_success(self, mock_retrieve, *args):
        expected_id = "test"
        expected_title = "test"

        mock_workspace = Workspace()
        mock_workspace.id = expected_id
        mock_workspace.title = expected_title

        mock_retrieve.return_value = mock_workspace

        result = _find_prolific_workspace(self.client, title="", id=expected_id)
        self.assertEqual((True, mock_workspace), result)

    @patch(f"{API_PATH}.workspaces.Workspaces.retrieve")
    def test__find_prolific_workspace_with_id_exception(self, mock_retrieve, *args):
        expected_id = "test"

        exception_message = "Error"
        mock_retrieve.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            _find_prolific_workspace(self.client, title="", id=expected_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.workspaces.Workspaces.list")
    def test__find_prolific_workspace_with_title_success(self, mock_list, *args):
        expected_title = "test"

        mock_workspace = Workspace()
        mock_workspace.title = expected_title

        mock_list.return_value = [mock_workspace]

        result = _find_prolific_workspace(self.client, title=expected_title)
        self.assertEqual((True, mock_workspace), result)

    @patch(f"{API_PATH}.workspaces.Workspaces.list")
    def test__find_prolific_workspace_with_title_success_no_result(self, mock_list, *args):
        expected_title = "test"

        mock_workspace = Workspace()
        mock_workspace.title = expected_title

        mock_list.return_value = []

        result = _find_prolific_workspace(self.client, title=expected_title)
        self.assertEqual((False, None), result)

    @patch(f"{API_PATH}.workspaces.Workspaces.list")
    def test__find_prolific_workspace_with_title_exception(self, mock_list, *args):
        expected_title = "test"

        exception_message = "Error"
        mock_list.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            _find_prolific_workspace(self.client, title=expected_title)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_find_or_create_prolific_workspace_success_find(
        self,
        mock__find_prolific_workspace,
        *args,
    ):
        expected_title = "test"

        mock_workspace = Workspace()
        mock_workspace.title = expected_title

        mock__find_prolific_workspace.return_value = (True, mock_workspace)

        result = find_or_create_prolific_workspace(self.client, expected_title)

        self.assertEqual(mock_workspace, result)

    @patch(f"{API_PATH}.workspaces.Workspaces.create")
    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_find_or_create_prolific_workspace_success_create(
        self,
        mock__find_prolific_workspace,
        mock_create,
        *args,
    ):
        expected_title = "test"

        mock_workspace = Workspace()
        mock_workspace.title = expected_title

        mock__find_prolific_workspace.return_value = (False, None)
        mock_create.return_value = mock_workspace

        result = find_or_create_prolific_workspace(self.client, expected_title)

        self.assertEqual(mock_workspace, result)

    @patch(f"{API_PATH}.workspaces.Workspaces.create")
    @patch(f"{UTILS_PATH}._find_prolific_workspace")
    def test_find_or_create_prolific_workspace_create_exception(
        self,
        mock__find_prolific_workspace,
        mock_create,
        *args,
    ):
        expected_title = "test"

        mock_workspace = Workspace()
        mock_workspace.title = expected_title

        mock__find_prolific_workspace.return_value = (False, None)

        exception_message = "Error"
        mock_create.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            find_or_create_prolific_workspace(self.client, expected_title)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.projects.Projects.list_for_workspace")
    def test__find_prolific_project_success_with_title(self, mock_list_for_workspace, *args):
        workspace_id = "test"
        project_title = "test2"

        mock_project = Project()
        mock_project.title = project_title

        mock_list_for_workspace.return_value = [mock_project]

        result = _find_prolific_project(self.client, workspace_id, project_title)

        self.assertEqual((True, mock_project), result)
        self.assertFalse(hasattr(mock_project, "id"))

    @patch(f"{API_PATH}.projects.Projects.list_for_workspace")
    def test__find_prolific_project_success_with_id(self, mock_list_for_workspace, *args):
        workspace_id = "test"
        project_title = "test2"
        project_id = "test3"

        mock_project = Project()
        mock_project.title = project_title
        mock_project.id = project_id

        mock_list_for_workspace.return_value = [mock_project]

        result = _find_prolific_project(self.client, workspace_id, project_title, project_id)

        self.assertEqual((True, mock_project), result)
        self.assertTrue(hasattr(mock_project, "id"))

    @patch(f"{API_PATH}.projects.Projects.list_for_workspace")
    def test__find_prolific_project_success_no_result(self, mock_list_for_workspace, *args):
        workspace_id = "test"
        project_title = "test2"

        mock_project = Project()
        mock_project.title = project_title

        mock_list_for_workspace.return_value = []

        result = _find_prolific_project(self.client, workspace_id, project_title)

        self.assertEqual((False, None), result)

    @patch(f"{API_PATH}.projects.Projects.list_for_workspace")
    def test__find_prolific_project_exception(self, mock_list_for_workspace, *args):
        workspace_id = "test"
        project_title = "test2"

        exception_message = "Error"
        mock_list_for_workspace.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            _find_prolific_project(self.client, workspace_id, project_title)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{UTILS_PATH}._find_prolific_project")
    def test_find_or_create_prolific_project_success_find(self, mock__find_prolific_project, *args):
        workspace_id = "test"
        project_title = "test2"

        mock_project = Project()
        mock_project.title = project_title

        mock__find_prolific_project.return_value = (True, mock_project)

        result = find_or_create_prolific_project(self.client, workspace_id, project_title)

        self.assertEqual(mock_project, result)

    @patch(f"{API_PATH}.projects.Projects.create_for_workspace")
    @patch(f"{UTILS_PATH}._find_prolific_project")
    def test_find_or_create_prolific_project_success_create(
        self,
        mock__find_prolific_project,
        mock_create_for_workspace,
        *args,
    ):
        workspace_id = "test"
        project_title = "test2"

        mock_project = Project()
        mock_project.title = project_title

        mock__find_prolific_project.return_value = (False, None)
        mock_create_for_workspace.return_value = mock_project

        result = find_or_create_prolific_project(self.client, workspace_id, project_title)

        self.assertEqual(mock_project, result)

    @patch(f"{API_PATH}.projects.Projects.create_for_workspace")
    @patch(f"{UTILS_PATH}._find_prolific_project")
    def test_find_or_create_prolific_project_create_exception(
        self,
        mock__find_prolific_project,
        mock_create_for_workspace,
        *args,
    ):
        workspace_id = "test"
        project_title = "test2"

        mock__find_prolific_project.return_value = (False, None)

        exception_message = "Error"
        mock_create_for_workspace.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            find_or_create_prolific_project(self.client, workspace_id, project_title)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.remove")
    def test_delete_qualification_success(self, mock_remove, *args):
        prolific_participant_group_id = "test"

        mock_remove.return_value = {}

        result = delete_qualification(self.client, prolific_participant_group_id)

        self.assertTrue(result)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.remove")
    def test_delete_qualification_exception(self, mock_remove, *args):
        prolific_participant_group_id = "test"

        exception_message = "Error"
        mock_remove.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            delete_qualification(self.client, prolific_participant_group_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list")
    def test__find_qualification_success(self, mock_participant_groups_list, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = "test"
        qualification_description = "test"
        expected_qualification_id = uuid4().hex[:24]
        mock_participant_groups_list.return_value = [
            ParticipantGroup(
                project_id=prolific_project_id,
                id=expected_qualification_id,
                name=qualification_name,
                description=qualification_description,
            )
        ]
        _, q = _find_qualification(self.client, prolific_project_id, qualification_name)
        self.assertEqual(q.id, expected_qualification_id)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list")
    def test__find_qualification_no_qualification(self, mock_participant_groups_list, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = "test"
        mock_participant_groups_list.return_value = []
        result = _find_qualification(self.client, prolific_project_id, qualification_name)
        self.assertEqual(result, (False, None))

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list")
    def test__find_qualification_error(self, mock_participant_groups_list, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = "test"
        exception_message = "Error"
        mock_participant_groups_list.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            _find_qualification(self.client, prolific_project_id, qualification_name)
        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.create")
    def test_create_qualification_success(self, mock_create, *args):
        prolific_project_id = "test"
        qualification_name = "test2"
        participant_group_id = "test3"

        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = participant_group_id
        mock_participant_group.name = qualification_name

        mock_create.return_value = mock_participant_group

        result = create_qualification(self.client, prolific_project_id, qualification_name)

        self.assertEqual(mock_participant_group, result)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.create")
    def test_create_qualification_exception(self, mock_create, *args):
        prolific_project_id = "test"
        qualification_name = "test2"

        exception_message = "Error"
        mock_create.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            create_qualification(self.client, prolific_project_id, qualification_name)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{UTILS_PATH}._find_qualification")
    def test_find_or_create_qualification_found_one(self, mock_find_qualification, *args):
        prolific_project_id = uuid4().hex[:24]
        qualification_name = "test"
        expected_qualification_id = uuid4().hex[:24]
        expected_qualification = ParticipantGroup()
        expected_qualification.id = expected_qualification_id
        mock_find_qualification.return_value = (True, expected_qualification)
        result = find_or_create_qualification(
            self.client,
            prolific_project_id,
            qualification_name,
        )
        self.assertEqual(result.id, expected_qualification_id)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.create")
    @patch(f"{UTILS_PATH}._find_qualification")
    def test_find_or_create_qualification_created_new(
        self,
        mock_find_qualification,
        mock_participant_groups_create,
        *args,
    ):
        qualification_name = "test"
        qualification_description = "test"
        expected_qualification_id = uuid4().hex[:24]
        mock_find_qualification.return_value = (False, None)
        mock_participant_groups_create.return_value = ParticipantGroup(
            id=expected_qualification_id,
            name=qualification_name,
            description=qualification_description,
        )
        result = find_or_create_qualification(
            self.client,
            qualification_name,
            qualification_description,
        )
        self.assertEqual(result.id, expected_qualification_id)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.create")
    @patch(f"{UTILS_PATH}._find_qualification")
    def test_find_or_create_qualification_error(
        self,
        mock_find_qualification,
        mock_participant_groups_create,
        *args,
    ):
        qualification_name = "test"
        qualification_description = "test"
        mock_find_qualification.return_value = (False, None)
        exception_message = "Error"
        mock_participant_groups_create.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            find_or_create_qualification(
                self.client,
                qualification_name,
                qualification_description,
            )
        self.assertEqual(cm.exception.message, exception_message)

    @patch("mephisto.abstractions.architects.ec2.ec2_architect.get_full_domain")
    def test__ec2_external_url(self, mock_get_full_domain, *args):
        mock_get_full_domain.return_value = "http://test.com"

        result = _ec2_external_url(mock_task_run_args)

        self.assertEqual(
            "http://test.com?"
            "participant_id={{%PROLIFIC_PID%}}&"
            "study_id={{%STUDY_ID%}}&"
            "submission_id={{%SESSION_ID%}}",
            result,
        )

    def test__is_ec2_architect(self, *args):
        result_local_architect = _is_ec2_architect(mock_task_run_args)

        mock_task_run_args_ec2 = deepcopy(mock_task_run_args)
        mock_task_run_args_ec2.architect._architect_type = "ec2"
        result_ec2_architect = _is_ec2_architect(mock_task_run_args_ec2)

        self.assertFalse(result_local_architect)
        self.assertTrue(result_ec2_architect)

    @patch("mephisto.abstractions.architects.ec2.ec2_architect.get_full_domain")
    def test__get_external_study_url(self, mock_get_full_domain, *args):
        mock_get_full_domain.return_value = "http://test.com"

        result_local_architect = _get_external_study_url(mock_task_run_args)

        mock_task_run_args_ec2 = deepcopy(mock_task_run_args)
        mock_task_run_args_ec2.architect._architect_type = "ec2"
        result_ec2_architect = _get_external_study_url(mock_task_run_args_ec2)

        self.assertEqual(
            mock_task_run_args.provider.prolific_external_study_url,
            result_local_architect,
        )
        self.assertEqual(
            "http://test.com?"
            "participant_id={{%PROLIFIC_PID%}}&"
            "study_id={{%STUDY_ID%}}&"
            "submission_id={{%SESSION_ID%}}",
            result_ec2_architect,
        )

    @patch(f"{API_PATH}.studies.Studies.update")
    @patch(f"{API_PATH}.studies.Studies.create")
    def test_create_study_success(self, mock_study_create, mock_study_update, *args):
        project_id = uuid4().hex[:24]
        expected_study_id = uuid4().hex[:24]
        mock_study = Study(
            project=project_id,
            id=expected_study_id,
            name="test",
            completion_codes=[
                dict(
                    code="test",
                    code_type="test",
                    actions=[
                        dict(
                            action="test",
                        )
                    ],
                )
            ],
        )
        mock_study_create.return_value = mock_study
        mock_study_update.return_value = mock_study
        study = create_study(
            client=self.client,
            task_run_config=mock_task_run_args,
            prolific_project_id=project_id,
        )
        self.assertEqual(study.id, expected_study_id)

    @patch(f"{API_PATH}.studies.Studies.update")
    @patch(f"{API_PATH}.studies.Studies.create")
    def test_create_study_error(self, mock_study_create, *args):
        project_id = uuid4().hex[:24]
        exception_message = "Error"
        mock_study_create.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            create_study(
                client=self.client,
                task_run_config=mock_task_run_args,
                prolific_project_id=project_id,
            )
        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.studies.Studies.update")
    @patch(f"{UTILS_PATH}.get_study")
    def test_increase_total_available_places_for_study_success(self, mock_get_study, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id
        mock_study.total_available_places = 0

        mock_get_study.return_value = mock_study

        result = increase_total_available_places_for_study(self.client, study_id)

        self.assertEqual(mock_study, result)

    @patch(f"{API_PATH}.studies.Studies.update")
    @patch(f"{UTILS_PATH}.get_study")
    def test_increase_total_available_places_for_study_exception(
        self,
        mock_get_study,
        mock_update,
        *args,
    ):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id
        mock_study.total_available_places = 0

        mock_get_study.return_value = mock_study

        exception_message = "Error"
        mock_update.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            increase_total_available_places_for_study(self.client, study_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.studies.Studies.retrieve")
    def test_get_study_success(self, mock_retrieve, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        mock_retrieve.return_value = mock_study

        result = get_study(self.client, study_id)

        self.assertEqual(mock_study, result)

    @patch(f"{API_PATH}.studies.Studies.retrieve")
    def test_get_study_exception(self, mock_retrieve, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        exception_message = "Error"
        mock_retrieve.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            get_study(self.client, study_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.studies.Studies.publish")
    def test_publish_study_success(self, mock_publish, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        mock_publish.return_value = mock_study

        result = publish_study(self.client, study_id)

        self.assertEqual(study_id, result)

    @patch(f"{API_PATH}.studies.Studies.publish")
    def test_publish_study_exception(self, mock_publish, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        exception_message = "Error"
        mock_publish.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            publish_study(self.client, study_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.studies.Studies.stop")
    def test_stop_study_success(self, mock_stop, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        mock_stop.return_value = mock_study

        result = stop_study(self.client, study_id)

        self.assertEqual(mock_study, result)

    @patch(f"{API_PATH}.studies.Studies.stop")
    def test_stop_study_exception(self, mock_stop, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        exception_message = "Error"
        mock_stop.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            stop_study(self.client, study_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.studies.Studies.update")
    @patch(f"{API_PATH}.studies.Studies.stop")
    @patch(f"{UTILS_PATH}.get_study")
    def test_expire_study_success(self, mock_get_study, mock_stop, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id
        mock_study.internal_name = "test"

        mock_get_study.return_value = mock_study
        mock_stop.return_value = mock_study

        result = expire_study(self.client, study_id)

        self.assertEqual(mock_study, result)

    @patch(f"{UTILS_PATH}.get_study")
    def test_expire_study_exception(self, mock_get_study, *args):
        study_id = "test"

        mock_study = Study()
        mock_study.id = study_id

        exception_message = "Error"
        mock_get_study.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            expire_study(self.client, study_id)

        self.assertEqual(cm.exception.message, exception_message)

    def test_is_study_expired(self, *args):
        study_id = "test"
        study_name = "test"

        mock_study = Study()
        mock_study.id = study_id
        mock_study.status = constants.StudyStatus.COMPLETED
        mock_study.internal_name = study_name

        result_just_with_completed_status = is_study_expired(mock_study)

        mock_study.status = constants.StudyStatus.ACTIVE
        result_with_any_other_status = is_study_expired(mock_study)

        mock_study.status = constants.StudyStatus.AWAITING_REVIEW
        result_just_with_awaiting_review_status = is_study_expired(mock_study)

        mock_study.status = constants.StudyStatus.COMPLETED
        mock_study.internal_name = study_name + "_" + constants.StudyStatus._EXPIRED
        result_with_completed_status_and_internal_name = is_study_expired(mock_study)

        self.assertFalse(result_just_with_completed_status)
        self.assertFalse(result_with_any_other_status)
        self.assertFalse(result_just_with_awaiting_review_status)
        self.assertTrue(result_with_completed_status_and_internal_name)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.add_participants_to_group")
    def test_add_workers_to_qualification_success(self, *args):
        worker_ids = ["test", "test2"]
        participant_group_id = "test3"

        result = add_workers_to_qualification(self.client, worker_ids, participant_group_id)

        self.assertIsNone(result)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.add_participants_to_group")
    def test_add_workers_to_qualification_exception(self, mock_add_participants_to_group, *args):
        worker_ids = ["test", "test2"]
        participant_group_id = "test3"

        exception_message = "Error"
        mock_add_participants_to_group.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            add_workers_to_qualification(self.client, worker_ids, participant_group_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.add_participants_to_group")
    def test_give_worker_qualification_success(self, mock_add_participants_to_group, *args):
        worker_id = "test"
        participant_group_id = "test3"

        result = give_worker_qualification(self.client, worker_id, participant_group_id)

        mock_add_participants_to_group.assert_called_once_with(
            id=participant_group_id,
            participant_ids=[worker_id],
        )
        self.assertIsNone(result)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.remove_participants_from_group")
    def test_remove_worker_qualification_success(self, *args):
        worker_id = "test"
        participant_group_id = "test2"

        result = remove_worker_qualification(self.client, worker_id, participant_group_id)

        self.assertIsNone(result)

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.remove_participants_from_group")
    def test_remove_worker_qualification_exception(
        self,
        mock_remove_participants_from_group,
        *args,
    ):
        worker_id = "test"
        participant_group_id = "test2"

        exception_message = "Error"
        mock_remove_participants_from_group.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            remove_worker_qualification(self.client, worker_id, participant_group_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.bonuses.Bonuses.pay")
    @patch(f"{API_PATH}.bonuses.Bonuses.set_up")
    @patch(f"{UTILS_PATH}.check_balance")
    def test_pay_bonus_empty_balance(self, mock_check_balance, mock_set_up, mock_pay, *args):
        worker_id = "test"
        study_id = "test2"
        bonus_amount = 1000

        mock_check_balance.return_value = False

        result = pay_bonus(self.client, mock_task_run_args, worker_id, bonus_amount, study_id)

        mock_set_up.assert_not_called()
        mock_pay.assert_not_called()
        self.assertFalse(result)

    @patch(f"{API_PATH}.bonuses.Bonuses.pay")
    @patch(f"{API_PATH}.bonuses.Bonuses.set_up")
    @patch(f"{UTILS_PATH}.check_balance")
    def test_pay_bonus_empty_balance(self, mock_check_balance, mock_set_up, mock_pay, *args):
        worker_id = "test"
        study_id = "test2"
        bonus_amount = 1000

        mock_check_balance.return_value = False

        result = pay_bonus(self.client, mock_task_run_args, worker_id, bonus_amount, study_id)

        mock_set_up.assert_not_called()
        mock_pay.assert_not_called()
        self.assertFalse(result)

    @patch(f"{API_PATH}.bonuses.Bonuses.pay")
    @patch(f"{API_PATH}.bonuses.Bonuses.set_up")
    @patch(f"{UTILS_PATH}.check_balance")
    def test_pay_bonus_success(self, mock_check_balance, mock_set_up, mock_pay, *args):
        worker_id = "test"
        study_id = "test2"
        bonus_payments_id = "test3"
        bonus_amount = 1000

        mock_bonus_payments = BonusPayments()
        mock_bonus_payments.id = bonus_payments_id
        mock_check_balance.return_value = True
        mock_set_up.return_value = mock_bonus_payments

        result = pay_bonus(self.client, mock_task_run_args, worker_id, bonus_amount, study_id)

        mock_set_up.assert_called_once_with(study_id, f"{worker_id},{bonus_amount / 100}")
        mock_pay.assert_called_once_with(mock_bonus_payments.id)
        self.assertTrue(result)

    @patch(f"{API_PATH}.bonuses.Bonuses.pay")
    @patch(f"{API_PATH}.bonuses.Bonuses.set_up")
    @patch(f"{UTILS_PATH}.check_balance")
    def test_pay_bonus_set_up_exception(self, mock_check_balance, mock_set_up, mock_pay, *args):
        worker_id = "test"
        study_id = "test2"
        bonus_amount = 1000

        mock_check_balance.return_value = True

        exception_message = "Error"
        mock_set_up.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            pay_bonus(self.client, mock_task_run_args, worker_id, bonus_amount, study_id)

        self.assertEqual(cm.exception.message, exception_message)
        mock_set_up.assert_called_once_with(study_id, f"{worker_id},{bonus_amount / 100}")
        mock_pay.assert_not_called()

    @patch(f"{API_PATH}.bonuses.Bonuses.pay")
    @patch(f"{API_PATH}.bonuses.Bonuses.set_up")
    @patch(f"{UTILS_PATH}.check_balance")
    def test_pay_bonus_pay_exception(self, mock_check_balance, mock_set_up, mock_pay, *args):
        worker_id = "test"
        study_id = "test2"
        bonus_payments_id = "test3"
        bonus_amount = 1000

        mock_bonus_payments = BonusPayments()
        mock_bonus_payments.id = bonus_payments_id
        mock_check_balance.return_value = True
        mock_set_up.return_value = mock_bonus_payments

        exception_message = "Error"
        mock_pay.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            pay_bonus(self.client, mock_task_run_args, worker_id, bonus_amount, study_id)

        self.assertEqual(cm.exception.message, exception_message)
        mock_set_up.assert_called_once_with(study_id, f"{worker_id},{bonus_amount / 100}")
        mock_pay.assert_called_once_with(mock_bonus_payments.id)

    @patch(f"{UTILS_PATH}.find_or_create_qualification")
    @patch(f"{UTILS_PATH}.find_or_create_prolific_project")
    @patch(f"{UTILS_PATH}.find_or_create_prolific_workspace")
    def test__get_block_list_qualification(
        self,
        mock_find_or_create_prolific_workspace,
        mock_find_or_create_prolific_project,
        mock_find_or_create_qualification,
        *args,
    ):
        mock_workspace = Workspace()
        mock_workspace.id = "test"
        mock_project = Project()
        mock_project.id = "test2"
        mock_project.title = "test2_title"
        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = "test3"
        mock_participant_group.name = "test3_name"

        mock_find_or_create_prolific_workspace.return_value = mock_workspace
        mock_find_or_create_prolific_project.return_value = mock_project
        mock_find_or_create_qualification.return_value = mock_participant_group

        result = _get_block_list_qualification(self.client, mock_task_run_args)

        self.assertEqual(mock_participant_group, result)

    @patch(f"{UTILS_PATH}.add_workers_to_qualification")
    @patch(f"{UTILS_PATH}._get_block_list_qualification")
    def test_block_worker_success(
        self,
        mock__get_block_list_qualification,
        mock_add_workers_to_qualification,
        *args,
    ):
        worker_id = "test"

        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = "test2"

        mock__get_block_list_qualification.return_value = mock_participant_group

        result = block_worker(self.client, mock_task_run_args, worker_id)

        self.assertIsNone(result)
        mock_add_workers_to_qualification.called_once_with(
            self.client,
            workers_ids=[worker_id],
            qualification_id=mock_participant_group.id,
        )

    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.remove_participants_from_group")
    @patch(f"{UTILS_PATH}._get_block_list_qualification")
    def test_unblock_worker_success(
        self,
        mock__get_block_list_qualification,
        mock_remove_participants_from_group,
        *args,
    ):
        worker_id = "test"

        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = "test2"

        mock__get_block_list_qualification.return_value = mock_participant_group

        result = unblock_worker(self.client, mock_task_run_args, worker_id)

        self.assertIsNone(result)
        mock_remove_participants_from_group.called_once_with(
            id=mock_participant_group.id,
            participant_ids=[worker_id],
        )

    @patch(f"{UTILS_PATH}.find_or_create_prolific_project")
    @patch(f"{UTILS_PATH}.find_or_create_prolific_workspace")
    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list_participants_for_group")
    @patch(f"{UTILS_PATH}._find_qualification")
    def test_is_worker_blocked_no_block_list_qualification(
        self,
        mock__find_qualification,
        mock_list_participants_for_group,
        *args,
    ):
        worker_id = "test"

        mock__find_qualification.return_value = (False, None)

        result = is_worker_blocked(self.client, mock_task_run_args, worker_id)

        self.assertFalse(result)
        mock_list_participants_for_group.assert_not_called()

    @patch(f"{UTILS_PATH}.find_or_create_prolific_project")
    @patch(f"{UTILS_PATH}.find_or_create_prolific_workspace")
    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list_participants_for_group")
    @patch(f"{UTILS_PATH}._find_qualification")
    def test_is_worker_blocked_success_true(
        self,
        mock__find_qualification,
        mock_list_participants_for_group,
        *args,
    ):
        worker_id = "test"

        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = "test2"
        mock_participant = Participant()
        mock_participant.participant_id = worker_id

        mock__find_qualification.return_value = (True, mock_participant_group)
        mock_list_participants_for_group.return_value = [mock_participant]

        result = is_worker_blocked(self.client, mock_task_run_args, worker_id)

        self.assertTrue(result)
        mock_list_participants_for_group.assert_called_once()

    @patch(f"{UTILS_PATH}.find_or_create_prolific_project")
    @patch(f"{UTILS_PATH}.find_or_create_prolific_workspace")
    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list_participants_for_group")
    @patch(f"{UTILS_PATH}._find_qualification")
    def test_is_worker_blocked_success_false(
        self,
        mock__find_qualification,
        mock_list_participants_for_group,
        *args,
    ):
        worker_id = "test"

        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = "test2"
        mock_participant = Participant()
        mock_participant.participant_id = "test3"

        mock__find_qualification.return_value = (True, mock_participant_group)
        mock_list_participants_for_group.return_value = [mock_participant]

        result = is_worker_blocked(self.client, mock_task_run_args, worker_id)

        self.assertFalse(result)
        mock_list_participants_for_group.assert_called_once()

    @patch(f"{UTILS_PATH}.find_or_create_prolific_project")
    @patch(f"{UTILS_PATH}.find_or_create_prolific_workspace")
    @patch(f"{API_PATH}.participant_groups.ParticipantGroups.list_participants_for_group")
    @patch(f"{UTILS_PATH}._find_qualification")
    def test_is_worker_blocked_exception(
        self,
        mock__find_qualification,
        mock_list_participants_for_group,
        *args,
    ):
        worker_id = "test"

        mock_participant_group = ParticipantGroup()
        mock_participant_group.id = "test2"
        mock_participant = Participant()
        mock_participant.participant_id = worker_id

        mock__find_qualification.return_value = (True, mock_participant_group)

        exception_message = "Error"
        mock_list_participants_for_group.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            is_worker_blocked(self.client, mock_task_run_args, worker_id)

        self.assertEqual(cm.exception.message, exception_message)
        mock_list_participants_for_group.assert_called_once()

    @patch(f"{API_PATH}.studies.Studies.calculate_cost")
    def test_calculate_pay_amount_success(self, mock_calculate_cost, *args):
        task_amount = 1000
        total_available_places = 2

        mock_calculate_cost.return_value = task_amount * total_available_places

        result = calculate_pay_amount(self.client, task_amount, total_available_places)

        self.assertEqual(task_amount * total_available_places, result)

    @patch(f"{API_PATH}.studies.Studies.calculate_cost")
    def test_calculate_pay_amount_exception(self, mock_calculate_cost, *args):
        task_amount = 1000
        total_available_places = 2

        exception_message = "Error"
        mock_calculate_cost.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            calculate_pay_amount(self.client, task_amount, total_available_places)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.submissions.Submissions.list")
    def test__find_submission_success_found(self, mock_list, *args):
        worker_id = "test"
        study_id = "test2"

        mock_list_submission = ListSubmission()
        mock_list_submission.id = "test3"
        mock_list_submission.participant_id = worker_id

        mock_list.return_value = [mock_list_submission]

        result = _find_submission(self.client, study_id, worker_id)

        self.assertEqual(mock_list_submission, result)

    @patch(f"{API_PATH}.submissions.Submissions.list")
    def test__find_submission_success_not_found(self, mock_list, *args):
        worker_id = "test"
        study_id = "test2"

        mock_list_submission = ListSubmission()
        mock_list_submission.id = "test3"
        mock_list_submission.participant_id = "test4"

        mock_list.return_value = [mock_list_submission]

        result = _find_submission(self.client, study_id, worker_id)

        self.assertEqual(None, result)

    @patch(f"{API_PATH}.submissions.Submissions.list")
    def test__find_submission_exception(self, mock_list, *args):
        worker_id = "test"
        study_id = "test2"

        exception_message = "Error"
        mock_list.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            _find_submission(self.client, study_id, worker_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.submissions.Submissions.retrieve")
    def test_get_submission_success(self, mock_retrieve, *args):
        submission_id = "test"

        mock_submission = Submission()
        mock_submission.id = "test2"

        mock_retrieve.return_value = mock_submission

        result = get_submission(self.client, submission_id)

        self.assertEqual(mock_submission, result)

    @patch(f"{API_PATH}.submissions.Submissions.retrieve")
    def test_get_submission_exception(self, mock_retrieve, *args):
        submission_id = "test"

        exception_message = "Error"
        mock_retrieve.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            get_submission(self.client, submission_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.submissions.Submissions.approve")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_approve_work_submission_not_found(self, mock__find_submission, mock_approve, *args):
        worker_id = "test"
        study_id = "test2"

        mock__find_submission.return_value = False

        result = approve_work(self.client, study_id, worker_id)

        self.assertIsNone(result)
        mock_approve.assert_not_called()

    @patch(f"{API_PATH}.submissions.Submissions.approve")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_approve_work_success(self, mock__find_submission, mock_approve, *args):
        worker_id = "test"
        study_id = "test2"

        mock_submission = Submission()
        mock_submission.id = "test3"
        mock_submission.status = constants.SubmissionStatus.AWAITING_REVIEW

        mock_submission_approved = Submission()
        mock_submission_approved.id = "test4"
        mock_submission_approved.status = constants.SubmissionStatus.APPROVED

        mock__find_submission.return_value = mock_submission
        mock_approve.return_value = mock_submission_approved

        result = approve_work(self.client, study_id, worker_id)

        self.assertEqual(mock_submission_approved, result)
        mock_approve.assert_called_once()

    @patch(f"{API_PATH}.submissions.Submissions.approve")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_approve_work_incorrect_submission_status(
        self,
        mock__find_submission,
        mock_approve,
        *args,
    ):
        worker_id = "test"
        study_id = "test2"

        mock_submission = Submission()
        mock_submission.id = "test3"
        mock_submission.status = constants.SubmissionStatus.ACTIVE

        mock__find_submission.return_value = mock_submission

        result = approve_work(self.client, study_id, worker_id)

        self.assertIsNone(result)
        mock_approve.assert_not_called()

    @patch(f"{API_PATH}.submissions.Submissions.approve")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_approve_work_exception(self, mock__find_submission, mock_approve, *args):
        worker_id = "test"
        study_id = "test2"

        mock_submission = Submission()
        mock_submission.id = "test3"
        mock_submission.status = constants.SubmissionStatus.AWAITING_REVIEW

        mock__find_submission.return_value = mock_submission

        exception_message = "Error"
        mock_approve.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            approve_work(self.client, study_id, worker_id)

        self.assertEqual(cm.exception.message, exception_message)

    @patch(f"{API_PATH}.submissions.Submissions.reject")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_reject_work_submission_not_found(self, mock__find_submission, mock_reject, *args):
        worker_id = "test"
        study_id = "test2"

        mock__find_submission.return_value = False

        result = reject_work(self.client, study_id, worker_id)

        self.assertIsNone(result)
        mock_reject.assert_not_called()

    @patch(f"{API_PATH}.submissions.Submissions.reject")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_reject_work_success(self, mock__find_submission, mock_reject, *args):
        worker_id = "test"
        study_id = "test2"

        mock_submission = Submission()
        mock_submission.id = "test3"
        mock_submission.status = constants.SubmissionStatus.AWAITING_REVIEW

        mock_submission_rejected = Submission()
        mock_submission_rejected.id = "test4"
        mock_submission_rejected.status = constants.SubmissionStatus.REJECTED

        mock__find_submission.return_value = mock_submission
        mock_reject.return_value = mock_submission_rejected

        result = reject_work(self.client, study_id, worker_id)

        self.assertEqual(mock_submission_rejected, result)
        mock_reject.assert_called_once()

    @patch(f"{API_PATH}.submissions.Submissions.reject")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_reject_work_incorrect_submission_status(
        self,
        mock__find_submission,
        mock_reject,
        *args,
    ):
        worker_id = "test"
        study_id = "test2"

        mock_submission = Submission()
        mock_submission.id = "test3"
        mock_submission.status = constants.SubmissionStatus.ACTIVE

        mock__find_submission.return_value = mock_submission

        result = reject_work(self.client, study_id, worker_id)

        self.assertIsNone(result)
        mock_reject.assert_not_called()

    @patch(f"{API_PATH}.submissions.Submissions.reject")
    @patch(f"{UTILS_PATH}._find_submission")
    def test_reject_work_exception(self, mock__find_submission, mock_reject, *args):
        worker_id = "test"
        study_id = "test2"

        mock_submission = Submission()
        mock_submission.id = "test3"
        mock_submission.status = constants.SubmissionStatus.AWAITING_REVIEW

        mock__find_submission.return_value = mock_submission

        exception_message = "Error"
        mock_reject.side_effect = ProlificRequestError(exception_message)
        with self.assertRaises(ProlificRequestError) as cm:
            reject_work(self.client, study_id, worker_id)

        self.assertEqual(cm.exception.message, exception_message)


if __name__ == "__main__":
    unittest.main()
