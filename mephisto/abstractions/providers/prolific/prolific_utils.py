#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import inspect
import json
import os
import sys
import uuid
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from jsonschema.exceptions import ValidationError
from omegaconf import DictConfig

from mephisto.abstractions.architects.ec2 import ec2_architect
from mephisto.utils.logger_core import get_logger
from . import api as prolific_api
from .api import constants
from .api import eligibility_requirement_classes
from .api.base_api_resource import CREDENTIALS_CONFIG_DIR
from .api.base_api_resource import CREDENTIALS_CONFIG_PATH
from .api.client import ProlificClient
from .api.data_models import BonusPayments
from .api.data_models import ListSubmission
from .api.data_models import Participant
from .api.data_models import ParticipantGroup
from .api.data_models import Project
from .api.data_models import Study
from .api.data_models import Submission
from .api.data_models import Workspace
from .api.data_models import WorkspaceBalance
from .api.exceptions import ProlificException
from .prolific_requester import ProlificRequesterArgs

DEFAULT_CLIENT = cast(ProlificClient, prolific_api)

logger = get_logger(name=__name__)


# --- Credentials ---
def check_credentials(client: ProlificClient = DEFAULT_CLIENT) -> bool:
    """Check whether API KEY is correct"""
    try:
        # Make a simple request to the API
        client.Users.me()
        return True
    except (ProlificException, ValidationError):
        return False


def get_authenticated_client(profile_name: str) -> ProlificClient:
    """Get a client for the given profile"""
    cred_path = os.path.expanduser(CREDENTIALS_CONFIG_PATH)
    assert os.path.exists(cred_path), f"No credentials file at {cred_path}"
    with open(cred_path) as cred_file:
        curr_creds = json.load(cred_file)
        assert profile_name in curr_creds, f"No stored credentials for {profile_name}"
        key = curr_creds[profile_name]

    return ProlificClient(api_key=key)


def setup_credentials(
    profile_name: str,
    register_args: Optional[ProlificRequesterArgs],
) -> bool:
    if register_args is None:
        api_key = input(f"Provide api key for {profile_name}: ")
    else:
        api_key = register_args.api_key

    if not os.path.exists(os.path.expanduser(CREDENTIALS_CONFIG_DIR)):
        os.mkdir(os.path.expanduser(CREDENTIALS_CONFIG_DIR))

    cred_path = os.path.expanduser(CREDENTIALS_CONFIG_PATH)

    if os.path.exists(cred_path):
        with open(cred_path) as cred_file:
            curr_creds = json.load(cred_file)
    else:
        curr_creds = {}

    curr_creds[profile_name] = api_key

    with open(os.path.expanduser(CREDENTIALS_CONFIG_PATH), "w") as cred_file:
        json.dump(curr_creds, cred_file)

    return True


def check_balance(client: ProlificClient, **kwargs) -> Union[float, int, None]:
    """Checks to see if there is at least available_balance amount in the workspace"""
    workspace_name = kwargs.get("workspace_name")
    if not workspace_name:
        return None

    found_workspace, workspace = _find_prolific_workspace(client, title=workspace_name)

    if not found_workspace:
        logger.error(f"Could not find a workspace with name {workspace_name}")
        return None

    try:
        workspace_balance: WorkspaceBalance = client.Workspaces.get_balance(id=workspace.id)
    except (ProlificException, ValidationError):
        logger.exception(f"Could not receive a workspace balance with {workspace.id=}")
        raise

    return workspace_balance.available_balance


# --- Workspaces ---
def _find_prolific_workspace(
    client: ProlificClient,
    title: str,
    id: Optional[str] = None,
) -> Tuple[bool, Optional[Workspace]]:
    """Find a Prolific Workspace by title or ID"""
    if id:
        try:
            workspace: Workspace = client.Workspaces.retrieve(id)
            return True, workspace
        except (ProlificException, ValidationError):
            logger.exception(f"Could not find a workspace by id {id}")
            raise

    try:
        workspaces: List[Workspace] = client.Workspaces.list()
    except (ProlificException, ValidationError):
        logger.exception(f"Could not find a workspace by title {title}")
        raise

    for workspace in workspaces:
        if workspace.title == title:
            return True, workspace

    return False, None


def find_or_create_prolific_workspace(
    client: ProlificClient,
    title: str,
    id: Optional[str] = None,
) -> Workspace:
    """Find or create a Prolific Workspace by title or ID"""
    found_workspace, workspace = _find_prolific_workspace(client, title, id)

    if found_workspace:
        return workspace

    try:
        workspace: Workspace = client.Workspaces.create(title=title)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not create a workspace with title "{title}"')
        raise

    return workspace


# --- Projects ---
def _find_prolific_project(
    client: ProlificClient,
    workspace_id: str,
    title: str,
    id: Optional[str] = None,
) -> Tuple[bool, Optional[Project]]:
    """Find a Prolific Project by title or ID"""
    try:
        projects: List[Project] = client.Projects.list_for_workspace(workspace_id)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not get projects for worspace "{workspace_id}"')
        raise

    for project in projects:
        if id and project.id == id:
            return True, project
        if project.title == title:
            return True, project

    return False, None


def find_or_create_prolific_project(
    client: ProlificClient,
    workspace_id: str,
    title: str,
    id: Optional[str] = None,
) -> Optional[Project]:
    """Find or create a Prolific Workspace by title or ID"""
    found_project, project = _find_prolific_project(client, workspace_id, title, id)

    if found_project:
        return project

    try:
        project: Project = client.Projects.create_for_workspace(
            workspace_id=workspace_id,
            title=title,
        )
    except (ProlificException, ValidationError):
        logger.exception(f'Could not create a project with title "{title}"')
        raise

    return project


# --- Eligibility Requirements ---
def _convert_eligibility_requirements(value: List[dict]) -> List[dict]:
    """
    Convert short format of Eligibility Requirements to Prolific format
    :param value: list of dicts such as
        [{
            # Without `web.eligibility.models.` as API requires. We will add it in the code
            'name': 'AgeRangeEligibilityRequirement',
            # Prolific Eligibility Requirement attributes and its values
            'min_age': 18,
            'max_age': 100,
        }, ...]
    :return: reformatted Prolific value, prepared for API request
    """
    eligibility_requirements = []

    try:
        for conf_eligibility_requirement in value:
            name = conf_eligibility_requirement.get("name")

            if cls := getattr(eligibility_requirement_classes, name, None):
                cls_kwargs = {}
                for param_name in cls.params():
                    if param_name in conf_eligibility_requirement:
                        cls_kwargs[param_name] = conf_eligibility_requirement[param_name]
                eligibility_requirements.append(cls(**cls_kwargs).to_prolific_dict())
    except Exception:
        logger.exception("Could not convert passed Eligibility Requirements")
        _output_available_eligibility_requirements()
        raise

    return eligibility_requirements


def _output_available_eligibility_requirements():
    """
    Output a human-readable log message saying
    what Eligibility Requirements and with what parameters are available.
    """
    available_classes = inspect.getmembers(
        sys.modules[eligibility_requirement_classes.__name__],
        inspect.isclass,
    )
    # fmt: off
    log_classes_dicts = [{
        "name": c[0],
        **{p: "<value>" for p in c[1].params()}
    } for c in available_classes]
    logger.info(
        f"Available Eligibility Requirements in short form for config:\n" +
        "\n".join([str(i) for i in log_classes_dicts])
    )
    # fmt: on


def delete_qualification(client: ProlificClient, id: str) -> bool:
    """
    Delete a qualification (Prolific Participant Group) by ID
    :param id: Prolific Participant Group's ID
    """
    try:
        client.ParticipantGroups.remove(id)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not remove a qualification with ID "{id}"')
        raise
    return True


def _find_qualification(
    client: ProlificClient,
    prolific_project_id: str,
    qualification_name: str,
) -> Tuple[bool, Optional[ParticipantGroup]]:
    """Find a qualification (Prolific Participant Group) by name"""
    try:
        qualifications: List[ParticipantGroup] = client.ParticipantGroups.list(
            project_id=prolific_project_id,
        )
    except (ProlificException, ValidationError):
        logger.exception(f'Could not receive a qualifications for project "{prolific_project_id}"')
        raise

    for qualification in qualifications:
        if qualification.name == qualification_name:
            return True, qualification

    return False, None


def create_qualification(
    client: ProlificClient,
    prolific_project_id: str,
    qualification_name: str,
) -> Optional[ParticipantGroup]:
    """Create a qualification (Prolific Participant Group) by name"""
    try:
        qualification: ParticipantGroup = client.ParticipantGroups.create(
            project_id=prolific_project_id,
            name=qualification_name,
        )
    except (ProlificException, ValidationError):
        logger.exception(
            f"Could not create a qualification "
            f'for project "{prolific_project_id}" with name "{qualification_name}"'
        )
        raise

    return qualification


def find_or_create_qualification(
    client: ProlificClient,
    prolific_project_id: str,
    qualification_name: str,
    *args,
    **kwargs,
) -> Optional[ParticipantGroup]:
    """Find or create a qualification (Prolific Participant Group) by name"""
    found_qualification, qualification = _find_qualification(
        client,
        prolific_project_id,
        qualification_name,
    )

    if found_qualification:
        return qualification

    qualification = create_qualification(
        client,
        prolific_project_id,
        qualification_name,
    )

    return qualification


# --- Studies ---
def _ec2_external_url(task_run_config: "DictConfig") -> str:
    c = constants
    url = ec2_architect.get_full_domain(args=task_run_config)
    url_with_args = (
        f"{url}?"
        f"{c.STUDY_URL_PARTICIPANT_ID_PARAM}={c.STUDY_URL_PARTICIPANT_ID_PARAM_PROLIFIC_VAR}"
        f"&{c.STUDY_URL_STUDY_ID_PARAM}={c.STUDY_URL_STUDY_ID_PARAM_PROLIFIC_VAR}"
        f"&{c.STUDY_URL_SUBMISSION_ID_PARAM}={c.STUDY_URL_SUBMISSION_ID_PARAM_PROLIFIC_VAR}"
    )
    return url_with_args


def _is_ec2_architect(task_run_config: "DictConfig") -> bool:
    return task_run_config.architect._architect_type == ec2_architect.ARCHITECT_TYPE


def _get_external_study_url(task_run_config: "DictConfig") -> str:
    if _is_ec2_architect(task_run_config):
        external_study_url = _ec2_external_url(task_run_config)
    else:
        external_study_url = task_run_config.provider.prolific_external_study_url
    return external_study_url


def create_study(
    client: ProlificClient,
    task_run_config: "DictConfig",
    prolific_project_id: str,
    eligibility_requirements: Optional[List[Dict]] = None,
    *args,
    **kwargs,
) -> Study:
    """Create a task (Prolific Study)"""

    def compose_completion_codes(code_suffix: str) -> List[dict]:
        return [
            dict(
                code=f"{constants.StudyCodeType.COMPLETED}_{code_suffix}",
                code_type=constants.StudyCodeType.COMPLETED,
                actions=[
                    dict(
                        action=constants.StudyAction.MANUALLY_REVIEW,
                    ),
                ],
            ),
        ]

    # Task info
    name = task_run_config.task.task_title
    description = task_run_config.task.task_description
    # How much are you going to pay the participants in cents. We use the currency of your account.
    reward_in_cents = task_run_config.task.task_reward

    # Provider-specific info

    # Default minimum value to create a Study (will be auto-incremented later when launching Units)
    total_available_places = 1
    estimated_completion_time_in_minutes = (
        task_run_config.provider.prolific_estimated_completion_time_in_minutes
    )
    external_study_url = _get_external_study_url(task_run_config)
    prolific_id_option = task_run_config.provider.prolific_id_option

    eligibility_requirements = eligibility_requirements or []
    prolific_eligibility_requirements = _convert_eligibility_requirements(eligibility_requirements)

    # Initially provide a random completion code during study
    completion_codes_random = compose_completion_codes(uuid.uuid4().hex[:5])

    logger.debug(f"Initial completion codes for creating Study: {completion_codes_random}")

    try:
        study: Study = client.Studies.create(
            project=prolific_project_id,
            name=name,
            internal_name=name,
            description=description,
            external_study_url=external_study_url,
            prolific_id_option=prolific_id_option,
            completion_option=constants.StudyCompletionOption.CODE,
            completion_codes=completion_codes_random,
            total_available_places=int(total_available_places),
            estimated_completion_time=int(estimated_completion_time_in_minutes),
            reward=int(reward_in_cents),
            eligibility_requirements=prolific_eligibility_requirements,
            submissions_config=dict(
                max_submissions_per_participant=-1,
            ),
        )

        #  Immediately update `completion_codes` in created Study, with just received Study ID.
        #  This code will be used to redirect worker to Prolific's "Submission Completed" page
        #  (see `mephisto.abstractions.providers.prolific.wrap_crowd_source.handleSubmitToProvider`)
        completion_codes_with_study_id = compose_completion_codes(study.id)
        logger.debug(f"Final completion codes for updating Study: {completion_codes_with_study_id}")
        study: Study = client.Studies.update(
            id=study.id,
            completion_codes=completion_codes_with_study_id,
        )
        logger.debug(f"Study was updated successfully! {study.completion_codes=}")
    except (ProlificException, ValidationError):
        logger.exception(
            f'Could not create a Study with name "{name}" and instructions "{description}"'
        )
        raise

    return study


def increase_total_available_places_for_study(client: ProlificClient, study_id: str) -> Study:
    study: Study = get_study(client, study_id)

    try:
        client.Studies.update(
            id=study.id,
            total_available_places=study.total_available_places + 1,
        )
    except (ProlificException, ValidationError):
        logger.exception(f'Could not increase `total_available_places` for a Study "{study_id}"')
        raise

    return study


def get_study(client: ProlificClient, study_id: str) -> Study:
    try:
        study: Study = client.Studies.retrieve(id=study_id)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not retreive a Study "{study_id}"')
        raise
    return study


def publish_study(client: ProlificClient, study_id: str) -> str:
    try:
        client.Studies.publish(id=study_id)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not publish a Study "{study_id}"')
        raise
    return study_id


def stop_study(client: ProlificClient, study_id: str) -> Study:
    try:
        study: Study = client.Studies.stop(id=study_id)
        logger.debug(f'Study "{study_id}" was stopped successfully!')
    except (ProlificException, ValidationError):
        logger.exception(f'Could not stop a Study "{study_id}"')
        raise

    return study


def expire_study(client: ProlificClient, study_id: str) -> Study:
    """
    Prolific Studies don't have EXPIRED status,
    so we mark it as COMPLETED and add `_EXPIRED` to the end of `Study.internal_name` field.
    Statuses: https://docs.prolific.co/docs/api-docs/public/#tag/Studies/The-study-object
    """
    try:
        study: Study = get_study(client, study_id)
        client.Studies.update(
            id=study_id,
            internal_name=f"{study.internal_name}_{constants.StudyStatus._EXPIRED}",
        )
        study: Study = client.Studies.stop(id=study_id)
        logger.debug(f'Study "{study_id}" was expired successfully!')
    except (ProlificException, ValidationError):
        logger.exception(f'Could not expire a Study "{study_id}"')
        raise

    return study


def is_study_expired(study: Study) -> bool:
    """
    Emulating "expired" status via internal_name of a completed Study,
    because Prolific Study object doesn't have "expired" status
    """
    Status = constants.StudyStatus
    completed_statuses = [
        Status.COMPLETED,
        Status.AWAITING_REVIEW,
    ]
    is_completed = study.status in completed_statuses
    name_with_expired_mark = study.internal_name.endswith(Status._EXPIRED)
    return is_completed and name_with_expired_mark


# --- Workers/Participants ---
def add_workers_to_qualification(
    client: ProlificClient,
    workers_ids: List[str],
    qualification_id: str,
) -> None:
    """Add workers to a qualification (Participant Group)"""
    try:
        client.ParticipantGroups.add_participants_to_group(
            id=qualification_id,
            participant_ids=workers_ids,
        )
    except (ProlificException, ValidationError):
        logger.exception(
            f'Could not add workers {workers_ids} to a qualification "{qualification_id}"'
        )
        raise

    return None


def give_worker_qualification(
    client: ProlificClient,
    worker_id: str,
    qualification_id: str,
) -> None:
    """Give a qualification to the given worker (add a worker to a Participant Group)"""
    add_workers_to_qualification(
        client,
        workers_ids=[worker_id],
        qualification_id=qualification_id,
    )


def remove_worker_qualification(
    client: ProlificClient,
    worker_id: str,
    qualification_id: str,
    *args,
    **kwargs,
) -> None:
    """Remove a qualification for the given worker (remove a worker from a Participant Group)"""
    try:
        client.ParticipantGroups.remove_participants_from_group(
            id=qualification_id,
            participant_ids=[worker_id],
        )
    except (ProlificException, ValidationError):
        logger.exception(
            f'Could not remove worker {worker_id} from a qualification "{qualification_id}"'
        )
        raise


def pay_bonus(
    client: ProlificClient,
    task_run_config: "DictConfig",
    worker_id: str,
    bonus_amount: int,  # in cents
    study_id: str,
    *args,
    **kwargs,
) -> bool:
    """
    Handles paying bonus to a worker.
    Returns True on success and False on failure (e.g. insufficient funds)
    """
    if not check_balance(
        client,
        workspace_name=task_run_config.provider.prolific_workspace_name,
    ):
        # Just in case if Prolific adds showing an available balance for an account
        logger.debug("Cannot pay bonus. Reason: Insufficient funds in your Prolific account.")
        return False

    # Unlike all other Prolific endpoints working with cents, this one requires dollars
    bonus_amount_in_dollars = bonus_amount / 100
    csv_bonuses = f"{worker_id},{bonus_amount_in_dollars}"

    try:
        bonus_obj: BonusPayments = client.Bonuses.set_up(study_id, csv_bonuses)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not set up bonuses for Study "{study_id}"')
        raise

    try:
        result: str = client.Bonuses.pay(bonus_obj.id)
        logger.debug(result)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not pay bonuses for Study "{study_id}"')
        raise

    return True


def _get_block_list_qualification(
    client: ProlificClient,
    task_run_config: "DictConfig",
) -> ParticipantGroup:
    workspace = find_or_create_prolific_workspace(
        client,
        title=task_run_config.provider.prolific_workspace_name,
    )
    project = find_or_create_prolific_project(
        client,
        workspace.id,
        title=task_run_config.provider.prolific_project_name,
    )
    block_list_qualification = find_or_create_qualification(
        client,
        project.id,
        task_run_config.provider.prolific_block_list_group_name,
    )
    return block_list_qualification


def block_worker(
    client: ProlificClient,
    task_run_config: "DictConfig",
    worker_id: str,
    *args,
    **kwargs,
) -> None:
    """Block a worker by id using the Prolific client, passes reason along"""
    block_list_qualification = _get_block_list_qualification(client, task_run_config)
    give_worker_qualification(client, worker_id, block_list_qualification.id)


def unblock_worker(
    client: ProlificClient,
    task_run_config: "DictConfig",
    worker_id: str,
    *args,
    **kwargs,
) -> None:
    """Remove a block on the given worker"""
    block_list_qualification = _get_block_list_qualification(client, task_run_config)
    remove_worker_qualification(client, worker_id, block_list_qualification.id)


def is_worker_blocked(
    client: ProlificClient,
    task_run_config: "DictConfig",
    worker_id: str,
) -> bool:
    """Determine if the given worker is blocked by this client

    Note that we're currently not using this check against Prolific "Blocked Participants" group
    and simply looked at `is_blocked` column in our datastore.
    """
    workspace = find_or_create_prolific_workspace(
        client,
        title=task_run_config.provider.prolific_workspace_name,
    )
    project = find_or_create_prolific_project(
        client,
        workspace.id,
        title=task_run_config.provider.prolific_project_name,
    )
    _, block_list_qualification = _find_qualification(
        client,
        project.id,
        task_run_config.provider.prolific_block_list_group_name,
    )

    if not block_list_qualification:
        return False

    try:
        participants: List[Participant] = client.ParticipantGroups.list_participants_for_group(
            block_list_qualification.id,
        )
    except (ProlificException, ValidationError):
        logger.exception(
            f'Could not receive a list of participants for group "{block_list_qualification.id}"'
        )
        raise

    participants_ids = [p.participant_id for p in participants]
    if worker_id in participants_ids:
        return True

    return False


def calculate_pay_amount(
    client: ProlificClient,
    task_amount: Union[int, float],
    total_available_places: int,
) -> Union[int, float]:
    try:
        total_cost: Union[int, float] = client.Studies.calculate_cost(
            reward=task_amount,
            total_available_places=total_available_places,
        )
    except (ProlificException, ValidationError):
        logger.exception("Could not calculate total cost for a study")
        raise
    return total_cost


# --- Submissions ---
def _find_submission(
    client: ProlificClient,
    study_id: str,
    worker_id: str,
) -> Optional[ListSubmission]:
    """Find a Submission by Study and Worker"""
    try:
        submissions: List[ListSubmission] = client.Submissions.list(study_id=study_id)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not receive submissions for study "{study_id}"')
        raise

    for submission in submissions:
        if submission.participant_id == worker_id:
            return submission

    return None


def get_submission(client: ProlificClient, submission_id: str) -> Submission:
    try:
        submission: Submission = client.Submissions.retrieve(id=submission_id)
    except (ProlificException, ValidationError):
        logger.exception(f'Could not retreive a Submission "{submission_id}"')
        raise
    return submission


def approve_work(
    client: ProlificClient,
    study_id: str,
    worker_id: str,
) -> Union[Submission, None]:
    submission: ListSubmission = _find_submission(client, study_id, worker_id)

    if not submission:
        logger.warning(f'No submission found for study "{study_id}" and participant "{worker_id}"')
        return None

    # TODO (#1008): Handle other statuses later (when Submission was reviewed in Prolific UI)
    if submission.status == constants.SubmissionStatus.AWAITING_REVIEW:
        try:
            submission: Submission = client.Submissions.approve(submission.id)
            return submission
        except (ProlificException, ValidationError):
            logger.exception(
                f'Could not approve submission for study "{study_id}" and participant "{worker_id}"'
            )
            raise
    else:
        logger.warning(
            f'Cannot approve submission "{submission.id}" with status "{submission.status}"'
        )

    return None


def reject_work(
    client: ProlificClient,
    study_id: str,
    worker_id: str,
) -> Union[Submission, None]:
    submission: ListSubmission = _find_submission(client, study_id, worker_id)

    if not submission:
        logger.warning(f'No submission found for study "{study_id}" and participant "{worker_id}"')
        return None

    # TODO (#1008): Handle other statuses later (when Submission was reviewed in Prolific UI)
    if submission.status == constants.SubmissionStatus.AWAITING_REVIEW:
        try:
            submission: Submission = client.Submissions.reject(submission.id)
            return submission
        except (ProlificException, ValidationError):
            logger.exception(
                f'Could not reject submission for study "{study_id}" and participant "{worker_id}"'
            )
            raise
    else:
        logger.warning(
            f'Cannot reject submission "{submission.id}" with status "{submission.status}"'
        )

    return None
