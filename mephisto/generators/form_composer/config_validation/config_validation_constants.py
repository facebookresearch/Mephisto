#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict

from mephisto.generators.generators_utils.config_validation.config_validation_constants import (
    AvailableAttrsType,
)
from mephisto.generators.generators_utils.config_validation.config_validation_constants import (
    COMMON_AVAILABLE_FIELD_ATTRS,
)

FORM_COMPOSER_TASK_TAG = "form-composer"

GENERATOR_METADATA_KEY = "form_metadata"

AVAILABLE_CONFIG_ATTRS: AvailableAttrsType = {
    "form": {
        "type": dict,
        "required": True,
    },
    GENERATOR_METADATA_KEY: {
        "type": dict,
        "required": False,
    },
}

AVAILABLE_FORM_ATTRS: AvailableAttrsType = {
    "classes": {
        "type": str,
        "required": False,
    },
    "id": {
        "type": str,
        "required": False,
    },
    "instruction": {
        "type": str,
        "required": False,
    },
    "sections": {
        "type": list,
        "required": True,
    },
    "show_instructions_as_modal": {
        "type": bool,
        "required": False,
    },
    "submit_button": {
        "type": dict,
        "required": True,
    },
    "title": {
        "type": str,
        "required": True,
    },
}

AVAILABLE_SUBMIT_BUTTON_ATTRS: AvailableAttrsType = {
    "classes": {
        "type": str,
        "required": False,
    },
    "id": {
        "type": str,
        "required": False,
    },
    "instruction": {
        "type": str,
        "required": False,
    },
    "text": {
        "type": str,
        "required": True,
    },
    "tooltip": {
        "type": str,
        "required": False,
    },
    "triggers": {
        "type": dict,
        "required": False,
    },
}

AVAILABLE_SECTION_ATTRS: AvailableAttrsType = {
    "classes": {
        "type": str,
        "required": False,
    },
    "collapsable": {
        "type": bool,
        "required": False,
    },
    "fieldsets": {
        "type": list,
        "required": True,
    },
    "id": {
        "type": str,
        "required": False,
    },
    "initially_collapsed": {
        "type": bool,
        "required": False,
    },
    "instruction": {
        "type": str,
        "required": False,
    },
    "name": {
        "type": str,
        "required": False,
    },
    "title": {
        "type": str,
        "required": True,
    },
    "triggers": {
        "type": dict,
        "required": False,
    },
}

AVAILABLE_FIELDSET_ATTRS: AvailableAttrsType = {
    "classes": {
        "type": str,
        "required": False,
    },
    "help": {
        "type": str,
        "required": False,
    },
    "id": {
        "type": str,
        "required": False,
    },
    "instruction": {
        "type": str,
        "required": False,
    },
    "name": {
        "type": str,
        "required": False,
    },
    "rows": {
        "type": list,
        "required": True,
    },
    "title": {
        "type": str,
        "required": False,
    },
}

AVAILABLE_ROW_ATTRS: AvailableAttrsType = {
    "classes": {
        "type": str,
        "required": False,
    },
    "fields": {
        "type": list,
        "required": True,
    },
    "help": {
        "type": str,
        "required": False,
    },
    "id": {
        "type": str,
        "required": False,
    },
}

AVAILABLE_FIELD_ATTRS_BY_TYPE: Dict[str, AvailableAttrsType] = {
    "checkbox": {
        **COMMON_AVAILABLE_FIELD_ATTRS,
        "options": {
            "type": list,
            "required": True,
        },
        "value": {
            "type": dict,
            "required": False,
        },
    },
    "email": COMMON_AVAILABLE_FIELD_ATTRS,
    "file": COMMON_AVAILABLE_FIELD_ATTRS,
    "hidden": COMMON_AVAILABLE_FIELD_ATTRS,
    "input": COMMON_AVAILABLE_FIELD_ATTRS,
    "radio": {
        **COMMON_AVAILABLE_FIELD_ATTRS,
        "options": {
            "type": list,
            "required": True,
        },
    },
    "select": {
        **COMMON_AVAILABLE_FIELD_ATTRS,
        "multiple": {
            "type": bool,
            "required": False,
        },
        "options": {
            "type": list,
            "required": True,
        },
        "value": {
            "type": (str, list),
            "required": False,
        },
    },
    "textarea": COMMON_AVAILABLE_FIELD_ATTRS,
}

ATTRS_SUPPORTING_TOKENS = [
    "help",
    "instruction",
    "label",
    "title",
    "tooltip",
]


ATTRS_WITH_UNIQUE_NAMES = [
    "id",
    "name",
]


_config_validation_path = "mephisto.generators.form_composer.config_validation"
VALIDATION_MAPPING = {
    "ATTRS_SUPPORTING_TOKENS": (
        f"{_config_validation_path}.config_validation_constants.ATTRS_SUPPORTING_TOKENS"
    ),
    "ATTRS_WITH_UNIQUE_NAMES": (
        f"{_config_validation_path}.config_validation_constants.ATTRS_WITH_UNIQUE_NAMES"
    ),
    "GENERATOR_METADATA_KEY": (
        f"{_config_validation_path}.config_validation_constants.GENERATOR_METADATA_KEY"
    ),
    "collect_unit_config_items_to_extrapolate": (
        f"{_config_validation_path}.task_data_config.collect_unit_config_items_to_extrapolate"
    ),
    "validate_unit_config": f"{_config_validation_path}.unit_config.validate_unit_config",
}
