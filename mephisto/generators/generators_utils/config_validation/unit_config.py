#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import List

from .utils import get_validation_mappings

UniqueAttrsType = Dict[str, List[str]]


def collect_values_for_unique_attrs_from_item(
    item: dict,
    values_for_unique_attrs: UniqueAttrsType,
) -> UniqueAttrsType:
    validation_mappings = get_validation_mappings()
    attrs_with_unique_names = validation_mappings["ATTRS_WITH_UNIQUE_NAMES"]

    for attr_name in attrs_with_unique_names:
        attr_value = item.get(attr_name)
        values_for_attr = values_for_unique_attrs.get(attr_name, [])

        if attr_value is not None:
            values_for_attr.append(attr_value)
            values_for_unique_attrs[attr_name] = values_for_attr

    return values_for_unique_attrs


def duplicate_values_exist(unique_names: UniqueAttrsType, errors: List[str]) -> bool:
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
