#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
)
from mephisto.generators.generators_utils.config_validation.utils import read_config_file
from mephisto.generators.generators_utils.remote_procedures import JS_NAME_FUNCTION_MAPPING
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import generators
from mephisto.tools.scripts import task_script


@task_script(default_config_file="default")
def main(operator: Operator, cfg: DictConfig) -> None:
    generators.build_video_annotator_generator_with_packages(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    # Configure shared state
    task_data_config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "task_data.json",
    )
    task_data = read_config_file(task_data_config_path)
    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=task_data,
        function_registry=JS_NAME_FUNCTION_MAPPING,
    )

    # Launch Task Run
    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
