#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

try:
    import torch
    from PIL import Image
except ImportError:
    print("Need to have torch, PIL installed to use this demo")
    exit(1)

import os
from io import BytesIO
import base64
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import (
    load_db_and_process_config,
    build_and_return_custom_bundle,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    BLUEPRINT_TYPE_REMOTE_PROCEDURE,
    SharedRemoteProcedureTaskState,
    RemoteProcedureAgentState,
)

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional

from model import mnist

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_SOURCE = os.path.abspath(os.path.join(TASK_DIRECTORY, "source_files"))

default_list = ["_self_", {"conf": "launch_with_local"}]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: default_list)
    task_dir: str = TASK_DIRECTORY


register_script_config(name="scriptconfig", module=TestScriptConfig)


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


@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    db, cfg = load_db_and_process_config(cfg)
    num_tasks = 2

    def onboarding_always_valid(onboarding_data):
        # NOTE you can make an onboarding task and validate it here
        print(onboarding_data)
        return True

    # Right now we're building locally, but should eventually
    # use non-local for the real thing
    tasks: List[Dict[str, Any]] = [{}] * num_tasks
    mnist_model = mnist(pretrained=True)
    context = build_local_context(num_tasks)

    def handle_with_model(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ) -> Dict[str, Any]:
        """Convert the image to be read by MNIST classifier, then classify"""
        img_dat = args["urlData"].split("data:image/png;base64,")[1]
        im = Image.open(BytesIO(base64.b64decode(img_dat)))
        im_gray = im.convert("L")
        im_resized = im_gray.resize((28, 28))
        im_vals = list(im_resized.getdata())
        norm_vals = [(255 - x) * 1.0 / 255.0 for x in im_vals]
        in_tensor = torch.tensor([norm_vals])
        output = mnist_model(in_tensor)
        pred = output.data.max(1)[1]
        print("Predicted digit:", pred.item())
        return {
            "digit_prediction": pred.item(),
        }

    function_registry = {
        "classify_digit": handle_with_model,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        validate_onboarding=onboarding_always_valid,
        function_registry=function_registry,
    )

    build_and_return_custom_bundle(task_dir)
    operator = Operator(db)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
