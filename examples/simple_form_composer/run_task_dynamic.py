#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from omegaconf import DictConfig

from mephisto.generators.form_composer.configs_validation.extrapolated_config import (
    create_extrapolated_config
)
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import build_custom_bundle
from mephisto.tools.scripts import task_script


@task_script(default_config_file="dynamic_example_local_mock")
def main(operator: Operator, cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    build_custom_bundle(
        task_dir,
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    operator.launch_task_run(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


def create_data_config():
    app_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(app_path, "data")

    extrapolated_form_config_path = os.path.join(data_path, "dynamic", "data.json")
    form_config_path = os.path.join(data_path, "dynamic", "form_config.json")
    tokens_values_config_path = os.path.join(data_path, "dynamic", "tokens_values_config.json")

    create_extrapolated_config(
        form_config_path=form_config_path,
        tokens_values_config_path=tokens_values_config_path,
        combined_config_path=extrapolated_form_config_path,
    )


if __name__ == "__main__":
    create_data_config()
    main()
