#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import itertools
from typing import Dict
from typing import List
from typing import Tuple

from .common_validation import validate_config_dict_item
from .config_validation_constants import AVAILABLE_TASK_ATTRS
from .config_validation_constants import TOKENS_VALUES_KEY
from .separate_token_values_config import validate_separate_token_values_config
from .utils import make_error_message
from .utils import read_config_file
from .utils import write_config_to_file

TokensPermutationType = List[Dict[str, Dict[str, List[str]]]]


def validate_token_sets_values_config(config_data: List[dict]) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_data, list):
        is_valid = False
        errors.append("Config must be a JSON Array.")

    if config_data:
        if not all(config_data):
            is_valid = False
            errors.append("Config must contain at least one non-empty item.")

        # Ensure each token set has correct JSON structure
        for item in config_data:
            item_is_valid = validate_config_dict_item(
                item,
                "item_tokens_values",
                AVAILABLE_TASK_ATTRS,
                errors,
            )
            if not item_is_valid:
                is_valid = False

        # Ensure all token sets have the same set of keys (i.e. token names)
        token_names_from_token_sets_values_config = [
            tuple(sorted(token_set_values_data.get(TOKENS_VALUES_KEY, {}).keys()))
            for token_set_values_data in config_data
        ]
        if len(set(token_names_from_token_sets_values_config)) > 1:
            is_valid = False
            errors.append("Some token sets contain dissimilar set of token names.")

    return is_valid, errors


def _premutate_separate_tokens(data: Dict[str, List[str]]) -> TokensPermutationType:
    all_permutations = []
    # Make a list to iterate many times
    data_keys = list(data.keys())

    # Collect a list of values lists in data keys order
    sorted_values_lists: List[list] = [values for token, values in data.items()]

    # Making a list of premutated dicts
    for i, row in enumerate(itertools.product(*sorted_values_lists, repeat=1)):
        single_permudation = {}
        for y, key in enumerate(data_keys):
            single_permudation[key] = row[y]

        all_permutations.append(
            {
                TOKENS_VALUES_KEY: single_permudation,
            }
        )

    return all_permutations


def update_token_sets_values_config_with_premutated_data(
    separate_token_values_config_path: str,
    token_sets_values_config_path: str,
):
    # Read JSON from files
    separate_token_values_config_data = read_config_file(separate_token_values_config_path)

    (
        separate_token_values_config_is_valid,
        separate_token_values_config_errors,
    ) = validate_separate_token_values_config(separate_token_values_config_data)

    errors = []
    if not separate_token_values_config_is_valid:
        errors.append(
            make_error_message(
                "Separate token values config is invalid",
                separate_token_values_config_errors,
            )
        )

    if errors:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(errors))

    premutated_data = _premutate_separate_tokens(separate_token_values_config_data)

    write_config_to_file(premutated_data, token_sets_values_config_path)
