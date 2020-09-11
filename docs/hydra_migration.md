Initial code:

```python
# static_test_script.py
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

```


final code:
```python
# static_test_script.py
import os
import time
import shlex
from mephisto.core.operator import Operator
from mephisto.core.utils import get_root_dir
from mephisto.server.blueprints.static_task.static_html_blueprint import BLUEPRINT_TYPE
from mephisto.utils.scripts import get_db_from_config

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any


TASK_DIRECTORY = os.path.join(get_root_dir(), "examples/simple_static_task")

defaults = [
    {"mephisto.blueprint": BLUEPRINT_TYPE},
    {"mephisto.architect": 'local'},
    {"mephisto.provider": 'mock'},
    {"conf": "example"},
]

from mephisto.core.hydra_config import ScriptConfig, register_script_config

@dataclass 
class TestScriptConfig(ScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY

register_script_config(name='scriptconfig', module=TestScriptConfig)

@hydra.main(config_name='scriptconfig')
def main(cfg: DictConfig) -> None:
    db = get_db_from_config(cfg)
    operator = Operator(db)

    operator.validate_and_run_config_wrap(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)

if __name__ == "__main__":
    main()
```

```yaml
# example.yaml
#@package _global_
mephisto:
  blueprint:
    data_csv: ${task_dir}/data.csv 
    task_source: ${task_dir}/server_files/demo_task.html
    preview_source: ${task_dir}/server_files/demo_preview.html
    extra_source_dir: ${task_dir}/server_files/extra_refs
    units_per_assignment: 2
  task:
    task_title: "Test static task"
    task_description: "This is a simple test of static tasks."
    task_reward: 0.3
    task_tags: "static,task,testing"
```