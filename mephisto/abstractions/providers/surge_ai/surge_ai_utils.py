#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Qualification -> Surge AI `Team`
"""

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import surge
from omegaconf import DictConfig
from surge import errors as surge_errors

from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.utils.logger_core import get_logger

SURGE_AI_BUDGET = 100000.0
SURGE_AI_CONFIG_DIR = '~/.surge_ai/'
SURGE_AI_CONFIG_PATH = os.path.join(SURGE_AI_CONFIG_DIR, 'credentials')

logger = get_logger(name=__name__)

# Surge AI library does not have main exception class (wierd),
# so we need to catch all their exceptions like this
surge_exceptions = (
    surge_errors.SurgeRequestError,
    surge_errors.SurgeMissingAPIKeyError,
    surge_errors.SurgeMissingIDError,
    surge_errors.SurgeMissingAttributeError,
    surge_errors.SurgeProjectQuestionError,
    surge_errors.SurgeTaskDataError,
)


def get_surge_ai_api_key() -> Union[str, None]:
    credentials_path = os.path.expanduser(SURGE_AI_CONFIG_PATH)
    if os.path.exists(credentials_path):
        with open(credentials_path, 'r') as f:
            api_key = f.read().strip()
            return api_key
    return None


surge.api_key = os.environ.get('SURGE_API_KEY', None) or get_surge_ai_api_key()


def check_credentials(*args, **kwargs) -> bool:
    """Check whether API KEY is correct"""
    try:
        # Make a simple request to the API
        surge.Project.list(page=1)
        return True
    except surge_exceptions:
        return False


def setup_credentials(
    profile_name: str, register_args: Optional[ProviderArgs],
) -> bool:
    if not os.path.exists(os.path.expanduser(SURGE_AI_CONFIG_DIR)):
        os.mkdir(os.path.expanduser(SURGE_AI_CONFIG_DIR))

    with open(os.path.expanduser(SURGE_AI_CONFIG_PATH), 'w') as f:
        f.write(register_args.api_key)

    return True


def check_balance(*args, **kwargs) -> Union[float, int]:
    """
    Checks to see if there is at least balance_needed amount in the
    requester account, returns True if the balance is greater than
    balance_needed
    """
    # TODO: Change this later.
    #  Surge AI does not return account budget, so we always return positive value
    return SURGE_AI_BUDGET


def delete_qualification(client, qualification_id: str) -> None:
    """Deletes a qualification by id"""
    client.Team.delete(qualification_id)


def find_qualification(client: surge, qualification_name: str) -> Tuple[bool, Optional[str]]:
    try:
        qualifications = client.Team.list()
    except surge_exceptions:
        logger.exception(f'Could not receive a qualifications')
        raise

    for qualification in qualifications:
        if qualification.name == qualification_name:
            return True, qualification.id

    return True, None


def find_or_create_qualification(
    client: surge, qualification_name: str, description: str,
) -> Optional[str]:
    found_qualification, qualification_id = find_qualification(client, qualification_name)

    if found_qualification:
        return qualification_id

    try:
        qualification = client.Team.create(name=qualification_name, description=description)
    except surge_exceptions:
        logger.exception(
            f'Could not create a qualification with name "{qualification_name}" '
            f'and description "{description}"'
        )
        raise

    return qualification.id


def create_project(
    client: surge, task_args: "DictConfig", qualifications: List[Dict[str, Any]],
) -> str:
    """Create a Surge AI Project"""
    name = task_args.task_title
    instructions = task_args.task_description

    try:
        project = client.Project.create(
            instructions=instructions,
            name=name,
            payment_per_response=task_args.task_reward,
            qualifications_required=[q['surge_ai_qualification_id'] for q in qualifications],
        )
    except surge_exceptions:
        logger.exception(
            f'Could not create a Project with name "{name}" '
            f'and instructions "{instructions}"'
        )
        raise

    project_id = project.id
    return project_id

