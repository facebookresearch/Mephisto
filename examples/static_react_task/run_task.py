#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from omegaconf import DictConfig
from rich import print

from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.data_model.unit import Unit
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _my_screening_unit_generator() -> dict:
    while True:
        yield {
            "text": "SCREENING UNIT: Press the red button",
            "is_screen": True,
        }


def _validate_screening_unit(unit: Unit) -> bool:
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


def _handle_onboarding(onboarding_data: dict) -> bool:
    if onboarding_data["outputs"]["success"] is True:
        return True

    return False


@task_script(default_config_file="example_local_mock.yaml")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_static_react_task(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    is_using_screening_units = cfg.mephisto.blueprint["use_screening_task"]
    shared_state = SharedStaticTaskState(
        static_task_data=[
            {"text": "This text is good text!"},
            {"text": "This text is bad text!"},
        ],
        validate_onboarding=_handle_onboarding,
    )

    if is_using_screening_units:
        # When using screening units there has to be a
        # few more properties set on shared_state
        shared_state.on_unit_submitted = ScreenTaskRequired.create_validation_function(
            cfg.mephisto,
            _validate_screening_unit,
        )
        shared_state.screening_data_factory = _my_screening_unit_generator()
        shared_state.qualifications += ScreenTaskRequired.get_mixin_qualifications(
            cfg.mephisto, shared_state
        )

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
