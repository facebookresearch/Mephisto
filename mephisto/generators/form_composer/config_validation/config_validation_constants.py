#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import Union

AvailableAttrsType = Dict[str, Dict[str, Union[type, bool]]]

TOKENS_VALUES_KEY = "tokens_values"
FILE_URL_TOKEN_KEY = "file_location"
INSERTIONS_PATH_NAME = "insertions"
CUSTOM_VALIDATORS_JS_FILE_NAME = "custom_validators.js"
CUSTOM_TRIGGERS_JS_FILE_NAME = "custom_triggers.js"
CUSTOM_VALIDATORS_JS_FILE_NAME_ENV_KEY = "WEBAPP__FORM_COMPOSER__CUSTOM_VALIDATORS"
CUSTOM_TRIGGERS_JS_FILE_NAME_ENV_KEY = "WEBAPP__FORM_COMPOSER__CUSTOM_TRIGGERS"
METADATA_FORM_KEY = "form_metadata"

AVAILABLE_CONFIG_ATTRS: AvailableAttrsType = {
    "form": {
        "type": dict,
        "required": True,
    },
    METADATA_FORM_KEY: {
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

COMMON_AVAILABLE_FIELD_ATTRS: AvailableAttrsType = {
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
    "label": {
        "type": str,
        "required": True,
    },
    "name": {
        "type": str,
        "required": True,
    },
    "placeholder": {
        "type": str,
        "required": False,
    },
    "show_preview": {
        "type": bool,
        "required": False,
    },
    "tooltip": {
        "type": str,
        "required": False,
    },
    "triggers": {
        "type": dict,
        "required": False,
    },
    "type": {
        "type": str,
        "required": True,
    },
    "validators": {
        "type": dict,
        "required": False,
    },
    "value": {
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

AVAILABLE_TASK_ATTRS: AvailableAttrsType = {
    TOKENS_VALUES_KEY: {
        "type": dict,
        "required": True,
    },
}

PY_JSON_TYPES_MAPPING: Dict[type, str] = {
    bool: "Boolean",
    dict: "Object",
    float: "Number(decimal)",
    int: "Number(integer)",
    list: "Array",
    str: "String",
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
