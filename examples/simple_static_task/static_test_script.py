#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import time
import shlex
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir
from mephisto.server.blueprints.static_task.static_html_blueprint import BLUEPRINT_TYPE
from mephisto.utils.scripts import MephistoRunScriptParser

(
    architect_type,
    requester_name,
    db,
    _args,
) = MephistoRunScriptParser().parse_launch_arguments()

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/simple_static_task")

task_title = "Test static task"
task_description = "This is a simple test of static tasks."

ARG_STRING = (
    f"--blueprint-type {BLUEPRINT_TYPE} "
    f"--architect-type {architect_type} "
    f"--requester-name {requester_name} "
    f'--task-title "\\"{task_title}\\"" '
    f'--task-description "\\"{task_description}\\"" '
    "--task-reward 0.3 "
    "--task-tags static,task,testing "
    f'--data-csv "{TASK_DIRECTORY}/data.csv" '
    f'--task-source "{TASK_DIRECTORY}/server_files/demo_task.html" '
    f'--preview-source "{TASK_DIRECTORY}/server_files/demo_preview.html" '
    f'--extra-source-dir "{TASK_DIRECTORY}/server_files/extra_refs" '
    f"--units-per-assignment 2 "
)

operator = Operator(db)
operator.parse_and_launch_run_wrapper(shlex.split(ARG_STRING))
operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
