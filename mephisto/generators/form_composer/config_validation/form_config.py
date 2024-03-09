#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import List
from typing import Tuple

from .common_validation import validate_config_dict_item
from .config_validation_constants import ATTRS_WITH_UNIQUE_NAMES
from .config_validation_constants import AVAILABLE_CONFIG_ATTRS
from .config_validation_constants import AVAILABLE_FIELD_ATTRS_BY_TYPE
from .config_validation_constants import AVAILABLE_FIELDSET_ATTRS
from .config_validation_constants import AVAILABLE_FORM_ATTRS
from .config_validation_constants import AVAILABLE_ROW_ATTRS
from .config_validation_constants import AVAILABLE_SECTION_ATTRS
from .config_validation_constants import AVAILABLE_SUBMIT_BUTTON_ATTRS
from .config_validation_constants import AvailableAttrsType

UniqueAttrsType = Dict[str, List[str]]


def _collect_values_for_unique_attrs_from_item(
    item: dict,
    values_for_unique_attrs: UniqueAttrsType,
) -> UniqueAttrsType:
    for attr_name in ATTRS_WITH_UNIQUE_NAMES:
        attr_value = item.get(attr_name)
        values_for_attr = values_for_unique_attrs.get(attr_name, [])

        if attr_value is not None:
            values_for_attr.append(attr_value)
            values_for_unique_attrs[attr_name] = values_for_attr

    return values_for_unique_attrs


def _duplicate_values_exist(unique_names: UniqueAttrsType, errors: List[str]) -> bool:
    is_valid = True

    for attr_name, unique_values in unique_names.items():
        checked_unique_values = set()
        duplicated_unique_names = [
            unique_name
            for unique_name in unique_values
            if unique_name in checked_unique_values or checked_unique_values.add(unique_name)
        ]
        if duplicated_unique_names:
            is_valid = False
            errors.append(
                f"Found duplicate names for unique attribute '{attr_name}' in your form config: "
                f"{', '.join(duplicated_unique_names)}"
            )

    return is_valid


def validate_form_config(config_data: dict) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_data, dict):
        is_valid = False
        errors.append("Form config must be a key/value JSON Object.")

    elif config_data.keys() != AVAILABLE_CONFIG_ATTRS.keys():
        is_valid = False
        errors.append(
            f"Form config must contain only these attributes: "
            f"{', '.join(AVAILABLE_CONFIG_ATTRS.keys())}."
        )

    if not is_valid:
        # return early in case configs don't even have a correst data type
        return is_valid, errors

    items_to_validate: List[Tuple[dict, str, AvailableAttrsType]] = []
    unique_names: UniqueAttrsType = {}

    # Add main config level
    items_to_validate.append((config_data, "Config", AVAILABLE_CONFIG_ATTRS))

    # Add form
    form = config_data["form"]
    items_to_validate.append((form, "form", AVAILABLE_FORM_ATTRS))
    _collect_values_for_unique_attrs_from_item(form, unique_names)

    # Add submit button
    submit_button = form["submit_button"]
    items_to_validate.append((submit_button, "submit_button", AVAILABLE_SUBMIT_BUTTON_ATTRS))

    # Add form sections
    sections = form["sections"]
    for section in sections:
        items_to_validate.append((section, "section", AVAILABLE_SECTION_ATTRS))
        _collect_values_for_unique_attrs_from_item(section, unique_names)

        # Add fieldsets
        fieldsets = section["fieldsets"]
        for fieldset in fieldsets:
            items_to_validate.append((fieldset, "fieldset", AVAILABLE_FIELDSET_ATTRS))
            _collect_values_for_unique_attrs_from_item(fieldset, unique_names)

            # Add rows
            rows = fieldset["rows"]
            for row in rows:
                items_to_validate.append((row, "row", AVAILABLE_ROW_ATTRS))
                _collect_values_for_unique_attrs_from_item(row, unique_names)

                # Add fields
                fields = row["fields"]
                for field in fields:
                    field_type = field.get("type")
                    available_field_attrs = AVAILABLE_FIELD_ATTRS_BY_TYPE.get(field_type)

                    if not available_field_attrs:
                        errors.append(
                            f"Object 'field' has unsupported 'type' attribute value: {field_type}"
                        )
                        is_valid = False
                        continue

                    items_to_validate.append((field, "field", available_field_attrs))
                    _collect_values_for_unique_attrs_from_item(field, unique_names)

    # Run structure validation
    for item in items_to_validate:
        config_is_valid = validate_config_dict_item(*item, errors=errors)
        if not config_is_valid:
            is_valid = False

    # Run unique attributes validation
    has_duplicated_values_for_unique_attrs = _duplicate_values_exist(unique_names, errors)
    if not has_duplicated_values_for_unique_attrs:
        is_valid = False

    return is_valid, errors
