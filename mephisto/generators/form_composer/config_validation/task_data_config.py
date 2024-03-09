#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os.path
import re
from copy import deepcopy
from typing import List
from typing import Optional
from typing import Tuple

from rich import print

from mephisto.generators.form_composer.constants import S3_URL_EXPIRATION_MINUTES_MAX
from mephisto.generators.form_composer.constants import TOKEN_END_REGEX
from mephisto.generators.form_composer.constants import TOKEN_START_REGEX
from mephisto.generators.form_composer.remote_procedures import ProcedureName
from .config_validation_constants import ATTRS_SUPPORTING_TOKENS
from .config_validation_constants import TOKENS_VALUES_KEY
from .form_config import validate_form_config
from .separate_token_values_config import validate_separate_token_values_config
from .token_sets_values_config import validate_token_sets_values_config
from .utils import get_s3_presigned_url
from .utils import make_error_message
from .utils import read_config_file
from .utils import write_config_to_file

FILE_LOCATION_TOKEN_NAME = "file_location"


def _extrapolate_tokens_values(text: str, tokens_values: dict) -> str:
    for token, value in tokens_values.items():
        text = re.sub(
            (
                TOKEN_START_REGEX
                + r"(\s*)"
                +
                # Escape and add parentheses around the token, in case it has special characters
                r"("
                + re.escape(token)
                + r")"
                + "(\s*)"
                + TOKEN_END_REGEX
            ),
            str(value),
            text,
        )
    return text


def _set_tokens_in_form_config_item(item: dict, tokens_values: dict):
    for attr_name in ATTRS_SUPPORTING_TOKENS:
        item_attr = item.get(attr_name)
        if not item_attr:
            continue

        item[attr_name] = _extrapolate_tokens_values(item_attr, tokens_values)


def _collect_form_config_items_to_extrapolate(config_data: dict) -> List[dict]:
    items_to_extrapolate = []

    if not isinstance(config_data, dict):
        return items_to_extrapolate

    form = config_data["form"]
    items_to_extrapolate.append(form)

    submit_button = form["submit_button"]
    items_to_extrapolate.append(submit_button)

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


def _collect_tokens_from_form_config(
    config_data: dict,
    regex: Optional[str] = None,
) -> Tuple[set, List[str]]:
    regex = regex or r"\s*(\w+?)\s*"

    items_to_extrapolate = _collect_form_config_items_to_extrapolate(config_data)
    tokens_in_form_config = set()
    tokens_in_unexpected_attrs_errors = []

    for item in items_to_extrapolate:
        for attr_name in ATTRS_SUPPORTING_TOKENS:
            item_attr = item.get(attr_name)
            if not item_attr:
                continue
            tokens_in_form_config.update(
                set(
                    re.findall(
                        TOKEN_START_REGEX + regex + TOKEN_END_REGEX,
                        item_attr,
                    )
                )
            )

        attrs_not_suppoting_tokens = set(item.keys()) - set(ATTRS_SUPPORTING_TOKENS)
        for attr_name in attrs_not_suppoting_tokens:
            item_attr = item.get(attr_name)
            if isinstance(item_attr, str):
                found_attr_tokens = re.findall(
                    TOKEN_START_REGEX + regex + TOKEN_END_REGEX,
                    item_attr,
                )
                if found_attr_tokens:
                    found_attr_tokens_string = ", ".join([f"'{t}'" for t in found_attr_tokens])
                    tokens_in_unexpected_attrs_errors.append(
                        f"You tried to set tokens {found_attr_tokens_string} "
                        f"in attribute '{attr_name}' with value '{item_attr}'. "
                        f"You can use tokens only in following attributes: "
                        f"{', '.join(ATTRS_SUPPORTING_TOKENS)}"
                    )

    return tokens_in_form_config, tokens_in_unexpected_attrs_errors


def _extrapolate_tokens_in_form_config(config_data: dict, tokens_values: dict) -> dict:
    items_to_extrapolate = _collect_form_config_items_to_extrapolate(config_data)
    for item in items_to_extrapolate:
        _set_tokens_in_form_config_item(item, tokens_values)
    return config_data


def _validate_tokens_in_both_configs(
    form_config_data: dict,
    token_sets_values_config_data: List[dict],
) -> Tuple[set, set, list]:
    tokens_from_form_config, tokens_in_unexpected_attrs_errors = _collect_tokens_from_form_config(
        form_config_data
    )
    tokens_from_token_sets_values_config = set(
        [
            token_name
            for token_set_values_data in token_sets_values_config_data
            for token_name in token_set_values_data.get(TOKENS_VALUES_KEY, {}).keys()
        ]
    )
    # Token names present in token values config, but not in form config
    overspecified_tokens = tokens_from_token_sets_values_config - tokens_from_form_config
    # Token names present in form config, but not in token values config
    underspecified_tokens = tokens_from_form_config - tokens_from_token_sets_values_config
    return overspecified_tokens, underspecified_tokens, tokens_in_unexpected_attrs_errors


def _combine_extrapolated_form_configs(
    form_config_data: dict,
    token_sets_values_config_data: List[dict],
) -> List[dict]:
    errors = []

    # Validate Form config
    form_config_is_valid, form_config_errors = validate_form_config(form_config_data)

    if not form_config_is_valid:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(form_config_errors))

    (
        token_sets_values_config_is_valid,
        token_sets_values_data_config_errors,
    ) = validate_token_sets_values_config(token_sets_values_config_data)

    # Validate that same token names are present in both configs
    (
        overspecified_tokens,
        underspecified_tokens,
        tokens_in_unexpected_attrs_errors,
    ) = _validate_tokens_in_both_configs(
        form_config_data,
        token_sets_values_config_data,
    )

    # Output errors, if any
    if overspecified_tokens:
        errors.append(
            f"Values for the following tokens are provided in token sets values config, "
            f"but they are not defined in the form config: "
            f"{', '.join(overspecified_tokens)}."
        )
    if underspecified_tokens:
        errors.append(
            f"The following tokens are specified in the form config, "
            f"but their values are not provided in the token sets values config: "
            f"{', '.join(underspecified_tokens)}."
        )

    if tokens_in_unexpected_attrs_errors:
        errors = errors + tokens_in_unexpected_attrs_errors

    if not form_config_is_valid:
        errors.append(make_error_message("Form config is invalid", form_config_errors))

    if not token_sets_values_config_is_valid:
        errors.append(
            make_error_message(
                "Token sets values config is invalid",
                token_sets_values_data_config_errors,
            )
        )

    if errors:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(errors))

    # If no errors, combine extrapolated form versions to create Task data config
    combined_config = []
    if token_sets_values_config_data:
        for token_sets_values in token_sets_values_config_data:
            if token_sets_values == {}:
                combined_config.append(form_config_data)
            else:
                form_config_data_with_tokens = _extrapolate_tokens_in_form_config(
                    deepcopy(form_config_data),
                    token_sets_values[TOKENS_VALUES_KEY],
                )
                combined_config.append(form_config_data_with_tokens)
    else:
        # If no config with tokens values was added than
        # we just create one-unit config and copy form config into it as-is
        combined_config.append(form_config_data)

    return combined_config


def create_extrapolated_config(
    form_config_path: str,
    token_sets_values_config_path: str,
    task_data_config_path: str,
):
    # Check if files exist
    if not os.path.exists(form_config_path):
        raise FileNotFoundError(f"Create file '{form_config_path}' and add form configuration")

    # Read JSON from files
    form_config_data = read_config_file(form_config_path)

    if os.path.exists(token_sets_values_config_path):
        token_sets_values_data = read_config_file(token_sets_values_config_path)
    else:
        token_sets_values_data = []

    # Create combined config
    try:
        extrapolated_form_config_data = _combine_extrapolated_form_configs(
            form_config_data,
            token_sets_values_data,
        )
        write_config_to_file(extrapolated_form_config_data, task_data_config_path)
    except ValueError as e:
        print(f"\n[red]Could not extrapolate form configs:[/red] {e}\n")
        exit()


def validate_task_data_config(config_data: List[dict]) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_data, list):
        is_valid = False
        errors.append("Config must be a JSON Array.")

    if config_data:
        if not all(config_data):
            is_valid = False
            errors.append("Task data config must contain at least one non-empty item.")

        # Validate each form version contained in task data config
        for item in config_data:
            form_config_is_valid, form_config_errors = validate_form_config(item)
            if not form_config_is_valid:
                is_valid = False
                errors += form_config_errors

    return is_valid, errors


def verify_form_composer_configs(
    task_data_config_path: str,
    form_config_path: Optional[str] = None,
    token_sets_values_config_path: Optional[str] = None,
    separate_token_values_config_path: Optional[str] = None,
    task_data_config_only: bool = False,
):
    errors = []

    try:
        # 1. Validate task data config
        task_data_config_data = read_config_file(task_data_config_path, exit_if_no_file=False)

        if task_data_config_data is None:
            pass
        else:
            task_data_config_is_valid, task_data_config_errors = validate_task_data_config(
                task_data_config_data,
            )
            if not task_data_config_is_valid:
                errors.append(
                    make_error_message(
                        "Task data config is invalid",
                        task_data_config_errors,
                    )
                )

        if task_data_config_only:
            if errors:
                raise ValueError(make_error_message("", errors))

            return None

        # 2. Validate form config
        form_config_data = read_config_file(form_config_path, exit_if_no_file=False)

        if form_config_data is None:
            pass
        else:
            form_config_is_valid, form_config_errors = validate_form_config(form_config_data)

            if not form_config_is_valid:
                errors.append(make_error_message("Form config is invalid", form_config_errors))

        # 3. Validate token sets values config
        token_sets_values_data = read_config_file(
            token_sets_values_config_path,
            exit_if_no_file=False,
        )

        # 3a. Validate token sets values data itself
        if token_sets_values_data is None:
            token_sets_values_data = []
        else:
            (
                token_sets_values_config_is_valid,
                token_sets_values_config_errors,
            ) = validate_token_sets_values_config(token_sets_values_data)

            if not token_sets_values_config_is_valid:
                errors.append(
                    make_error_message(
                        "Token sets values config is invalid",
                        token_sets_values_config_errors,
                        indent=4,
                    )
                )

        # 3b. Ensure there's no unused token names in both token setes and form config
        (
            overspecified_tokens,
            underspecified_tokens,
            tokens_in_unexpected_attrs_errors,
        ) = _validate_tokens_in_both_configs(form_config_data, token_sets_values_data)

        if overspecified_tokens:
            errors.append(
                f"Values for the following tokens are provided in token sets values config, "
                f"but they are not defined in the form config: "
                f"{', '.join(overspecified_tokens)}."
            )
        if underspecified_tokens:
            errors.append(
                f"The following tokens are specified in the form config, "
                f"but their values are not provided in the token sets values config: "
                f"{', '.join(underspecified_tokens)}."
            )

        if tokens_in_unexpected_attrs_errors:
            errors = errors + tokens_in_unexpected_attrs_errors

        # 4. Validate separate token values config
        separate_token_values_config_data = read_config_file(
            separate_token_values_config_path,
            exit_if_no_file=False,
        )

        (
            separate_token_values_config_is_valid,
            separate_token_values_config_errors,
        ) = validate_separate_token_values_config(separate_token_values_config_data)

        if not separate_token_values_config_is_valid:
            errors.append(
                make_error_message(
                    "Separate token values config is invalid",
                    separate_token_values_config_errors,
                )
            )

        if errors:
            raise ValueError(make_error_message("", errors))
        else:
            print(f"[green]All configs are valid.[/green]")

    except ValueError as e:
        print(f"\n[red]Provided Form Composer config files are invalid:[/red] {e}\n")


def prepare_task_config_for_review_app(config_data: dict) -> dict:
    config_data = deepcopy(config_data)

    procedure_code_regex = r"\s*(.+?)\s*"
    tokens_from_inputs, _ = _collect_tokens_from_form_config(
        config_data,
        regex=procedure_code_regex,
    )

    url_from_rpocedure_code_regex = r"\(\"(.+?)\"\)"
    token_values = {}
    for token in tokens_from_inputs:
        presigned_url_procedure_names = [
            ProcedureName.GET_MULTIPLE_PRESIGNED_URLS,
            ProcedureName.GET_PRESIGNED_URL,
        ]
        if any([p in token for p in presigned_url_procedure_names]):
            url = re.findall(url_from_rpocedure_code_regex, token)[0]
            # Presign URL for max possible perioid of time,
            # because there's no need to hide files from researchers
            # and review can last for a long time
            presigned_url = get_s3_presigned_url(url, S3_URL_EXPIRATION_MINUTES_MAX)
            token_values[token] = presigned_url

    prepared_config = _extrapolate_tokens_in_form_config(config_data, token_values)
    return prepared_config
