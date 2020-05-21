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
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir
from mephisto.server.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE,
)
from mephisto.utils.scripts import MephistoRunScriptParser, str2bool

import random

parser = MephistoRunScriptParser()
parser.add_argument(
    "-uo",
    "--use-onboarding",
    default=False,
    help="Launch task with an onboarding world",
    type=str2bool,
)
architect_type, requester_name, db, args = parser.parse_launch_arguments()

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FRONTEND_SOURCE_DIR = os.path.join(TASK_DIRECTORY, "webapp")
FRONTEND_BUILD_DIR = os.path.join(FRONTEND_SOURCE_DIR, "build")
STATIC_FILES_DIR = os.path.join(FRONTEND_SOURCE_DIR, "src", "static")
USE_ONBOARDING = args["use_onboarding"]

task_title = "Rating a sentence as good or bad"
task_description = "In this task, you'll be given a sentence. It is your job to rate it as either good or bad."

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
    f"--task-name react-static-task-example "
    f'--extra-source-dir "{STATIC_FILES_DIR}" '
)

if USE_ONBOARDING:
    ARG_STRING += f"--onboarding-qualification test-react-static-qualification "

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
