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

from omegaconf import DictConfig


@task_script(default_config_file="screening_example")
def main(operator: Operator, cfg: DictConfig) -> None:
    def onboarding_always_valid(onboarding_data):
        return True

    def validate_screening_unit(unit: Unit):
        agent = unit.get_assigned_agent()
        print(agent)
        if agent is not None:
            data = agent.state.get_data()
            print(data)
        return True

    shared_state = SharedStaticTaskState(
        static_task_data=[
            {"text": "This text is good text!"},
            {"text": "This text is bad text!"},
        ],
        validate_onboarding=onboarding_always_valid,
        on_unit_submitted=ScreenTaskRequired.create_validation_function(
            cfg.mephisto,
            validate_screening_unit,
        ),
        screening_data_factory=False,
    )

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
