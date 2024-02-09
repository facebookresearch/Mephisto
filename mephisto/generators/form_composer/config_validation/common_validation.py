#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .config_validation_constants import AvailableAttrsType
from .config_validation_constants import PY_JSON_TYPES_MAPPING


def validate_config_dict_item(
    item: dict,
    item_log_name: str,
    available_attrs: AvailableAttrsType,
    errors: List[str],
) -> bool:
    is_valid = True

    item_unique_name = item.get("name")
    name_error_substring = f" with name `{item_unique_name}`" if item_unique_name else ""

    item_attrs_keys = list(item.keys())
    available_attrs_keys = list(available_attrs.keys())
    required_attrs_keys = [k for k, v in available_attrs.items() if v["required"]]

    # Check for required fields
    passed_required_attrs_keys = [k for k in item_attrs_keys if k in required_attrs_keys]
    if len(required_attrs_keys) > len(passed_required_attrs_keys):
        is_valid = False
        errors.append(
            f"Object `{item_log_name}`{name_error_substring}. "
            f"Not all required attributes were specified. "
            f"Required attributes: {', '.join(required_attrs_keys)}. "
            f"Passed attributes: {', '.join(item_attrs_keys)}."
        )

    # Check item attributes
    for attr_key in item_attrs_keys:
        if attr_key not in available_attrs_keys:
            is_valid = False
            errors.append(
                f"Object `{item_log_name}`{name_error_substring} "
                f"has no available attribute with name `{attr_key}`. "
                f"Available attributes: {', '.join(available_attrs_keys)}."
            )

        attr_settings: dict = available_attrs.get(attr_key)
        if not attr_settings:
            continue

        attr_type: type = attr_settings.get("type")
        if not isinstance(item[attr_key], attr_type):
            is_valid = False
            errors.append(
                f"Attribute `{attr_key}` in object `{item_log_name}` "
                f"must be `{PY_JSON_TYPES_MAPPING[attr_type]}`."
            )

    return is_valid
