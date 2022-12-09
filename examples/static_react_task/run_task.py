#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.data_model.unit import Unit
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script, build_custom_bundle
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from rich import print
from omegaconf import DictConfig


def my_screening_unit_generator():
    while True:
        yield {"text": "SCREENING UNIT: Press the red button", "is_screen": True}


def validate_screening_unit(unit: Unit):
    agent = unit.get_assigned_agent()
    if agent is not None:
        data = agent.state.get_data()
        print(data)
        if (
            data["outputs"] is not None
            and "rating" in data["outputs"]
            and data["outputs"]["rating"] == "bad"
        ):
            # User pressed the red button
            return True
    return False


def handle_onboarding(onboarding_data):
    if onboarding_data["outputs"]["success"] == True:
        return True
    return False


@task_script(default_config_file="example.yaml")
def main(operator: Operator, cfg: DictConfig) -> None:
    is_using_screening_units = cfg.mephisto.blueprint["use_screening_task"]
    shared_state = SharedStaticTaskState(
        static_task_data=[
            {"text": "This text is good text!"},
            {"text": "This text is bad text!"},
        ],
        validate_onboarding=handle_onboarding,
    )

    if is_using_screening_units:
        """
        When using screening units there has to be a
        few more properties set on shared_state
        """
        shared_state.on_unit_submitted = ScreenTaskRequired.create_validation_function(
            cfg.mephisto,
            validate_screening_unit,
        )
        shared_state.screening_data_factory = my_screening_unit_generator()
        shared_state.qualifications += ScreenTaskRequired.get_mixin_qualifications(
            cfg.mephisto, shared_state
        )

    task_dir = cfg.task_dir

    build_custom_bundle(
        task_dir,
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
