#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

try:
    import torch
    from PIL import Image
except ImportError:
    print(
        "Need to have torch, PIL, numpy installed to use this demo. "
        "For example: pip install torch pillow numpy"
    )
    exit(1)

import base64
from io import BytesIO
from typing import Any
from typing import Dict
from typing import List

from omegaconf import DictConfig

from examples.remote_procedure.mnist.model import mnist
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    RemoteProcedureAgentState,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
)
from mephisto.data_model.unit import Unit
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script
from mephisto.utils.console_writer import ConsoleWriter

logger = ConsoleWriter()


def _my_screening_unit_generator() -> dict:
    """
    The frontend react webapp reads in
    isScreeningUnit using the initialTaskData
    prop
    """
    while True:
        yield {
            "isScreeningUnit": True,
        }


def _validate_screening_unit(unit: Unit) -> bool:
    """Checking if the drawn number is 3"""
    agent = unit.get_assigned_agent()
    if agent is not None:
        data = agent.state.get_data()
        annotation = data["outputs"]["final_submission"]["annotations"][0]
        if annotation["isCorrect"] and annotation["currentAnnotation"] == 3:
            return True

    return False


def _handle_with_model(
    _request_id: str,
    args: Dict[str, Any],
    agent_state: RemoteProcedureAgentState,
) -> Dict[str, Any]:
    """Convert the image to be read by MNIST classifier, then classify"""

    img_dat = args["urlData"].split("data:image/png;base64,")[1]
    im = Image.open(BytesIO(base64.b64decode(img_dat)))
    im_gray = im.convert("L")
    im_resized = im_gray.resize((28, 28))
    im_vals = list(im_resized.getdata())
    norm_vals = [(255 - x) * 1.0 / 255.0 for x in im_vals]
    in_tensor = torch.tensor([norm_vals])

    mnist_model = mnist(pretrained=True)
    output = mnist_model(in_tensor)

    pred = output.data.max(1)[1]

    logger.debug(f"Predicted digit: {pred.item()}")

    return {
        "digit_prediction": pred.item(),
    }


@task_script(default_config_file="example_local_mock")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_remote_procedure_mnist(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    tasks: List[Dict[str, Any]] = [{"isScreeningUnit": False}] * cfg.num_tasks
    is_using_screening_units = cfg.mephisto.blueprint["use_screening_task"]

    function_registry = {
        "classify_digit": _handle_with_model,
    }
    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
    )

    if is_using_screening_units:
        # You have to define a few more properties to enable screening units
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
