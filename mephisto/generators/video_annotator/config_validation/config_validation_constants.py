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
METADATA_ANNOTATOR_KEY = "annotator_metadata"

AVAILABLE_CONFIG_ATTRS: AvailableAttrsType = {
    "annotator": {
        "type": dict,
        "required": True,
    },
    METADATA_ANNOTATOR_KEY: {
        "type": dict,
        "required": False,
    },
}

AVAILABLE_ANNOTATOR_ATTRS: AvailableAttrsType = {
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
    "video": {
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
    "video",
]


ATTRS_WITH_UNIQUE_NAMES = [
    "id",
    "name",
]
