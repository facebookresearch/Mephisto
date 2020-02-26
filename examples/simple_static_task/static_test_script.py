import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir

db = LocalMephistoDB()

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/simple_static_task")

operator = Operator(db)
requester = db.find_requesters(provider_type="mturk_sandbox")[-1]
requester_name = requester.requester_name
assert requester_name.endswith("_sandbox"), "Should use a sandbox for testing"
print(requester)
print(requester.provider_type)
ARG_STRING = (
    "--blueprint-type static "
    "--architect-type heroku "
    f"--requester-name {requester_name} "
    '--task-title "Test-static-task" '
    "--task-description description "
    "--task-reward 0.3 "
    "--task-tags static,task,testing "
    f'--data-csv "{TASK_DIRECTORY}/data.csv" '
    f'--task-source "{TASK_DIRECTORY}/server_files/demo_task.html" '
    f'--preview-source "{TASK_DIRECTORY}/server_files/demo_preview.html" '
    f'--extra-source-dir "{TASK_DIRECTORY}/server_files/extra_refs" '
)

try:
    operator.parse_and_launch_run(shlex.split(ARG_STRING))
    print("task run supposedly launched?")
    print(operator.get_running_task_runs())
    while len(operator.get_running_task_runs()) > 0:
        print(f"Operator running {operator.get_running_task_runs()}")
        time.sleep(10)
except BaseException as e:
    import traceback

    traceback.print_exc()
    pass

operator.shutdown()
