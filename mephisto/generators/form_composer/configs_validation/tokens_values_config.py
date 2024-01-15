from typing import List
from typing import Tuple

from .common_validation import validate_config_dict_item
from .config_validation_constants import AVAILABLE_TASK_ATTRS


def validate_tokens_values_config(config_json: List[dict]) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_json, list):
        is_valid = False
        errors.append("Config must be `Array`.")

    if config_json:
        if not all(config_json):
            is_valid = False
            errors.append("Config must contain at least one non-empty item.")

        for item in config_json:
            unit_is_valid = validate_config_dict_item(
                item, "unit_tokens_values", AVAILABLE_TASK_ATTRS, errors,
            )
            if not unit_is_valid:
                is_valid = False

    return is_valid, errors
