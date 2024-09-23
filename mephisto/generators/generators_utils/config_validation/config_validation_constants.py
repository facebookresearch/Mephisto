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
CUSTOM_VALIDATORS_JS_FILE_NAME_ENV_KEY = "WEBAPP__GENERATOR__CUSTOM_VALIDATORS"
CUSTOM_TRIGGERS_JS_FILE_NAME_ENV_KEY = "WEBAPP__GENERATOR__CUSTOM_TRIGGERS"
GENERATOR_METADATA_KEY = "form_metadata"

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
