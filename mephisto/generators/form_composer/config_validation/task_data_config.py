#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.generators.generators_utils.config_validation.task_data_config import (
    verify_generator_configs,
)


def verify_form_composer_configs(
    task_data_config_path: str,
    unit_config_path: Optional[str] = None,
    token_sets_values_config_path: Optional[str] = None,
    separate_token_values_config_path: Optional[str] = None,
    task_data_config_only: bool = False,
    data_path: Optional[str] = None,
    force_exit: bool = False,
):
    verify_generator_configs(
        task_data_config_path=task_data_config_path,
        unit_config_path=unit_config_path,
        token_sets_values_config_path=token_sets_values_config_path,
        separate_token_values_config_path=separate_token_values_config_path,
        task_data_config_only=task_data_config_only,
        data_path=data_path,
        force_exit=force_exit,
        error_message="\n[red]Provided Form Composer config files are invalid:[/red] {exc}\n",
    )


def collect_unit_config_items_to_extrapolate(config_data: dict) -> List[dict]:
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
