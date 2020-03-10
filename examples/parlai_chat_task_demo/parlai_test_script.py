import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir

USE_LOCAL = True

db = LocalMephistoDB()

operator = Operator(db)

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/parlai_chat_task_demo")

if USE_LOCAL:
    requester = db.find_requesters(provider_type="mock")[-1]
    requester_name = requester.requester_name
    ARG_STRING = (
        "--blueprint-type parlai_chat "
        "--architect-type local "
        f"--requester-name {requester_name} "
        "--num-conversations 1 "
        '--task-title "Test-parlai-chat-task" '
        "--task-description description "
        "--task-reward 0.3 "
        "--task-tags parlai_chat,task,testing "
        f'--world-file "{TASK_DIRECTORY}/demo_worlds.py"'
    )
else:
    requester = db.find_requesters(provider_type="mturk_sandbox")[-1]
    requester_name = requester.requester_name
    assert requester_name.endswith("_sandbox"), "Should use a sandbox for testing"
    print(requester)
    print(requester.provider_type)
    ARG_STRING = (
        "--blueprint-type parlai_chat "
        "--architect-type heroku "
        f"--requester-name {requester_name} "
        "--num-conversations 1 "
        '--task-title "Test-parlai-chat-task" '
        "--task-description description "
        "--task-reward 0.3 "
        "--task-tags parlai_chat,task,testing "
        f'--world-file "{TASK_DIRECTORY}/demo_worlds.py"'
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
