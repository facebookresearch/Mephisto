#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir
from mephisto.server.blueprints.static_task.static_html_blueprint import BLUEPRINT_TYPE
from mephisto.utils.scripts import get_db_from_config, augment_config_from_db

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any


TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/simple_static_task")

defaults = [
    {"mephisto.blueprint": BLUEPRINT_TYPE},
    {"mephisto.architect": 'local'},
    {"mephisto.provider": 'mock'},
    {"conf": "example"},
]

from mephisto.core.hydra_config import ScriptConfig, register_script_config

@dataclass 
class TestScriptConfig(ScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY

register_script_config(name='scriptconfig', module=TestScriptConfig)

@hydra.main(config_name='scriptconfig')
def main(cfg: DictConfig) -> None:
    db = get_db_from_config(cfg)
    cfg = augment_config_from_db(db, cfg)
    operator = Operator(db)

    operator.validate_and_run_config_wrap(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)

if __name__ == "__main__":
    main()
