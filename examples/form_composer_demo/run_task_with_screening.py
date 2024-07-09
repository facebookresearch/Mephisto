#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from json import JSONDecodeError

from omegaconf import DictConfig

from examples.form_composer_demo.data.simple.screening_units.screening_units_validation import (
    validate_screening_unit,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import ScreenTaskRequired
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import build_custom_bundle
from mephisto.tools.scripts import task_script


def _build_custom_bundles(cfg: DictConfig) -> None:
    """Locally build bundles that are not available on npm repository"""
    mephisto_packages_dir = os.path.join(
        # Root project directory
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "packages",
    )

    # Build `mephisto-task-multipart` React package
    build_custom_bundle(
        mephisto_packages_dir,
        force_rebuild=cfg.mephisto.task.force_rebuild,
        webapp_name="mephisto-task-multipart",
        build_command="build",
    )

    # Build `react-form-composer` React package
    build_custom_bundle(
        mephisto_packages_dir,
        force_rebuild=cfg.mephisto.task.force_rebuild,
        webapp_name="react-form-composer",
        build_command="build",
    )

    # Build Review UI for the application
    build_custom_bundle(
        cfg.task_dir,
        force_rebuild=cfg.mephisto.task.force_rebuild,
        webapp_name="webapp",
        build_command="build:simple:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        cfg.task_dir,
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
        build_command="dev:simple",
    )


def screening_unit_factory() -> dict:
    while True:
        screening_data_path = os.path.join(
            # Root project directory
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            "simple",
            "screening_units",
            "screening_units_data.json",
        )

        try:
            with open(screening_data_path) as config_file:
                screening_data = json.load(config_file)[0]
        except (JSONDecodeError, TypeError) as e:
            print(
                f"[red]"
                f"Could not read Screening Unit data from file: '{screening_data_path}': {e}."
                f"[/red]"
            )
            exit()

        yield screening_data


@task_script(default_config_file="example_local_mock_with_screening")
def main(operator: Operator, cfg: DictConfig) -> None:
    # 1. Build packages
    _build_custom_bundles(cfg)

    # 2. Prepare ShareState with Screeining
    shared_state = SharedStaticTaskState()

    shared_state.on_unit_submitted = ScreenTaskRequired.create_validation_function(
        cfg.mephisto,
        validate_screening_unit,
    )
    shared_state.screening_data_factory = screening_unit_factory()
    shared_state.qualifications += ScreenTaskRequired.get_mixin_qualifications(
        cfg.mephisto,
        shared_state,
    )

    # 3. Launch TaskRun
    operator.launch_task_run(cfg.mephisto, shared_state=shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
