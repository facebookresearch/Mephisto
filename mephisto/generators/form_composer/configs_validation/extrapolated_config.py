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
from typing import Tuple
from urllib.parse import urljoin
from urllib.parse import urlparse

import boto3

from mephisto.generators.form_composer.constants import JSON_IDENTATION
from .config_validation_constants import ATTRS_SUPPORTING_TOKENS
from .form_config import validate_form_config
from .tokens_values_config import validate_tokens_values_config

FILE_LOCATION_TOKEN_NAME = "file_location"


def _extrapolate_tokens_values(text: str, tokens_values: dict) -> str:
    for token, value in tokens_values.items():
        text = re.sub(r"\{\{(\s*)" + token + r"(\s*)\}\}", value, text)
    return text


def _set_tokens_in_form_config_item(item: dict, tokens_values: dict):
    for attr_name in ATTRS_SUPPORTING_TOKENS:
        item_attr = item.get(attr_name)
        if not item_attr:
            continue

        item[attr_name] = _extrapolate_tokens_values(item_attr, tokens_values)


def _collect_form_config_items_to_extrapolate(config_data: dict) -> List[dict]:
    items_to_extrapolate = []

    form = config_data["form"]
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


def _collect_tokens_from_form_config(config_data: dict) -> set:
    items_to_extrapolate = _collect_form_config_items_to_extrapolate(config_data)
    tokens_in_form_config = set()

    for item in items_to_extrapolate:
        for attr_name in ATTRS_SUPPORTING_TOKENS:
            item_attr = item.get(attr_name)
            if not item_attr:
                continue
            tokens_in_form_config.update(set(re.findall(r"\{\{\s*(\w+?)\s*\}\}", item_attr)))

    return tokens_in_form_config


def _extrapolate_tokens_in_form_config(config_data: dict, tokens_values: dict) -> dict:
    items_to_extrapolate = _collect_form_config_items_to_extrapolate(config_data)
    for item in items_to_extrapolate:
        _set_tokens_in_form_config_item(item, tokens_values)
    return config_data


def _combine_extrapolated_form_configs(
    form_config_data: dict,
    tokens_values_config_data: List[dict],
    skip_validating_tokens_values_config: bool,
) -> List[dict]:
    errors = []

    # Validate Form config
    form_config_is_valid, form_config_errors = validate_form_config(form_config_data)

    # Validate token values config
    if skip_validating_tokens_values_config:
        tokens_values_config_is_valid, tokens_values_data_config_errors = True, []
    else:
        tokens_values_config_is_valid, tokens_values_data_config_errors = (
            validate_tokens_values_config(tokens_values_config_data)
        )

    # Validate tokens in both configs
    tokens_from_form_config = _collect_tokens_from_form_config(form_config_data)
    tokens_from_tokens_values_config = set(sum(
        [list(u["tokens_values"].keys()) for u in tokens_values_config_data],
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
    if tokens_values_config_data:
        for unit_tokens_values in tokens_values_config_data:
            if unit_tokens_values == {}:
                combined_config.append(form_config_data)
            else:
                form_config_data_with_tokens = _extrapolate_tokens_in_form_config(
                    deepcopy(form_config_data), unit_tokens_values["tokens_values"],
                )
                combined_config.append(form_config_data_with_tokens)
    else:
        # If no config with tokens values was added than
        # we just create one-unit config and copy form config into it as-is
        combined_config.append(form_config_data)

    return combined_config


def _write_config_to_file(config_data: List[dict], file_path: str):
    config_str = json.dumps(config_data, indent=JSON_IDENTATION)

    with open(file_path, "w") as f:
        f.write(config_str)


def create_extrapolated_config(
    form_config_path: str,
    tokens_values_config_path: str,
    extrapolated_form_config_path: str,
    skip_validating_tokens_values_config: bool = False,
):
    # Check if files exist
    if not os.path.exists(form_config_path):
        raise FileNotFoundError(f"Create file '{form_config_path}' and add form configuration")

    # Read JSON from files
    try:
        with open(form_config_path) as form_config_file:
            form_config_data = json.load(form_config_file)
    except (JSONDecodeError, TypeError):
        print(f"Could not read JSON from '{form_config_path}' file")
        raise

    if os.path.exists(tokens_values_config_path):
        try:
            with open(tokens_values_config_path) as tokens_values_data_config_file:
                tokens_values_data = json.load(tokens_values_data_config_file)
        except (JSONDecodeError, TypeError):
            print(f"Could not read JSON from '{tokens_values_config_path}' file")
    else:
        tokens_values_data = []

    # Create combined config
    try:
        extrapolated_form_config_data = _combine_extrapolated_form_configs(
            form_config_data,
            tokens_values_data,
            skip_validating_tokens_values_config,
        )
        _write_config_to_file(extrapolated_form_config_data, extrapolated_form_config_path)
    except ValueError as e:
        print(f"Could not extrapolate form configs: {e}")


def _get_bucket_and_key_from_S3_url(s3_url: str) -> Tuple[str, str]:
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.hostname.split('.')[0]
    relative_path = parsed_url.path

    if not relative_path:
        raise ValueError(f'Cannot extract S3 key from invalid URL "{s3_url}"')

    # Remove a slash from the beginning of the path
    s3_key = relative_path[1:]
    return bucket_name, s3_key


def is_s3_url(value: str) -> bool:
    if isinstance(value, str):
        parsed_url = urlparse(value)
        return bool(
            parsed_url.scheme == 'https' and
            "s3" in parsed_url.hostname and
            parsed_url.netloc and
            parsed_url.path
        )

    return False


def get_file_urls_from_s3_storage(s3_url: str) -> List[str]:
    urls = []

    base_url = "{0.scheme}://{0.netloc}/".format(urlparse(s3_url))
    bucket, s3_path = _get_bucket_and_key_from_S3_url(s3_url)

    s3 = boto3.resource("s3")
    my_bucket = s3.Bucket(bucket)

    for object_summary in my_bucket.objects.filter(Prefix=s3_path):
        file_s3_key: str = object_summary.key
        filename = os.path.basename(file_s3_key)
        is_file = bool(filename)
        if is_file:
            urls.append(urljoin(base_url, file_s3_key))

    return urls


def generate_tokens_values_config_from_files(tokens_values_config_path: str, files: List[str]):
    tokens_values_config_data = []

    for i, file_location in enumerate(files):
        tokens_values_config_data.append(dict(
            tokens_values={
                FILE_LOCATION_TOKEN_NAME: file_location,
            },
        ))

    try:
        _write_config_to_file(tokens_values_config_data, tokens_values_config_path)
    except ValueError as e:
        print(f"Could not generate tokens values config: {e}")
