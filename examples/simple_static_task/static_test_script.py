import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir

USE_LOCAL = True

db = LocalMephistoDB()

operator = Operator(db)

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/simple_static_task")

# ARG_STRING goes through shlex.split twice, hence be careful if these
# strings contain anything which needs quoting.
task_title = "Test static task"
task_description = "This is a simple test of static tasks."

provider_type = "mock" if USE_LOCAL else "mturk_sandbox"
architect_type = "local" if USE_LOCAL else "heroku"

# The first time round, need to call the following here.
# TODO(#95) make this more user friendly than needing to uncomment script lines
# db.new_requester("<mturk_account_name>", "mturk")
# db.new_requester("<mturk_account_name>_sandbox", "mturk_sandbox")

if USE_LOCAL:
    from mephisto.core.utils import get_mock_requester

    requester = get_mock_requester(db)
else:
    requester = db.find_requesters(provider_type=provider_type)[-1]
requester_name = requester.requester_name
assert USE_LOCAL or requester_name.endswith(
    "_sandbox"
), "Should use a sandbox for testing"

# The first time using mturk, need to call the following here
# requester.register()

ARG_STRING = (
    "--blueprint-type static "
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

try:
    operator.parse_and_launch_run(shlex.split(ARG_STRING))
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
