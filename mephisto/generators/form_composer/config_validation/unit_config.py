#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional
from typing import Tuple

from mephisto.generators.generators_utils.config_validation.common_validation import (
    validate_config_dict_item,
)
from mephisto.generators.generators_utils.config_validation.config_validation_constants import (
    AvailableAttrsType,
)
from mephisto.generators.generators_utils.config_validation.unit_config import (
    collect_values_for_unique_attrs_from_item,
)
from mephisto.generators.generators_utils.config_validation.unit_config import (
    duplicate_values_exist,
)
from mephisto.generators.generators_utils.config_validation.unit_config import UniqueAttrsType


def validate_unit_config(
    config_data: dict,
    data_path: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    from .config_validation_constants import AVAILABLE_CONFIG_ATTRS
    from .config_validation_constants import AVAILABLE_FIELD_ATTRS_BY_TYPE
    from .config_validation_constants import AVAILABLE_FIELDSET_ATTRS
    from .config_validation_constants import AVAILABLE_FORM_ATTRS
    from .config_validation_constants import AVAILABLE_ROW_ATTRS
    from .config_validation_constants import AVAILABLE_SECTION_ATTRS
    from .config_validation_constants import AVAILABLE_SUBMIT_BUTTON_ATTRS

    is_valid = True
    errors = []

    if not isinstance(config_data, dict):
        is_valid = False
        errors.append("Unit config must be a key/value JSON Object.")

    elif not validate_config_dict_item(
        config_data,
        "form",
        AVAILABLE_CONFIG_ATTRS,
        errors=errors,
        data_path=data_path,
    ):
        is_valid = False
        errors.append(
            f"Unit config must contain only these attributes: "
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
    collect_values_for_unique_attrs_from_item(form, unique_names)

    # Add submit button
    submit_button = form["submit_button"]
    items_to_validate.append((submit_button, "submit_button", AVAILABLE_SUBMIT_BUTTON_ATTRS))

    # Add form sections
    sections = form["sections"]
    for section in sections:
        items_to_validate.append((section, "section", AVAILABLE_SECTION_ATTRS))
        collect_values_for_unique_attrs_from_item(section, unique_names)

        # Add fieldsets
        fieldsets = section["fieldsets"]
        for fieldset in fieldsets:
            items_to_validate.append((fieldset, "fieldset", AVAILABLE_FIELDSET_ATTRS))
            collect_values_for_unique_attrs_from_item(fieldset, unique_names)

            # Add rows
            rows = fieldset["rows"]
            for row in rows:
                items_to_validate.append((row, "row", AVAILABLE_ROW_ATTRS))
                collect_values_for_unique_attrs_from_item(row, unique_names)

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
                    collect_values_for_unique_attrs_from_item(field, unique_names)

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
