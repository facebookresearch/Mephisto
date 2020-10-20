#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.core.hydra_config import RunScriptConfig, register_script_config
import os
from mephisto.core.operator import Operator
from mephisto.utils.scripts import load_db_and_process_config
from mephisto.server.blueprints.parlai_chat.parlai_chat_blueprint import (
    BLUEPRINT_TYPE,
    SharedParlAITaskState,
)
import importlib

import hydra
from omegaconf import DictConfig, MISSING
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    "conf/base",
    {"conf": "custom_prebuilt"},
    {"conf": "dataloader_squad"},
]


@dataclass
class DataLoaderConfig:
    module_name: str = field(
        default="parlai.tasks.squad.agents",
        metadata={"help": ""}
    )
    class_name: str = field(
        default="DefaultTeacher",
        metadata={"help": ""}
    )
    datatype: str = field(
        default="train",
        metadata={"help": ""}
    )
    datapath: str = field(
        default="${task_dir}/data",
        metadata={"help": ""}
    )
    datafile: str = field(
        default=MISSING,
        metadata={"help": ""}
    )
    task: str = field(
        default="${mephisto.task.task_name}",
        metadata={"help": ""}
    )


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    num_turns: int = field(
        default=3,
        metadata={"help": "Number of turns before a conversation is complete"},
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            "help": "Maximum response time before kicking "
            "a worker out, default 300 seconds"
        },
    )
    dataloader: DataLoaderConfig = DataLoaderConfig()


register_script_config(name="scriptconfig", module=TestScriptConfig)


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    db, cfg = load_db_and_process_config(cfg)

    my_module = importlib.import_module(cfg.dataloader.module_name)
    task_class = getattr(my_module, cfg.dataloader.class_name)
    task_opt = cfg.dataloader
    dataloader = task_class(task_opt)

    world_opt = {"num_turns": cfg.num_turns,
                 "turn_timeout": cfg.turn_timeout, "dataloader": dataloader}

    custom_bundle_path = cfg.mephisto.blueprint.get(
        "custom_source_bundle", None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
        )
        world_opt["send_task_data"] = True

    shared_state = SharedParlAITaskState(
        world_opt=world_opt, onboarding_world_opt=world_opt
    )

    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
