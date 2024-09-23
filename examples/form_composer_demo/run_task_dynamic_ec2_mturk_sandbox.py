#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import re
from json import JSONDecodeError

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__UNIT_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.generators.generators_utils.constants import TOKEN_END_REGEX
from mephisto.generators.generators_utils.constants import TOKEN_START_REGEX
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _generate_data_json_config():
    """
    Generate extrapolated `task_data.json` config file,
    based on existing form and tokens values config files
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(app_path, "data", "dynamic")

    unit_config_path = os.path.join(data_path, FORM_COMPOSER__UNIT_CONFIG_NAME)
    token_sets_values_config_path = os.path.join(
        data_path,
        FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
    )
    task_data_config_path = os.path.join(data_path, FORM_COMPOSER__DATA_CONFIG_NAME)

    set_form_composer_env_vars()

    create_extrapolated_config(
        unit_config_path=unit_config_path,
        token_sets_values_config_path=token_sets_values_config_path,
        task_data_config_path=task_data_config_path,
        data_path=data_path,
    )


def _generate_preview_html():
    """
    Generate HTML preview of a Task (based on first form version contained in `task_data.json`)
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    preview_path = os.path.join(app_path, "preview")
    data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME, "dynamic")

    data_config_path = os.path.join(data_path, FORM_COMPOSER__DATA_CONFIG_NAME)
    preview_template_path = os.path.join(preview_path, "mturk_preview_template.html")
    preview_html_path = os.path.join(preview_path, "mturk_preview.html")

    try:
        with open(data_config_path) as data_config_file:
            data_config_data = json.load(data_config_file)
    except (JSONDecodeError, TypeError) as e:
        print(f"Could not read JSON from '{data_config_path}' file: {e}")
        raise

    first_form_version = data_config_data[0]["form"]

    # Erase all tokens from the text since HTML preview is inherently static
    erase_tokens = lambda text: re.sub(
        TOKEN_START_REGEX + r"(.*?)" + TOKEN_END_REGEX,
        "...",
        text,
    )
    preview_data = {
        "title": erase_tokens(first_form_version["title"]),
        "instruction": erase_tokens(first_form_version["instruction"]),
    }

    with open(preview_template_path, "r") as f:
        preview_template = str(f.read())

    with open(preview_html_path, "w") as f:
        for attr_name, value in preview_data.items():
            # Simply replace `[[ token_name ]]` substrings in the HTML template for our valoues
            preview_template = re.sub(
                r"\[\[(\s*)" + attr_name + r"(\s*)\]\]",
                value,
                preview_template,
            )

        f.write(preview_template)


@task_script(default_config_file="dynamic_example_ec2_mturk_sandbox")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_form_composer_dynamic_ec2_mturk_sandbox(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    shared_state = SharedStaticTaskState()

    # Mephisto qualifications
    shared_state.qualifications = [
        # Custom Mephisto qualifications
    ]

    # Mturk qualifications
    shared_state.mturk_specific_qualifications = [
        # MTurk-specific quality control qualifications
    ]

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    _generate_data_json_config()
    _generate_preview_html()
    main()
