#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Dict
from typing import List
from typing import Tuple

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from rich import print

from mephisto.generators.form_composer.constants import TOKEN_END_SYMBOLS
from mephisto.generators.form_composer.constants import TOKEN_START_SYMBOLS
from mephisto.generators.form_composer.remote_procedures import ProcedureName
from .config_validation_constants import FILE_URL_TOKEN_KEY
from .utils import get_file_urls_from_s3_storage
from .utils import read_config_file
from .utils import write_config_to_file


def validate_separate_token_values_config(
    config_data: Dict[str, List[str]],
) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_data, dict):
        is_valid = False
        errors.append("Config must be a key/value JSON Object.")
        return is_valid, errors

    for i, token_values in enumerate(config_data.items()):
        token, values = token_values

        if not values:
            is_valid = False
            errors.append(
                f"You passed empty array of values for token '{token}'. "
                f"It must contain at least one value or just remove it you left it by mistake."
            )

    return is_valid, errors


def update_separate_token_values_config_with_file_urls(
    url: str,
    separate_token_values_config_path: str,
    use_presigned_urls: bool = False,
):
    try:
        files_locations = get_file_urls_from_s3_storage(url)
    except (BotoCoreError, ClientError, NoCredentialsError) as e:
        print(f"Could not retrieve files from S3 URL '{url}'. Reason: {e}")
        return None

    if not files_locations:
        print(
            f"Could not retrieve files from '{url}' - "
            f"check if this location exists and contains files"
        )
        return None

    if use_presigned_urls:
        files_locations = [
            (
                TOKEN_START_SYMBOLS
                + f'{ProcedureName.GET_MULTIPLE_PRESIGNED_URLS}("{url}")'
                + TOKEN_END_SYMBOLS
            )
            for url in files_locations
        ]

    # Update data in existing config file, or create new if it doesn't exist
    config_data = {}
    if os.path.exists(separate_token_values_config_path):
        config_data = read_config_file(separate_token_values_config_path)

    config_data.update(
        {
            FILE_URL_TOKEN_KEY: files_locations,
        }
    )

    write_config_to_file(config_data, separate_token_values_config_path)
