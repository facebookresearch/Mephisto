#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _handle_onboarding(onboarding_data: dict) -> bool:
    if onboarding_data["outputs"]["success"] is True:
        return True

    return False


@task_script(default_config_file="example_local_mock_with_oboarding")
def main(operator: Operator, cfg: DictConfig) -> None:
    # 1. Build packages
    examples.build_form_composer_simple_with_onboarding(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    # 2. Prepare ShareState with Onboarding
    shared_state = SharedStaticTaskState(
        validate_onboarding=_handle_onboarding,
    )

    # 3. Launch TaskRun
    operator.launch_task_run(cfg.mephisto, shared_state=shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
