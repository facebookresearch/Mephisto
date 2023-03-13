#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from omegaconf import DictConfig

from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.utils.logger_core import get_logger

PROLIFIC_BUDGET = 100000.0
PROLIFIC_CONFIG_DIR = '~/.prolific/'
PROLIFIC_CONFIG_PATH = os.path.join(PROLIFIC_CONFIG_DIR, 'credentials')

logger = get_logger(name=__name__)


def get_prolific_api_key() -> Union[str, None]:
    credentials_path = os.path.expanduser(PROLIFIC_CONFIG_PATH)
    if os.path.exists(credentials_path):
        with open(credentials_path, 'r') as f:
            api_key = f.read().strip()
            return api_key
    return None


PROLIFIC_API_KEY = os.environ.get('PROLIFIC_API_KEY', None) or get_prolific_api_key()


def check_credentials(*args, **kwargs) -> bool:
    """Check whether API KEY is correct"""
    # TODO (FB-3): Implement
    pass


def setup_credentials(
    profile_name: str, register_args: Optional[ProviderArgs],
) -> bool:
    if not os.path.exists(os.path.expanduser(PROLIFIC_CONFIG_DIR)):
        os.mkdir(os.path.expanduser(PROLIFIC_CONFIG_DIR))

    with open(os.path.expanduser(PROLIFIC_CONFIG_PATH), 'w') as f:
        f.write(register_args.api_key)

    return True


def check_balance(*args, **kwargs) -> Union[float, int]:
    """
    Checks to see if there is at least balance_needed amount in the
    requester account, returns True if the balance is greater than
    balance_needed
    """
    # TODO (FB-3): Implement
    return PROLIFIC_BUDGET


def delete_qualification(
    client: Any, # TODO (FB-3): Implement
    qualification_id: str,
) -> None:
    """Deletes a qualification by id"""
    client.Team.delete(qualification_id)


def find_qualification(
    client: Any,  # TODO (FB-3): Implement
    qualification_name: str,
) -> Tuple[bool, Optional[str]]:
    try:
        qualifications = []  # TODO (FB-3): Implement
    except Exception:  # TODO (FB-3): Implement
        logger.exception(f'Could not receive a qualifications')
        raise

    for qualification in qualifications:
        if qualification.name == qualification_name:
            return True, qualification.id

    return True, None


def find_or_create_qualification(
    client: Any,  # TODO (FB-3): Implement
    qualification_name: str,
    description: str,
) -> Optional[str]:
    found_qualification, qualification_id = find_qualification(client, qualification_name)

    if found_qualification:
        return qualification_id

    try:
        # TODO (FB-3): Implement
        qualification = None
    except Exception:  # TODO (FB-3): Implement
        logger.exception(
            f'Could not create a qualification with name "{qualification_name}" '
            f'and description "{description}"'
        )
        raise

    return qualification.id if qualification else None


def create_study(
    client: Any,  # TODO (FB-3): Implement
    task_args: "DictConfig",
    qualifications: List[Dict[str, Any]],
) -> str:
    """Create a Prolific Project"""
    name = task_args.task_title
    instructions = task_args.task_description

    try:
        # TODO (FB-3): Implement
        pass
    except Exception:  # TODO (FB-3): Implement
        logger.exception(
            f'Could not create a Study with name "{name}" '
            f'and instructions "{instructions}"'
        )
        raise

    study_id = None
    return study_id

