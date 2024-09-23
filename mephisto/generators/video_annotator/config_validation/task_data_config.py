#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.generators.generators_utils.config_validation.task_data_config import (
    verify_generator_configs,
)


def verify_video_annotator_configs(
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
        error_message="\n[red]Provided Video Annotator config files are invalid:[/red] {exc}\n",
    )


def collect_unit_config_items_to_extrapolate(config_data: dict) -> List[dict]:
    items_to_extrapolate = []

    if not isinstance(config_data, dict):
        return items_to_extrapolate

    annotator = config_data["annotator"]
    items_to_extrapolate.append(annotator)

    submit_button = annotator["submit_button"]
    items_to_extrapolate.append(submit_button)

    segment_fields = annotator.get("segment_fields")
    if segment_fields:
        for field in segment_fields:
            items_to_extrapolate.append(field)

    return items_to_extrapolate
