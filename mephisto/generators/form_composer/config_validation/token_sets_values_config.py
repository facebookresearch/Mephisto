import itertools
import json
from json import JSONDecodeError
from typing import Dict
from typing import List
from typing import Tuple

from .common_validation import validate_config_dict_item
from .config_validation_constants import AVAILABLE_TASK_ATTRS
from .single_token_values_config import validate_single_token_values_config
from .utils import make_error_message
from .utils import read_config_file
from .utils import write_config_to_file

TokensPermutationType = List[
    Dict[
        str, Dict[
            str, List[str]
        ]
    ]
]


def validate_token_sets_values_config(config_json: List[dict]) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_json, list):
        is_valid = False
        errors.append("Config must be a JSON Array.")

    if config_json:
        if not all(config_json):
            is_valid = False
            errors.append("Config must contain at least one non-empty item.")

        for item in config_json:
            item_is_valid = validate_config_dict_item(
                item, "item_tokens_values", AVAILABLE_TASK_ATTRS, errors,
            )
            if not item_is_valid:
                is_valid = False

    return is_valid, errors


def _premutate_single_tokents(data: Dict[str, List[str]]) -> TokensPermutationType:
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
                "tokens_values": single_permudation,
            }
        )

    return all_permutations


def update_token_sets_values_config_with_premutated_data(
    single_token_values_config_path: str,
    token_sets_values_config_path: str,
):
    # Read JSON from files
    single_token_values_config_data = read_config_file(single_token_values_config_path)

    single_token_values_config_is_valid, single_token_values_config_errors = (
        validate_single_token_values_config(single_token_values_config_data)
    )

    errors = []
    if not single_token_values_config_is_valid:
        errors.append(make_error_message(
            "Single token values config is invalid.", single_token_values_config_errors,
        ))

    if errors:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(errors))

    premutated_data = _premutate_single_tokents(single_token_values_config_data)

    write_config_to_file(premutated_data, token_sets_values_config_path)
