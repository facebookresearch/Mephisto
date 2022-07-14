#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

try:
    from detoxify import Detoxify
except ImportError:
    print("Need to have detoxify to use this demo. For example: pip install detoxify")
    exit(1)

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import (
    build_custom_bundle,
    task_script,
)

from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
    RemoteProcedureAgentState,
)
from omegaconf import DictConfig
from typing import Any, Dict


def build_tasks(num_tasks):
    """
    Create a set of tasks you want annotated
    """
    # NOTE These form the init_data for a task
    tasks = []
    for x in range(num_tasks):
        tasks.append(
            {
                "index": x,
                "local_value_key": x,
            }
        )
    return tasks


def determine_toxicity(text: str):
    return Detoxify("original").predict(text)["toxicity"]


@task_script(default_config_file="launch_with_local")
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks = build_tasks(cfg.num_tasks)

    def calculate_toxicity(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ) -> Dict[str, Any]:
        return {
            "toxicity": str(determine_toxicity(args["text"])),
        }

    function_registry = {
        "determine_toxicity": calculate_toxicity,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
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
