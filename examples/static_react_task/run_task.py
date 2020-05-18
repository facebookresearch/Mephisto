#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import time
import shlex
import sh
import shutil
import subprocess
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir

import random

USE_LOCAL = True

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FRONTEND_SOURCE_DIR = os.path.join(TASK_DIRECTORY, "webapp")
FRONTEND_BUILD_DIR = os.path.join(FRONTEND_SOURCE_DIR, "build")
STATIC_FILES_DIR = os.path.join(FRONTEND_SOURCE_DIR, "src", "static")

db = LocalMephistoDB()

# ARG_STRING goes through shlex.split twice, hence be careful if these
# strings contain anything which needs quoting.
task_title = "Rating a sentence as good or bad"
task_description = (
    "In this task, you'll be given a sentence. It is your job to rate it as either good or bad."
)

provider_type = "mock" if USE_LOCAL else "mturk_sandbox"
architect_type = "local" if USE_LOCAL else "heroku"

requester_name = db.find_requesters(provider_type=provider_type)[-1].requester_name

assert USE_LOCAL or requester_name.endswith(
    "_sandbox"
), "Should use a sandbox for testing"


ARG_STRING = (
    "--blueprint-type static_react_task "
    f"--architect-type {architect_type} "
    f"--requester-name {requester_name} "
    f'--task-title "\\"{task_title}\\"" '
    f'--task-description "\\"{task_description}\\"" '
    "--task-reward 0.05 "
    "--task-tags test,simple,button "
    f'--task-source "{TASK_DIRECTORY}/webapp/build/bundle.js" '
    f"--units-per-assignment 1 "
    f"--task-name light-quest-pilot-test "
    f'--extra-source-dir "{STATIC_FILES_DIR}" '
)

extra_args = {
    "static_task_data": [
        {"text": "This text is good text!"},
        {"text": "This text is bad text!"},
    ]
}

# build the task
def build_task():
    """Rebuild the frontend for this task"""
    return_dir = os.getcwd()
    os.chdir(FRONTEND_SOURCE_DIR)
    if os.path.exists(FRONTEND_BUILD_DIR):
        shutil.rmtree(FRONTEND_BUILD_DIR)
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


build_task()

operator = Operator(db)
operator.parse_and_launch_run_wrapper(shlex.split(ARG_STRING), extra_args=extra_args)
operator.wait_for_runs_then_shutdown()
