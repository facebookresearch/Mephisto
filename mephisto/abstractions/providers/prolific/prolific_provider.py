#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import cast
from typing import ClassVar
from typing import Type
from typing import TYPE_CHECKING

from mephisto.abstractions.crowd_provider import CrowdProvider
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.api.constants import ProlificIDOption
from mephisto.abstractions.providers.prolific.prolific_agent import ProlificAgent
from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
from mephisto.abstractions.providers.prolific.prolific_unit import ProlificUnit
from mephisto.abstractions.providers.prolific.prolific_worker import ProlificWorker
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.operations.registry import register_mephisto_abstraction
from mephisto.utils.logger_core import get_logger
from . import api as prolific_api
from .api.data_models import Project
from .api.data_models import Workspace
from .api.exceptions import ProlificException

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.blueprint import SharedTaskState
    from omegaconf import DictConfig


DEFAULT_FRAME_HEIGHT = 0
DEFAULT_PROLIFIC_GROUP_NAME_ALLOW_LIST = 'Allow list'
DEFAULT_PROLIFIC_GROUP_NAME_BLOCK_LIST = 'Block list'
DEFAULT_PROLIFIC_PROJECT_NAME = 'Project'
DEFAULT_PROLIFIC_WORKSPACE_NAME = 'My Workspace'


logger = get_logger(name=__name__)


@dataclass
class ProlificProviderArgs(ProviderArgs):
    """Base class for arguments to configure Crowd Providers"""
    _provider_type: str = PROVIDER_TYPE
    requester_name: str = PROVIDER_TYPE
    # This link is being collected automatically for EC2 archidect.
    prolific_external_study_url: str = field(
        default='',
        metadata={
            'help': (
                'The external study URL of your study that you want participants to be direct to. '
                'The URL can be customized to add information to match participants '
                'in your survey. '
                'You can add query parameters with the following placeholders. '
                'Example of a link with params: '
                'https://example.com?'
                'participant_id={{%PROLIFIC_PID%}}'
                '&study_id={{%STUDY_ID%}}'
                '&submission_id={{%SESSION_ID%}}'
                'where `prolific_pid`, `study_id`, `submission_id` are params we use on our side, '
                'and `{{%PROLIFIC_PID%}}`, `{{%STUDY_ID%}}`, `{{%SESSION_ID%}}` are their '
                'format of template variables they use to replace with their IDs'
            ),
        },
    )
    prolific_id_option: str = field(
        default=ProlificIDOption.URL_PARAMETERS,
        metadata={
            'help': (
                'Enum: "question" "url_parameters" "not_required". '
                'Use \'question\' if you will add a question in your survey or '
                'experiment asking the participant ID. '
                'Recommended Use \'url_parameters\' if your survey or experiment can retrieve and '
                'store those parameters for your analysis.'
                'Use \'not_required\' if you don\'t need to record them'
            ),
        },
    )
    prolific_estimated_completion_time_in_minutes: int = field(
        default=5,
        metadata={
            'help': (
                'Estimated duration in minutes of the experiment or survey '
                '(`estimated_completion_time` in Prolific).'
            ),
        },
    )
    prolific_total_available_places: int = field(
        default=1,
        metadata={
            'help': 'How many participants are you looking to recruit.',
        },
    )
    prolific_eligibility_requirements: list = field(
        default=(),
        metadata={
            'help': (
                'Eligibility requirements allows you to define '
                'participants criteria such as age, gender and country. '
            ),
        },
    )
    prolific_workspace_name: str = field(
        default=DEFAULT_PROLIFIC_WORKSPACE_NAME,
    )
    prolific_project_name: str = field(
        default=DEFAULT_PROLIFIC_PROJECT_NAME,
    )
    prolific_allow_list_group_name: str = field(
        default=DEFAULT_PROLIFIC_GROUP_NAME_ALLOW_LIST,
    )
    prolific_block_list_group_name: str = field(
        default=DEFAULT_PROLIFIC_GROUP_NAME_BLOCK_LIST,
    )


@register_mephisto_abstraction()
class ProlificProvider(CrowdProvider):
    """
    Prolific implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """
    UnitClass: ClassVar[Type["Unit"]] = ProlificUnit

    RequesterClass: ClassVar[Type["Requester"]] = ProlificRequester

    WorkerClass: ClassVar[Type["Worker"]] = ProlificWorker

    AgentClass: ClassVar[Type["Agent"]] = ProlificAgent

    ArgsClass = ProlificProviderArgs

    PROVIDER_TYPE = PROVIDER_TYPE

    curr_db_location: ClassVar[str]

    def initialize_provider_datastore(self, storage_path: str) -> Any:
        return ProlificDatastore(datastore_root=storage_path)

    def _get_client(self, requester_name: str) -> prolific_api:
        """Get a Prolific client"""
        return self.datastore.get_client_for_requester(requester_name)

    def setup_resources_for_task_run(
        self,
        task_run: 'TaskRun',
        args: 'DictConfig',
        shared_state: 'SharedTaskState',
        server_url: str,
    ) -> None:
        requester = cast('ProlificRequester', task_run.get_requester())
        client = self._get_client(requester.requester_name)
        task_run_id = task_run.db_id

        # Set up Task Run config
        config_dir = os.path.join(self.datastore.datastore_root, task_run_id)

        frame_height = task_run.get_blueprint().get_frontend_args().get(
            'frame_height', DEFAULT_FRAME_HEIGHT,
        )

        # Get Prolific specific data to create a task
        prolific_workspace: Workspace = prolific_utils.find_or_create_prolific_workspace(
            client, title=args.provider.prolific_workspace_name,
        )
        prolific_project: Project = prolific_utils.find_or_create_prolific_project(
            client, prolific_workspace.id, title=args.provider.prolific_project_name,
        )

        # Register TaskRun in Datastore
        self.datastore.register_run(
            run_id=task_run_id,
            prolific_workspace_id=prolific_workspace.id,
            prolific_project_id=prolific_project.id,
            prolific_study_config_path=config_dir,
            frame_height=frame_height,
            prolific_study_id=None,
        )

    def cleanup_resources_from_task_run(self, task_run: 'TaskRun', server_url: str) -> None:
        """No cleanup necessary for task type"""
        pass

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), 'wrap_crowd_source.js')

    def cleanup_qualification(self, qualification_name: str) -> None:
        """Remove the qualification from Prolific (Participant Group), if it exists"""
        mapping = self.datastore.get_qualification_mapping(qualification_name)
        if mapping is None:
            return None

        requester_id = mapping['requester_id']
        requester = Requester.get(self.db, requester_id)
        assert isinstance(requester, ProlificRequester), 'Must be an Prolific requester'
        client = requester._get_client(requester.requester_name)
        try:
            prolific_utils.delete_qualification(client, mapping['prolific_participant_group_id'])
        except ProlificException:
            logger.exception('Could not delete qualification on Prolific')

