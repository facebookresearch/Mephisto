#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import (
    task_script,
    build_custom_bundle,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    BLUEPRINT_TYPE_REMOTE_PROCEDURE,
    SharedRemoteProcedureTaskState,
    RemoteProcedureAgentState,
)

from omegaconf import DictConfig
from typing import Any, Dict


def build_local_context(num_tasks):
    """
    Create local context that you don't intend to be shared with the frontend,
    but which you may want your remote functions to use
    """
    # NOTE this can be used to establish any kind of shared local context you
    # might need access to
    context = {}
    for x in range(num_tasks):
        context[x] = f"Hello {x}, this task was for you."
    return context


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


@task_script(default_config_file="launch_with_local")
def main(operator: Operator, cfg: DictConfig) -> None:
    def onboarding_always_valid(onboarding_data):
        # NOTE you can make an onboarding task and validate it here
        print(onboarding_data)
        return True

    # Right now we're building locally, but should eventually
    # use non-local for the real thing
    tasks = build_tasks(cfg.num_tasks)
    context = build_local_context(cfg.num_tasks)

    def handle_with_model(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ) -> Dict[str, Any]:
        """Remote call to process external content using a 'model'"""
        # NOTE this body can be whatever you want
        print(f"The parsed args are {args}, you can do what you want with that")
        print(f"You can also use {agent_state.init_data}, to get task keys")
        assert agent_state.init_data is not None
        idx = agent_state.init_data["local_value_key"]
        print(f"And that may let you get local context, like {context[idx]}")
        return {
            "secret_local_value": context[idx],
            "update": f"this was request {args['arg3'] + 1}",
        }

    function_registry = {
        "handle_with_model": handle_with_model,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        validate_onboarding=onboarding_always_valid,
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
