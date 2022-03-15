#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.static_html_task.static_html_blueprint import (
    BLUEPRINT_TYPE_STATIC_HTML,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)

from omegaconf import DictConfig
from dataclasses import dataclass

CORRECT_ANSWER = "apple"


@dataclass
class OnboardingConfig(build_default_task_config("onboarding_example")):  # type: ignore
    correct_answer: str = CORRECT_ANSWER


@task_script(config=OnboardingConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
    correct_config_answer = cfg.correct_answer

    def onboarding_is_valid(onboarding_data):
        inputs = onboarding_data["inputs"]
        outputs = onboarding_data["outputs"]
        return outputs.get("answer") == correct_config_answer

    shared_state = SharedStaticTaskState(
        onboarding_data={"correct_answer": correct_config_answer},
        validate_onboarding=onboarding_is_valid,
    )

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
