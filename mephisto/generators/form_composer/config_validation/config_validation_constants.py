#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import Union

AvailableAttrsType = Dict[str, Dict[str, Union[type, bool]]]

TOKENS_VALUES_KEY = "tokens_values"
FILE_URL_TOKEN_KEY = "file_location"

AVAILABLE_CONFIG_ATTRS: AvailableAttrsType = {
    "form": {
        "type": dict,
        "required": True,
    },
}

AVAILABLE_FORM_ATTRS: AvailableAttrsType = {
    "instruction": {
        "type": str,
        "required": False,
    },
    "sections": {
        "type": list,
        "required": True,
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
}

AVAILABLE_SECTION_ATTRS: AvailableAttrsType = {
    "collapsable": {
        "type": bool,
        "required": False,
    },
    "fieldsets": {
        "type": list,
        "required": True,
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
}

AVAILABLE_FIELDSET_ATTRS: AvailableAttrsType = {
    "help": {
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
        "required": True,
    },
}

AVAILABLE_ROW_ATTRS: AvailableAttrsType = {
    "fields": {
        "type": list,
        "required": True,
    },
    "help": {
        "type": str,
        "required": False,
    },
}

COMMON_AVAILABLE_FIELD_ATTRS: AvailableAttrsType = {
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
    "tooltip": {
        "type": str,
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
    },
    "email": COMMON_AVAILABLE_FIELD_ATTRS,
    "file": COMMON_AVAILABLE_FIELD_ATTRS,
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
