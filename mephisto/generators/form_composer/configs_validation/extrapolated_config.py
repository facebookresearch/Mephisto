#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os.path
import re
from copy import deepcopy
from json import JSONDecodeError
from typing import List

from mephisto.generators.form_composer.constants import JSON_IDENTATION
from mephisto.utils.logger_core import get_logger
from .config_validation_constants import ATTRS_SUPPORTING_TOKENS
from .form_config import validate_form_config
from .tokens_values_config import validate_tokens_values_config

logger = get_logger(name=__name__)


def _extrapolate_tokens_values(text: str, tokens_values: dict) -> str:
    for token, value in tokens_values.items():
        text = text.replace("{{%s}}" % token, value)
    return text


def _set_tokens_in_form_config_item(item: dict, tokens_values: dict):
    for attr_name in ATTRS_SUPPORTING_TOKENS:
        item_attr = item.get(attr_name)
        if not item_attr:
            continue

        item[attr_name] = _extrapolate_tokens_values(item_attr, tokens_values)


def _collect_form_config_items_to_extrapolate(config_json: dict) -> List[dict]:
    items_to_extrapolate = []

    form = config_json["form"]
    items_to_extrapolate.append(form)

    sections = form["sections"]
    for section in sections:
        items_to_extrapolate.append(section)

        fieldsets = section["fieldsets"]
        for fieldset in fieldsets:
            items_to_extrapolate.append(fieldset)

            rows = fieldset["rows"]
            for row in rows:
                items_to_extrapolate.append(row)

                fields = row["fields"]
                for field in fields:
                    items_to_extrapolate.append(field)

    return items_to_extrapolate


def _collect_tokens_from_form_config(config_json: dict) -> set:
    items_to_extrapolate = _collect_form_config_items_to_extrapolate(config_json)
    tokens_in_form_config = set()

    for item in items_to_extrapolate:
        for attr_name in ATTRS_SUPPORTING_TOKENS:
            item_attr = item.get(attr_name)
            if not item_attr:
                continue
            tokens_in_form_config.update(set(re.findall(r"\{\{(.+?)\}\}", item_attr)))

    return tokens_in_form_config


def _extrapolate_tokens_in_form_config(config_json: dict, tokens_values: dict) -> dict:
    items_to_extrapolate = _collect_form_config_items_to_extrapolate(config_json)
    for item in items_to_extrapolate:
        _set_tokens_in_form_config_item(item, tokens_values)
    return config_json


def _combine_extrapolated_form_configs(
    form_config_json: dict, tokens_values_config_json: List[dict],
) -> List[dict]:
    errors = []

    # Validate Form config
    form_config_is_valid, form_config_errors = validate_form_config(form_config_json)

    # Validate token values config
    tokens_values_config_is_valid, tokens_values_data_config_errors = validate_tokens_values_config(
        tokens_values_config_json,
    )

    # Validate tokens in both configs
    tokens_from_form_config = _collect_tokens_from_form_config(form_config_json)
    tokens_from_tokens_values_config = set(sum(
        [list(u["tokens_values"].keys()) for u in tokens_values_config_json],
        [],
    ))

    # Token names present in token values config, but not in form config
    overspecified_tokens = tokens_from_tokens_values_config - tokens_from_form_config
    # Token names present in form config, but not in token values config
    underspecified_tokens = tokens_from_form_config - tokens_from_tokens_values_config

    # Print errors
    if overspecified_tokens:
        errors.append(
            f"Values for the following tokens are provided in tokens value config, "
            f"but they are not defined in the form config: "
            f"{', '.join(overspecified_tokens)}."
        )
    if underspecified_tokens:
        errors.append(
            f"The following tokens are specified in the form config, "
            f"but their values are not provided in the tokens values config: "
            f"{', '.join(underspecified_tokens)}."
        )

    if not form_config_is_valid:
        form_config_errors = [f"  - {e}" for e in form_config_errors]
        errors_string = "\n".join(form_config_errors)
        errors.append(f"Form config is invalid. Errors:\n{errors_string}")

    if not tokens_values_config_is_valid:
        tokens_values_data_config_errors = [f"  - {e}" for e in tokens_values_data_config_errors]
        errors_string = "\n".join(tokens_values_data_config_errors)
        errors.append(f"Units data config is invalid. Errors:\n{errors_string}")

    if errors:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(errors))

    # Combine extrapolated configs
    combined_config = []
    if tokens_values_config_json:
        for unit_tokens_values in tokens_values_config_json:
            if unit_tokens_values == {}:
                combined_config.append(form_config_json)
            else:
                form_config_json_with_tokens = _extrapolate_tokens_in_form_config(
                    deepcopy(form_config_json), unit_tokens_values["tokens_values"],
                )
                combined_config.append(form_config_json_with_tokens)
    else:
        # If no config with tokens values was added than
        # we just create one-unit config and copy form config into it as-is
        combined_config.append(form_config_json)

    return combined_config


def _save_combined_extrapolated_configs(config_json: List[dict], file_path: str):
    config_str = json.dumps(config_json, indent=JSON_IDENTATION)

    with open(file_path, "w") as f:
        f.write(config_str)


def create_extrapolated_config(
    form_config_path: str, tokens_values_config_path: str, combined_config_path: str,
):
    # Check if files exist
    if not os.path.exists(form_config_path):
        raise FileNotFoundError(f"Create file `{form_config_path}` and add form configuration")

    # Read JSON from files
    try:
        with open(form_config_path) as form_config_file:
            form_config_json = json.load(form_config_file)
    except (JSONDecodeError, TypeError):
        logger.error(f"Could not read JSON from `{form_config_path}` file")
        raise

    if os.path.exists(tokens_values_config_path):
        try:
            with open(tokens_values_config_path) as tokens_values_data_config_file:
                tokens_values_json = json.load(tokens_values_data_config_file)
        except (JSONDecodeError, TypeError):
            logger.error(f"Could not read JSON from `{tokens_values_config_path}` file")
    else:
        tokens_values_json = []

    # Create combined config
    try:
        extrapolated_form_config_json = _combine_extrapolated_form_configs(
            form_config_json, tokens_values_json,
        )
        _save_combined_extrapolated_configs(extrapolated_form_config_json, combined_config_path)
    except ValueError as e:
        logger.error(e)
