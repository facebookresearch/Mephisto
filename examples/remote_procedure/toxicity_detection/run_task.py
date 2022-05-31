#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

try:
    import torch
    from PIL import Image
    from detoxify import Detoxify
except ImportError:
    print(
        "Need to have torch, PIL, numpy installed, detoxify to use this demo. For example: pip install torch pillow numpy detoxify"
    )
    exit(1)

import os
import base64
from io import BytesIO
import sys

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
from typing import List, Any, Dict


def determine_toxicity(text):
    return Detoxify("original").predict(text)["toxicity"]


@task_script(default_config_file="launch_with_local")
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks: List[Dict[str, Any]] = [{}] * cfg.num_tasks

    # function_registry = {
    #     "classify_digit": handle_with_model,
    # }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        # function_registry=function_registry,
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(determine_toxicity(sys.argv[1]))
