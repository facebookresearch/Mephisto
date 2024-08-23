#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from mephisto.generators.form_composer.config_validation.task_data_config import (
    verify_form_composer_configs,
)


def verify_video_annotator_configs(
    task_data_config_path: str,
    form_config_path: Optional[str] = None,
    token_sets_values_config_path: Optional[str] = None,
    separate_token_values_config_path: Optional[str] = None,
    task_data_config_only: bool = False,
    data_path: Optional[str] = None,
    force_exit: bool = False,
):
    verify_form_composer_configs(
        task_data_config_path=task_data_config_path,
        form_config_path=form_config_path,
        token_sets_values_config_path=token_sets_values_config_path,
        separate_token_values_config_path=separate_token_values_config_path,
        task_data_config_only=task_data_config_only,
        data_path=data_path,
        force_exit=force_exit,
    )
