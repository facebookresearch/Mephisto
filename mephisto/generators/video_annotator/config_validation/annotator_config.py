#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from mephisto.generators.form_composer.config_validation.common_validation import (
    validate_config_dict_item,
)
from mephisto.generators.form_composer.config_validation.form_config import (
    collect_values_for_unique_attrs_from_item,
)
from mephisto.generators.form_composer.config_validation.form_config import duplicate_values_exist
from .config_validation_constants import AVAILABLE_CONFIG_ATTRS
from .config_validation_constants import AVAILABLE_ANNOTATOR_ATTRS
from .config_validation_constants import AVAILABLE_SUBMIT_BUTTON_ATTRS
from .config_validation_constants import AvailableAttrsType

UniqueAttrsType = Dict[str, List[str]]


def validate_annotator_config(
    config_data: dict,
    data_path: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_data, dict):
        is_valid = False
        errors.append("Annotator config must be a key/value JSON Object.")

    elif not validate_config_dict_item(
        config_data, "annotator", AVAILABLE_CONFIG_ATTRS, errors=errors, data_path=data_path
    ):
        is_valid = False
        errors.append(
            f"Annotator config must contain only these attributes: "
            f"{', '.join(AVAILABLE_CONFIG_ATTRS.keys())}."
        )

    if not is_valid:
        # return early in case configs don't even have a correst data type
        return is_valid, errors

    items_to_validate: List[Tuple[dict, str, AvailableAttrsType]] = []
    unique_names: UniqueAttrsType = {}

    # Add main config level
    items_to_validate.append((config_data, "Config", AVAILABLE_CONFIG_ATTRS))

    # Add annotator
    annotator = config_data["annotator"]
    items_to_validate.append((annotator, "annotator", AVAILABLE_ANNOTATOR_ATTRS))
    collect_values_for_unique_attrs_from_item(annotator, unique_names)

    # Add submit button
    submit_button = annotator["submit_button"]
    items_to_validate.append((submit_button, "submit_button", AVAILABLE_SUBMIT_BUTTON_ATTRS))

    # Run structure validation
    for item in items_to_validate:
        config_is_valid = validate_config_dict_item(*item, errors=errors, data_path=data_path)
        if not config_is_valid:
            is_valid = False

    # Run unique attributes validation
    has_duplicated_values_for_unique_attrs = duplicate_values_exist(unique_names, errors)
    if not has_duplicated_values_for_unique_attrs:
        is_valid = False

    return is_valid, errors
