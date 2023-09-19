#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import cast
from typing import ClassVar
from typing import List
from typing import Type
from typing import TYPE_CHECKING

from omegaconf import DictConfig

from mephisto.abstractions.crowd_provider import CrowdProvider
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.api.constants import ProlificIDOption
from mephisto.abstractions.providers.prolific.api.constants import StudyStatus
from mephisto.abstractions.providers.prolific.prolific_agent import ProlificAgent
from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
from mephisto.abstractions.providers.prolific.prolific_unit import ProlificUnit
from mephisto.abstractions.providers.prolific.prolific_worker import ProlificWorker
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.operations.registry import register_mephisto_abstraction
from mephisto.utils.logger_core import get_logger
from mephisto.utils.qualifications import QualificationType
from mephisto.utils.qualifications import worker_is_qualified
from .api.client import ProlificClient
from .api.data_models import ParticipantGroup
from .api.data_models import Project
from .api.data_models import Study
from .api.data_models import Workspace
from .api.eligibility_requirement_classes import CustomBlacklistEligibilityRequirement
from .api.eligibility_requirement_classes import CustomWhitelistEligibilityRequirement
from .api.eligibility_requirement_classes import ParticipantGroupEligibilityRequirement
from .api.exceptions import ProlificException

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.blueprint import SharedTaskState


DEFAULT_FRAME_HEIGHT = 0
DEFAULT_PROLIFIC_GROUP_NAME_ALLOW_LIST = "Allow list"
DEFAULT_PROLIFIC_GROUP_NAME_BLOCK_LIST = "Block list"
DEFAULT_PROLIFIC_PROJECT_NAME = "Project"
DEFAULT_PROLIFIC_WORKSPACE_NAME = "My Workspace"

logger = get_logger(name=__name__)


@dataclass
class ProlificProviderArgs(ProviderArgs):
    """Base class for arguments to configure Crowd Providers"""

    # `_provider_type` cannot be `OmegaConf.MISSING`,
    # because `dataclasses` does not allow defining non-default properties before optional
    # in Python 3.9
    _provider_type: str = PROVIDER_TYPE

    # This link is being collected automatically for EC2 archidect.
    # But we leave the ability to pass any other URL for other architects,
    # especially, for those that weren't specified in
    # `mephisto.abstractions.providers.prolific.prolific_utils._get_external_study_url`
    prolific_external_study_url: str = field(
        default="",
        metadata={
            "help": (
                "The external study URL of your study that you want participants to be direct to. "
                "The URL can be customized to add information to match participants "
                "in your survey. "
                "You can add query parameters with the following placeholders. "
                "Example of a link with params: "
                "https://example.com?"
                "participant_id={{%PROLIFIC_PID%}}"
                "&study_id={{%STUDY_ID%}}"
                "&submission_id={{%SESSION_ID%}}"
                "where `prolific_pid`, `study_id`, `submission_id` are params we use on our side, "
                "and `{{%PROLIFIC_PID%}}`, `{{%STUDY_ID%}}`, `{{%SESSION_ID%}}` are their "
                "format of template variables they use to replace with their IDs"
            ),
        },
    )
    prolific_id_option: str = field(
        default=ProlificIDOption.URL_PARAMETERS,
        metadata={
            "help": (
                'Enum: "question" "url_parameters" "not_required". '
                "Use 'question' if you will add a question in your survey or "
                "experiment asking the participant ID. "
                "Recommended Use 'url_parameters' if your survey or experiment can retrieve and "
                "store those parameters for your analysis."
                "Use 'not_required' if you don't need to record them"
            ),
        },
    )
    prolific_estimated_completion_time_in_minutes: int = field(
        default=5,
        metadata={
            "help": (
                "Estimated duration in minutes of the experiment or survey "
                "(`estimated_completion_time` in Prolific)."
            ),
        },
    )
    prolific_eligibility_requirements: list = field(
        default=(),
        metadata={
            "help": (
                "Eligibility requirements allows you to define "
                "participants criteria such as age, gender and country. "
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

    @property
    def log_prefix(self) -> str:
        return "[Prolific Provider] "

    def _get_client(self, requester_name: str) -> ProlificClient:
        """Get a Prolific client"""
        return self.datastore.get_client_for_requester(requester_name)

    def _get_qualified_workers(
        self,
        qualifications: List[QualificationType],
        bloked_participant_ids: List[str],
    ) -> List["Worker"]:
        qualified_workers = []
        workers: List[Worker] = self.db.find_workers(provider_type="prolific")
        # `worker_name` is Prolific Participant ID in provider-specific datastore
        available_workers = [w for w in workers if w.worker_name not in bloked_participant_ids]

        for worker in available_workers:
            if worker_is_qualified(worker, qualifications):
                qualified_workers.append(worker)

        return qualified_workers

    def _create_participant_group_with_qualified_workers(
        self,
        client: ProlificClient,
        requester: ProlificRequester,
        workers_ids: List[str],
        prolific_project_id: str,
    ) -> ParticipantGroup:
        participant_proup_name = f"PG {datetime.now(timezone.utc).isoformat()}"
        prolific_participant_group = prolific_utils.create_qualification(
            client,
            prolific_project_id,
            participant_proup_name,
        )
        prolific_utils.add_workers_to_qualification(
            client,
            workers_ids,
            prolific_participant_group.id,
        )
        self.datastore.create_participant_group_mapping(
            qualification_name=participant_proup_name,
            requester_id=requester.db_id,
            prolific_project_id=prolific_project_id,
            prolific_participant_group_name=participant_proup_name,
            prolific_participant_group_id=prolific_participant_group.id,
        )
        return prolific_participant_group

    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        requester = cast("ProlificRequester", task_run.get_requester())
        client = self._get_client(requester.requester_name)
        task_run_id = task_run.db_id

        # Set up Task Run config
        config_dir = os.path.join(self.datastore.datastore_root, task_run_id)

        frame_height = (
            task_run.get_blueprint().get_frontend_args().get("frame_height", DEFAULT_FRAME_HEIGHT)
        )

        # Mephisto qualifications
        qualifications = shared_state.qualifications

        # Get provider-specific qualification from SharedState
        prolific_specific_qualifications = getattr(
            shared_state,
            "prolific_specific_qualifications",
            [],
        )
        # Update with ones from YAML config under `provider` title
        yaml_prolific_specific_qualifications = args.provider.prolific_eligibility_requirements
        if yaml_prolific_specific_qualifications:
            prolific_specific_qualifications += yaml_prolific_specific_qualifications

        if not qualifications and not prolific_specific_qualifications:
            raise AssertionError(
                '"qualifications" or "prolific_specific_qualifications" must be provided'
            )

        # Get Prolific specific data to create a task
        prolific_workspace: Workspace = prolific_utils.find_or_create_prolific_workspace(
            client,
            title=args.provider.prolific_workspace_name,
        )
        prolific_project: Project = prolific_utils.find_or_create_prolific_project(
            client,
            prolific_workspace.id,
            title=args.provider.prolific_project_name,
        )

        blocked_participant_ids = self.datastore.get_bloked_participant_ids()

        # If no Mephisto qualifications found,
        # we need to block Mephisto workers on Prolific as well
        if blocked_participant_ids:
            new_prolific_specific_qualifications = []
            # Add empty Blacklist in case if there is not in state or config
            blacklist_qualification = DictConfig(
                dict(
                    name=CustomBlacklistEligibilityRequirement.name,
                    black_list=[],
                )
            )

            for prolific_specific_qualification in prolific_specific_qualifications:
                name = prolific_specific_qualification["name"]

                if name == CustomBlacklistEligibilityRequirement.name:
                    blacklist_qualification = prolific_specific_qualification
                elif name == CustomWhitelistEligibilityRequirement.name:
                    # Remove blocked Participat IDs from Whitelist Eligibility Requirement
                    whitelist_qualification = prolific_specific_qualification
                    prev_value = whitelist_qualification["white_list"]
                    whitelist_qualification["white_list"] = [
                        p for p in prev_value if p not in blocked_participant_ids
                    ]
                    new_prolific_specific_qualifications.append(whitelist_qualification)
                elif name == ParticipantGroupEligibilityRequirement.name:
                    # Remove blocked Participat IDs from Participant Group Eligibility Requirement
                    client.ParticipantGroups.remove_participants_from_group(
                        id=prolific_specific_qualification["id"],
                        participant_ids=blocked_participant_ids,
                    )
                else:
                    new_prolific_specific_qualifications.append(prolific_specific_qualification)

            # Set Blacklist Eligibility Requirement
            blacklist_qualification["black_list"] = list(
                set(blacklist_qualification["black_list"] + blocked_participant_ids)
            )
            new_prolific_specific_qualifications.append(blacklist_qualification)
            prolific_specific_qualifications = new_prolific_specific_qualifications

        if qualifications:
            qualified_workers = self._get_qualified_workers(qualifications, blocked_participant_ids)

            if qualified_workers:
                prolific_workers_ids = [w.worker_name for w in qualified_workers]
                # Create a new Participant Group
                prolific_participant_group = self._create_participant_group_with_qualified_workers(
                    client,
                    requester,
                    prolific_workers_ids,
                    prolific_project.id,
                )
                # Add this Participant Group to Prolific-specific requirements
                prolific_specific_qualifications.append(
                    {
                        "name": ParticipantGroupEligibilityRequirement.name,
                        "id": prolific_participant_group.id,
                    }
                )

                qualification_names = [q["qualification_name"] for q in qualifications]
                qualification_objs = self.db.find_qualifications()
                qualifications_ids = [
                    q.db_id
                    for q in qualification_objs
                    if q.qualification_name in qualification_names
                ]
                self.datastore.create_qualification_mapping(
                    run_id=task_run_id,
                    prolific_participant_group_id=prolific_participant_group.id,
                    qualifications=qualifications,
                    qualification_ids=qualifications_ids,
                )

        # Create Study
        logger.debug(f"{self.log_prefix}Creating Prolific Study")
        prolific_study: Study = prolific_utils.create_study(
            client,
            task_run_config=args,
            prolific_project_id=prolific_project.id,
            eligibility_requirements=prolific_specific_qualifications,
        )
        logger.debug(
            f"{self.log_prefix}"
            f"Prolific Study has been created successfully with ID: {prolific_study.id}"
        )

        # Publish Prolific Study
        logger.debug(f"{self.log_prefix}Publishing Prolific Study")
        prolific_utils.publish_study(client, prolific_study.id)
        logger.debug(
            f"{self.log_prefix}"
            f'Prolific Study "{prolific_study.id}" has been published successfully with ID'
        )

        # Register TaskRun in Datastore
        self.datastore.register_run(
            run_id=task_run_id,
            prolific_workspace_id=prolific_workspace.id,
            prolific_project_id=prolific_project.id,
            prolific_study_config_path=config_dir,
            frame_height=frame_height,
            prolific_study_id=prolific_study.id,
        )

        # Save Study into provider-specific datastore
        self.datastore.new_study(
            prolific_study_id=prolific_study.id,
            study_link=prolific_study.external_study_url,
            duration_in_seconds=(args.provider.prolific_estimated_completion_time_in_minutes * 60),
            task_run_id=task_run_id,
            status=StudyStatus.ACTIVE,
        )
        logger.debug(
            f'{self.log_prefix}Prolific Study "{prolific_study.id}" has been saved into datastore'
        )

    def cleanup_resources_from_task_run(self, task_run: "TaskRun", server_url: str) -> None:
        """
        Cleanup all temporary data for this TaskRun
            1. Remove one-time Participant Groups from datastore and Prolific
        """
        requester = cast("ProlificRequester", task_run.get_requester())
        client = self._get_client(requester.requester_name)

        # 1. Remove one-time Participant Groups
        datastore_qualifications = self.datastore.find_qualifications_by_ids(
            task_run_ids=[task_run.db_id],
        )

        # Remove from Provider-specific datastore
        participant_group_ids = [
            i["prolific_participant_group_id"] for i in datastore_qualifications
        ]
        self.datastore.delete_qualifications_by_participant_group_ids(
            participant_group_ids=participant_group_ids,
        )
        self.datastore.delete_participant_groups_by_participant_group_ids(
            participant_group_ids=participant_group_ids,
        )

        # Remove from Prolific
        for qualification in datastore_qualifications:
            prolific_utils.delete_qualification(
                client,
                qualification["prolific_participant_group_id"],
            )

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")

    def cleanup_qualification(self, qualification_name: str) -> None:
        """Remove the qualification from Prolific (Participant Group), if it exists"""
        mapping = self.datastore.get_qualification_mapping(qualification_name)
        if mapping is None:
            return None

        requester_id = mapping["requester_id"]
        requester = Requester.get(self.db, requester_id)
        assert isinstance(requester, ProlificRequester), "Must be an Prolific requester"
        client = requester._get_client(requester.requester_name)
        try:
            prolific_utils.delete_qualification(
                client,
                mapping["prolific_participant_group_id"],
            )
        except ProlificException:
            logger.exception("Could not delete qualification on Prolific")
