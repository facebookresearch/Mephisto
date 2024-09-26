#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
)
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__UNIT_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.generators.generators_utils.config_validation.utils import read_config_file
from mephisto.generators.generators_utils.remote_procedures import JS_NAME_FUNCTION_MAPPING
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _generate_data_json_config():
    """
    Generate extrapolated `task_data.json` config file,
    based on existing form and tokens values config files
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME, "dynamic_presigned_urls")

    unit_config_path = os.path.join(
        data_path,
        FORM_COMPOSER__UNIT_CONFIG_NAME,
    )
    token_sets_values_config_path = os.path.join(
        data_path,
        FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
    )
    task_data_config_path = os.path.join(
        data_path,
        FORM_COMPOSER__DATA_CONFIG_NAME,
    )

    set_form_composer_env_vars()

    create_extrapolated_config(
        unit_config_path=unit_config_path,
        token_sets_values_config_path=token_sets_values_config_path,
        task_data_config_path=task_data_config_path,
        data_path=data_path,
    )


@task_script(default_config_file="dynamic_presigned_urls_example_ec2_prolific")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_form_composer_dynamic_presigned_urls_ec2_prolific(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    # Configure shared state
    task_data_config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "dynamic_presigned_urls",
        "task_data.json",
    )
    task_data = read_config_file(task_data_config_path)
    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=task_data,
        function_registry=JS_NAME_FUNCTION_MAPPING,
    )

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    _generate_data_json_config()
    main()
