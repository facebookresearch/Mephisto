from typing import List
from typing import Tuple

from .common_validation import validate_config_dict_item
from .config_validation_constants import AVAILABLE_CONFIG_ATTRS
from .config_validation_constants import AVAILABLE_FIELD_ATTRS_BY_TYPE
from .config_validation_constants import AVAILABLE_FIELDSET_ATTRS
from .config_validation_constants import AVAILABLE_FORM_ATTRS
from .config_validation_constants import AVAILABLE_ROW_ATTRS
from .config_validation_constants import AVAILABLE_SECTION_ATTRS
from .config_validation_constants import AvailableAttrsType


def _add_values_for_unique_item_attrs(item: dict, values_for_unique_attrs: List[str]) -> List[str]:
    unique_attr_names = ["id", "name"]

    for attr_name in unique_attr_names:
        attr_value = item.get(attr_name)
        if attr_value is not None:
            values_for_unique_attrs.append(attr_value)

    return values_for_unique_attrs


def _duplicate_values_exist(unique_names: List[str], errors: List[str]) -> bool:
    is_valid = True

    checked_unique_values = set()
    duplicated_unique_names = [
        unique_name for unique_name in unique_names
        if unique_name in checked_unique_values or checked_unique_values.add(unique_name)
    ]
    if duplicated_unique_names:
        is_valid = False
        errors.append(
            f"Found duplicated unique names and IDs: "
            f"{', '.join(duplicated_unique_names)}"
        )

    return is_valid


def validate_form_config(config_json: dict) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_json, dict):
        is_valid = False
        errors.append("Config must be `Object`.")

    if config_json.keys() != AVAILABLE_CONFIG_ATTRS.keys():
        is_valid = False
        errors.append(
            f"Config must contain only next attributes: "
            f"{', '.join(AVAILABLE_CONFIG_ATTRS.keys())}."
        )

    items_to_validate: List[Tuple[dict, str, AvailableAttrsType]] = []
    unique_names = []

    # Add main config level
    items_to_validate.append((config_json, "Config", AVAILABLE_CONFIG_ATTRS))

    # Add form
    form = config_json["form"]
    items_to_validate.append((form, 'form', AVAILABLE_FORM_ATTRS))
    _add_values_for_unique_item_attrs(form, unique_names)

    # Add form sections
    sections = form["sections"]
    for section in sections:
        items_to_validate.append((section, "section", AVAILABLE_SECTION_ATTRS))
        _add_values_for_unique_item_attrs(section, unique_names)

        # Add fieldsets
        fieldsets = section["fieldsets"]
        for fieldset in fieldsets:
            items_to_validate.append((fieldset, "fieldset", AVAILABLE_FIELDSET_ATTRS))
            _add_values_for_unique_item_attrs(fieldset, unique_names)

            # Add rows
            rows = fieldset["rows"]
            for row in rows:
                items_to_validate.append((row, "row", AVAILABLE_ROW_ATTRS))
                _add_values_for_unique_item_attrs(row, unique_names)

                # Add fields
                fields = row["fields"]
                for field in fields:
                    field_type = field.get("type")
                    available_field_attrs = AVAILABLE_FIELD_ATTRS_BY_TYPE.get(field_type)

                    if not available_field_attrs:
                        errors.append(f"Object `field` mast have `type` attribute.")
                        is_valid = False
                        continue

                    items_to_validate.append((field, "field", available_field_attrs))
                    _add_values_for_unique_item_attrs(field, unique_names)

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
