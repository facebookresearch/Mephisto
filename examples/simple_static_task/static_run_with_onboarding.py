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

CORRECT_ANSWER = "apple"

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
    f'--onboarding-source "{TASK_DIRECTORY}/server_files/demo_onboarding.html" '
    f'--extra-source-dir "{TASK_DIRECTORY}/server_files/extra_refs" '
    f"--units-per-assignment 2 "
    f"--onboarding-qualification static-test-onboarding-qual"
)

def onboarding_is_valid(onboarding_data):
    print(onboarding_data)
    return onboarding_data.get('answer') == CORRECT_ANSWER

extra_args = {
    "validate_onboarding": onboarding_is_valid,
    "onboarding_data": {"correct_answer": CORRECT_ANSWER},
}

operator = Operator(db)
operator.parse_and_launch_run_wrapper(shlex.split(ARG_STRING), extra_args=extra_args)
operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
