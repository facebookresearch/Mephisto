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
import base64
from io import BytesIO
from model import mnist

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


@task_script(default_config_file="launch_with_local")
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks: List[Dict[str, Any]] = [{}] * cfg.num_tasks
    mnist_model = mnist(pretrained=True)

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
        function_registry=function_registry,
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
