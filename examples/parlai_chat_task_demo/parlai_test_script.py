#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import time
import shlex
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir
from mephisto.server.blueprints.parlai_chat.parlai_chat_blueprint import BLUEPRINT_TYPE
from mephisto.utils.scripts import MephistoRunScriptParser, str2bool

parser = MephistoRunScriptParser()
parser.add_argument(
    "-uo",
    "--use-onboarding",
    default=False,
    help="Launch task with an onboarding world",
    type=str2bool,
)
parser.add_argument(
    "-uct",
    "--use-custom-task",
    default=False,
    help="Launch task with custom pre-built javascript",
    type=str2bool,
)
parser.add_argument(
    "-bct",
    "--build-custom-task",
    default=False,
    help="Launch task after building new custom js",
    type=str2bool,
)
parser.add_argument(
    "-tt",
    "--turn-timeout",
    default=300,
    help="Maximum response time before kicking a worker out, default 300 seconds",
    type=int,
)

architect_type, requester_name, db, args = parser.parse_launch_arguments()

USE_LOCAL = True
DEMO_CUSTOM_BUNDLE = args["use_custom_task"]
DEMO_BUILD_SIMPLE = args["build_custom_task"]
USE_ONBOARDING = args["use_onboarding"]

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/parlai_chat_task_demo")

task_title = "Test ParlAI Chat Task"
task_description = (
    "This is a simple chat between two people used to demonstrate "
    "the functionalities around using Mephisto for ParlAI tasks."
)

ARG_STRING = (
    f"--blueprint-type {BLUEPRINT_TYPE} "
    f"--architect-type {architect_type} "
    f"--requester-name {requester_name} "
    f'--task-title "\\"{task_title}\\"" '
    f'--task-description "\\"{task_description}\\"" '
    "--task-reward 0.3 "
    "--task-tags dynamic,chat,testing "
    f'--world-file "{TASK_DIRECTORY}/demo_worlds.py" '
    f'--task-description-file "{TASK_DIRECTORY}/task_description.html" '
    "--num-conversations 1 "
)

if USE_ONBOARDING:
    ARG_STRING += f"--onboarding-qualification test-parlai-chat-qualification "

world_opt = {"num_turns": 3, "turn_timeout": args["turn_timeout"]}

if DEMO_CUSTOM_BUNDLE:
    bundle_file_path = f"{TASK_DIRECTORY}/webapp/build/bundle.js"
    assert os.path.exists(bundle_file_path), (
        "Must build the custom bundle with `npm install; npm run dev` from within "
        f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
    )
    world_opt["send_task_data"] = True
    ARG_STRING += f"--custom-source-bundle {bundle_file_path} "
if DEMO_BUILD_SIMPLE:
    source_dir_path = f"{TASK_DIRECTORY}/custom_simple"
    ARG_STRING += f"--custom-source-dir {source_dir_path} "

extra_args = {"world_opt": world_opt, "onboarding_world_opt": world_opt}

operator = Operator(db)
operator.parse_and_launch_run_wrapper(shlex.split(ARG_STRING), extra_args=extra_args)
operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
