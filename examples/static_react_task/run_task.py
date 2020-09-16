#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import subprocess
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir
from mephisto.utils.scripts import load_db_and_validate_config
from mephisto.server.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE,
)
from mephisto.server.blueprints.abstract.static_task.static_blueprint import SharedStaticTaskState

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

defaults = [
    {"mephisto.blueprint": BLUEPRINT_TYPE},
    {"mephisto.architect": 'local'},
    {"mephisto.provider": 'mock'},
    {"conf": "example"},
]

from mephisto.core.hydra_config import RunScriptConfig, register_script_config

@dataclass 
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY

register_script_config(name='scriptconfig', module=TestScriptConfig)


# TODO it would be nice if this was automated in the way that it
# is for ParlAI custom frontend tasks
def build_task(task_dir):
    """Rebuild the frontend for this task"""

    frontend_source_dir = os.path.join(task_dir, "webapp")
    frontend_build_dir = os.path.join(frontend_source_dir, "build")

    return_dir = os.getcwd()
    os.chdir(frontend_source_dir)
    if os.path.exists(frontend_build_dir):
        shutil.rmtree(frontend_build_dir)
    packages_installed = subprocess.call(["npm", "install"])
    if packages_installed != 0:
        raise Exception(
            "please make sure npm is installed, otherwise view "
            "the above error for more info."
        )

    webpack_complete = subprocess.call(["npm", "run", "dev"])
    if webpack_complete != 0:
        raise Exception(
            "Webpack appears to have failed to build your "
            "frontend. See the above error for more information."
        )
    os.chdir(return_dir)


@hydra.main(config_name='scriptconfig')
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    shared_state = SharedStaticTaskState(
        static_task_data=[
            {"text": "This text is good text!"},
            {"text": "This text is bad text!"},
        ],
        validate_onboarding=onboarding_always_valid,
    )

    build_task(task_dir)

    db, cfg = load_db_and_validate_config(cfg)
    operator = Operator(db)

    operator.validate_and_run_config_or_die(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)

if __name__ == "__main__":
    main()
