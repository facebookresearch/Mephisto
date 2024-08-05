#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

try:
    from detoxify import Detoxify
except ImportError:
    print("Need to have detoxify to use this demo. For example: pip install detoxify")
    exit(1)

from typing import Any
from typing import Dict
from typing import List

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    RemoteProcedureAgentState,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
)
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _build_tasks(num_tasks: int) -> List[dict]:
    """Create a set of tasks you want annotated"""
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


def _determine_toxicity(text: str) -> str:
    return Detoxify("original").predict(text)["toxicity"]


def _calculate_toxicity(
    _request_id: str,
    args: Dict[str, Any],
    agent_state: RemoteProcedureAgentState,
) -> Dict[str, Any]:
    return {
        "toxicity": str(_determine_toxicity(args["text"])),
    }


@task_script(default_config_file="example_local_mock")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_remote_procedure_toxicity_detection(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    tasks = _build_tasks(cfg.num_tasks)

    function_registry = {
        "determine_toxicity": _calculate_toxicity,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
    )

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
