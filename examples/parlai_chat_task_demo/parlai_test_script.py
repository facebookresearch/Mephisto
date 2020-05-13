import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir

USE_LOCAL = True
DEMO_CUSTOM_BUNDLE = True
USE_ONBOARDING = False

db = LocalMephistoDB()

TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/parlai_chat_task_demo")

task_title = "Test ParlAI Chat Task"
task_description = (
    "This is a simple chat between two people used to demonstrate "
    "the functionalities around using Mephisto for ParlAI tasks."
)

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
    "--blueprint-type parlai_chat "
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

world_opt = {"num_turns": 3}

if DEMO_CUSTOM_BUNDLE:
    bundle_file_path = f"{TASK_DIRECTORY}/webapp/build/bundle.js"
    assert os.path.exists(bundle_file_path), (
        "Must build the custom bundle with `npm install; npm run dev` from within "
        f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
    )
    world_opt["send_task_data"] = True
    ARG_STRING += f"--custom-source-bundle {bundle_file_path} "

extra_args = {"world_opt": world_opt}

operator = Operator(db)
operator.parse_and_launch_run(shlex.split(ARG_STRING), extra_args=extra_args)
operator.wait_for_runs_then_shutdown(log_rate=30)
