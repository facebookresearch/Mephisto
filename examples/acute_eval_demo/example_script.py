#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir


"""
Example script for running ACUTE-EVAL.
The only argument that *must* be modified for this to be run is:
``pairings_filepath``:  Path to pairings file in the format specified in the README.md

The following args are useful to tweak to fit your specific needs;
    - ``annotations_per_pair``: A useful arg if you'd like to evaluate a given conversation pair
                                more than once.
    - ``num_matchup_pairs``:    Essentially, how many pairs of conversations you would like to evaluate
    - ``subtasks_per_unit``:     How many comparisons you'd like a turker to complete in one HIT

Help strings for the other arguments can be found in run.py.
"""

USE_LOCAL = True

db = LocalMephistoDB()

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/acute_eval_demo")

# ARG_STRING goes through shlex.split twice, hence be careful if these
# strings contain anything which needs quoting.
task_title = "Which Conversational Partner is Better?"
task_description = "Evaluate quality of conversations through comparison."
hit_keywords = "chat,evaluation,comparison,conversation"

provider_type = "mock" if USE_LOCAL else "mturk_sandbox"
architect_type = "local" if USE_LOCAL else "heroku"

# The first time round, need to call the following here.
# TODO make this more user friendly than needing to uncomment script lines
# db.new_requester("<some_email_address>", "mock")
# db.new_requester("<your_email_address>_sandbox", "mturk_sandbox")

requester = db.find_requesters(provider_type=provider_type)[-1]
requester_name = requester.requester_name
assert USE_LOCAL or requester_name.endswith(
    "_sandbox"
), "Should use a sandbox for testing"

# The first time using mturk, need to call the following here
# requester.register()

ARG_STRING = (
    "--blueprint-type acute_eval "
    f"--architect-type {architect_type} "
    f"--requester-name {requester_name} "
    f'--task-title "\\"{task_title}\\"" '
    f'--task-description "\\"{task_description}\\"" '
    "--task-reward 0.5 "
    f"--task-tags {hit_keywords} "
    f"--subtasks-per-unit 2 "  # num comparisons to show within one unit
    f"--maximum-units-per-worker 0 " # Num of units a worker is allowed to do, 0 is infinite
    f"--allowed-concurrent 1 " # Workers can only do one task at a time, or onboarding may break
)

extra_args = {
    "pairings_filepath": f"{TASK_DIRECTORY}/pairings.jsonl",
    "block_on_onboarding_fail": True,
    "block_qualification": "onboarding_qual_name",
    "annotations_per_pair": 1,  # num times to use the same conversation pair
    "random_seed": 42,  # random seed
    "subtasks_per_unit": 2,  # num comparisons to show within one hit
    "num_matchup_pairs": 2,  # num pairs of conversations to be compared
    # question phrasing
    "s1_choice": "I would prefer to talk to <Speaker 1>",
    "s2_choice": "I would prefer to talk to <Speaker 2>",
    "eval_question": "Who would you prefer to talk to for a long conversation?",
}

try:
    operator = Operator(db)
    operator.parse_and_launch_run(shlex.split(ARG_STRING), extra_args=extra_args)
    print("task run supposedly launched?")
    print(operator.get_running_task_runs())
    while len(operator.get_running_task_runs()) > 0:
        print(f"Operator running {operator.get_running_task_runs()}")
        time.sleep(10)
except Exception as e:
    import traceback

    traceback.print_exc()
except (KeyboardInterrupt, SystemExit) as e:
    pass
finally:
    operator.shutdown()


# TODO these args are not yet configurable in mephisto
# args['assignment_duration_in_seconds'] = 600
