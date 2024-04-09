#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import List
from typing import Optional

from .config_validation_constants import ATTRS_SUPPORTING_TOKENS
from .config_validation_constants import AvailableAttrsType
from .config_validation_constants import PY_JSON_TYPES_MAPPING
from .utils import is_insertion_file


def validate_config_dict_item(
    item: dict,
    item_log_name: str,
    available_attrs: AvailableAttrsType,
    errors: List[str],
    data_path: Optional[str] = None,
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

        if data_path:
            for attr_name in ATTRS_SUPPORTING_TOKENS:
                item_attr = item.get(attr_name)
                if not item_attr:
                    continue

                if is_insertion_file(item_attr):
                    file_path = os.path.abspath(os.path.join(data_path, item_attr))
                    if not os.path.exists(file_path):
                        is_valid = False
                        errors.append(
                            f"Could not find insertion file '{file_path}'. "
                            f"Either create the file, or update the config."
                        )

    return is_valid


def replace_path_to_file_with_its_content(
    rel_file_path: str,
    data_path: str,
) -> str:
    """
    Attributes may contain tokens whose value is relative HTML file paths.
    We replace such token values with content from the indicated file.
    """
    if not data_path:
        raise Exception(f'Received empty `data_path` when reading inserted file {rel_file_path}')
    if not rel_file_path:
        raise Exception(f'Received empty `value` when reading inserted file in {data_path}')

    if is_insertion_file(rel_file_path):
        file_path = os.path.abspath(os.path.join(data_path, rel_file_path))
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not open insertion file '{file_path}'")

        with open(file_path) as html_file:
            file_content = html_file.read()
            return file_content

    return rel_file_path
