# Transitioning from ARG_STRING to Hydra
As Mephisto has moved away from the `ARG_STRING` in [#246](https://github.com/facebookresearch/Mephisto/pull/246), all existing scripts that used to use the `ARG_STRING` will need to use Hydra moving forward.

This document shows the transition steps from moving from the old format to the new format, using the `ParlAIChatBlueprint` as an example.

# Original file
```python
# parlai_test_script.py
import os
import time
import shlex
from mephisto.operations.operator import Operator
from mephisto.utils.dirs import get_root_dir
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import BLUEPRINT_TYPE
from mephisto.tools.scripts import MephistoRunScriptParser, str2bool

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
```

# Breaking it down
## Replacing the ARG_STRING
### Before
Configuration used to be centered within the `ARG_STRING`:
```python
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
...
    ARG_STRING += f"--onboarding-qualification test-parlai-chat-qualification "

...
    ARG_STRING += f"--custom-source-bundle {bundle_file_path} "
...
    ARG_STRING += f"--custom-source-dir {source_dir_path} "
```
### After
Beyond the first three components of the arg string (which select the major components to use), each of these `ARG_STRING` components corresponds to one of the `architect`, `blueprint`, `provider`, or `task` argument sets in Hydra. The ones of these that are common to all tasks (or that you'll tend to use in most launches), you can move to a `base.yaml` file:
```yaml
# base.yaml
#@package _global_
mephisto:
  blueprint:
    world_file: ${task_dir}/demo_worlds.py
    task_description_file: ${task_dir}/task_description.html
    num_conversations: 1
```
The remaining options that will potentially differ between runs can go into their own files. Here we have separate files for the base run, and one that uses a custom source directory:
```yaml
# example.yaml
#@package _global_
mephisto:
  task:
    task_name: parlai-chat-example
    task_title: "Test ParlAI Chat Task"
    task_description:
      "This is a simple chat between two people
      used to demonstrate the functionalities around using Mephisto
      for ParlAI tasks."
    task_reward: 0.3
    task_tags: "dynamic,chat,testing"
# custom_simple.yaml
mephisto:
  blueprint:
    custom_source_dir: ${task_dir}/custom_simple
  task:
    task_name: parlai-chat-example
    task_title: "Test ParlAI Simply Built Chat Task"
    task_description:
      "This is a simple chat between two people
      used to demonstrate the functionalities around using Mephisto
      for ParlAI tasks."
    task_reward: 0.3
    task_tags: "dynamic,chat,testing"
```
You can print the contents of `OmegaConf.to_yaml(cfg)` in your scripts to see the arguments that can be used or set.

## Adding additional arguments, and configuring defaults
### Before
It used to be the case that additional arguments were added to the `RunScriptParser`
```python
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
```
Many of these are set directly as part of the standard Mephisto config now, as arguments about using onboarding and such are exposed directly in the hydra config. Some of these are handled differently now though.

### After
We replace configuring via argparse and `RunScriptParser` by using a `dataclass` containing the configuration you want to add to a script. In the below we add `num_turns` and `turn_timeout` as options.

Via variable interpolation in hydra, we can define `task_dir` in this configuration file, and refer to this in other arguments with `${task_dir}`.

```python
TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": 'local'},
    {"mephisto/provider": 'mock'},
    "conf/base",
    {"conf": "example"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    num_turns: int = field(
        default=3,
        metadata={
            'help': "Number of turns before a conversation is complete",
        },
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            'help':
                "Maximum response time before kicking "
                "a worker out, default 300 seconds",
        },
    )

register_script_config(name='scriptconfig', module=TestScriptConfig)
```

Most of the new configuration happens in the `TestScriptConfig`. This will need to inherit from `RunScriptConfig` in order to get parsing of the standard `mephisto` components for free. Afterwards, we need to call `register_script_config` and name our configuration file such that Hydra knows what to parse from the command line when you execute your script.

#### defaults
It's important to note the step of creating the `defaults` entry for your `RunScriptConfig`. This will provide Hydra with some default values for keys in the created `yaml` file. The `{"mephisto/blueprint": BLUEPRINT_TYPE},` entry ensures that Hydra loads up the blueprint argument configuration that corresponds with the blueprint you're running, for instance.

Setting `architect` to `local` and `provider` to `mock` will make the script default to that configuration when given no arguments, however you can provide different values either in configuration files or on the command line (with `mephisto.provider.requester_name=some_requester`, or `mephisto/architect=heroku` for instance). Configuring a full abstraction uses slash notation as in `mephisto/abstraction=value`, while configuring variables within an abstraction uses dot notation as in `mephisto/abstraction.variable=value`.

The entry with just `"conf/base"` tells hydra to load the entire contents of `conf/base.yaml` as default values.

Lastly, `{"conf": "example"},` gives hydra the command to load specifically the configuration in `conf/example.yaml`, however on the command line you can use `conf=<>` to make hydra use the defaults you've specified in a different configuration file instead. This last line is useful for a demo version for your script, but it's likely your important configuration options will exist in files you can access with `python script.py conf=<>` instead.

## Extra arguments
### Before
Extra arguments used to be provided via the `extra_args` parameter to the run script, however this used to be merged with the regular argument dict passed in.
```python
world_opt = {"num_turns": 3, "turn_timeout": args["turn_timeout"]}
...
extra_args = {"world_opt": world_opt, "onboarding_world_opt": world_opt}
```
### After
Mephisto now asks that tasks specify their shared state with `SharedTaskState`. The `ParlAIChatBlueprint` now specifies a `SharedParlAITaskState` that we pass instead.
```python
world_opt = {
    "num_turns": cfg.num_turns,
    "turn_timeout": cfg.turn_timeout,
}
...
    world_opt["send_task_data"] = True

shared_state = SharedParlAITaskState(
    world_opt=world_opt,
    onboarding_world_opt=world_opt,
)
```

## Argument validation
### Before
Before, it used to be the case that the call to `parse_launch_arguments` would validate the given requester and much of the input configuration. Other arguments were validated at varying points of the script.
```python
architect_type, requester_name, db, args = parser.parse_launch_arguments()
...
if DEMO_CUSTOM_BUNDLE:
    bundle_file_path = f"{TASK_DIRECTORY}/webapp/build/bundle.js"
    assert os.path.exists(bundle_file_path), (
        "Must build the custom bundle with `npm install; npm run dev` from within "
        f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
    )
```
### After
Now, the script arguments are generally validated by Hydra, so much of what `parse_launch_arguments` used to do is irrelevant, so long as you wrap your main with `@hydra.main` and pass in the config name you gave to your `RunScriptConfig` with `register_script_config`. The remainder is captured with the new `augment_config_from_db` method. Manual validation can also be done where desired in the main script.
```python
@hydra.main(config_name='scriptconfig')
def main(cfg: DictConfig) -> None:
    db, cfg = load_db_and_process_config(cfg)
    ...
    custom_bundle_path = cfg.mephisto.blueprint.get('custom_source_bundle', None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
        )
```

## Calling the operator
### Before
```python
operator = Operator(db)
operator.parse_and_launch_run_wrapper(shlex.split(ARG_STRING), extra_args=extra_args)
operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
```

### After
```python
operator = Operator(db)

operator.validate_and_run_config(cfg.mephisto, shared_state)
operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
```
## Imports
### Before
```python
import os
import shlex  # shlex is no longer required, as we're not using arg strings
from mephisto.operations.operator import Operator
from mephisto.utils.dirs import get_root_dir
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import BLUEPRINT_TYPE
from mephisto.tools.scripts import MephistoRunScriptParser, str2bool # RunScriptParser has been deprecated.
```

We remove unnecessary or deprecated imports.

### After
We'll need to add a few things. First, `load_db_and_process_config` covers the old capabilities of the `MephistoRunScriptParser`.
Mephisto now defines run scripts and configurations using Hydra and dataclasses, as such you'll need some imports from `dataclasses`, `hydra`, and `omegaconf` (which is the configuration library that powers hydra).
```python
import os
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import BLUEPRINT_TYPE, SharedParlAITaskState

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any
```

# Putting it all together
## Run file
```python
# parlai_test_script.py
import os
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import BLUEPRINT_TYPE, SharedParlAITaskState

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": 'local'},
    {"mephisto/provider": 'mock'},
    "conf/base",
    {"conf": "example"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    num_turns: int = field(
        default=3,
        metadata={
            'help': "Number of turns before a conversation is complete",
        },
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            'help':
                "Maximum response time before kicking "
                "a worker out, default 300 seconds",
        },
    )

register_script_config(name='scriptconfig', module=TestScriptConfig)


@hydra.main(config_name='scriptconfig')
def main(cfg: DictConfig) -> None:
    db, cfg = load_db_and_process_config(cfg)

    world_opt = {
        "num_turns": cfg.num_turns,
        "turn_timeout": cfg.turn_timeout,
    }

    custom_bundle_path = cfg.mephisto.blueprint.get('custom_source_bundle', None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
        )
        world_opt["send_task_data"] = True

    shared_state = SharedParlAITaskState(
        world_opt=world_opt,
        onboarding_world_opt=world_opt,
    )

    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)

if __name__ == "__main__":
    main()
```

## Configuration files
### Base config
```yaml
# base.yaml
#@package _global_
mephisto:
  blueprint:
    world_file: ${task_dir}/demo_worlds.py
    task_description_file: ${task_dir}/task_description.html
    num_conversations: 1
```

### Example run file
```yaml
# example.yaml
#@package _global_
mephisto:
  task:
    task_name: parlai-chat-example
    task_title: "Test ParlAI Chat Task"
    task_description:
      "This is a simple chat between two people
      used to demonstrate the functionalities around using Mephisto
      for ParlAI tasks."
    task_reward: 0.3
    task_tags: "dynamic,chat,testing"
```
