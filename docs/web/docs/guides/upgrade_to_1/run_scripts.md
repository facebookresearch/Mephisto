---
sidebar_position: 2
---

# Migrating Run Scripts

Prior to Mephisto 1.0, our run scripts relied directly on Hydra semantics to settle in to launch things. This led to some unclear import ordering (not including `"_self_"` at times), boilerplate on registering the configs, and other issues.

This guide seeks to provide all of the steps to upgrade your run scripts to work properly.

In 1.0 we've released a new decorator (`task_script`) as well as some additional hydra configuration improvements (`build_default_task_config`). We've also deprecated use of `operator.validate_and_run_config` in favor of `operator.launch_task_run`. To get you upgraded you'll need to change your `@hydra.main` and this operator call. Here's how:

## Upgrading `@hydra.main` to `@task_script`

The biggest part of this migration is moving to use `@task_script`, which is a decorator that abstracts away most of the process of dealing with Hydra. Regardless of the args you use, you'll first need to update your main signature.

### main signature
The old main signature expected just a `DictConfig`, while the new one expects both an `Operator` and a `DictConfig`.
```python
# before
import hydra
...
@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:

# after
from mephisto.tools.scripts import task_script
...
@task_script(...)
def main(operator: Operator, cfg: DictConfig) -> None:
```

### Picking `@task_script` args
Now, you'll actually need to fill in arguments for the `@task_script` decorator. If the only custom arguments you were using in your `RunScriptConfig` were `defaults`, `task_dir`, and `num_tasks` you're in luck as these are all included in the new `TaskConfig`! You'll follow the simple migration. If you did create your own arguments, you're still in luck as the new syntax is still much cleaner than the old one! You can follow the complex case.

**Note:** if you were using a `config_path` other than `hydra_configs` in the folder your run script was in, you'll have to pass that `config_path` to `@task_script` now instead.

#### Simple Case (no custom script args)
Almost all of the hydra initialization can just be boiled down to the name of the `conf` file you intend to use (minus the `.yaml`)
```python
# before
import hydra
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
defaults = ["_self_", {"conf": "example"}]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    num_tasks: int = 5

register_script_config(name="scriptconfig", module=TestScriptConfig)

@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:


# after

from mephisto.operations.operator import Operator
from omegaconf import DictConfig
from mephisto.tools.scripts import task_script

@task_script(default_config_file="example")
def main(operator: Operator, cfg: DictConfig) -> None:
```
And that's it! Just move the name present in `{"conf": "this_right_here"}` to the arg you pass in as `default_config_file` to `@task_script`.

#### Complex Case (some custom script args)
In the more complex case, you'll still need to provide some custom dataclass for Hydra to identify the args you want to pass to your script. For this you'll create a config just for your args, and pass that along to `@task_script` instead. We rely on `build_default_task_config` to create the base class for your `TaskConfig`, using the same `default_config_file` that you used to pass in as `"conf"`. You can then pass your custom `TaskConfig` as the `config` argument to `@task_script`.

```python
import os
import hydra
from mephisto.operations.operator import Operator
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CORRECT_ANSWER = "apple"

defaults = ["_self_", {"conf": "onboarding_example"}]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    correct_answer: str = CORRECT_ANSWER

register_script_config(name="scriptconfig", module=TestScriptConfig)

@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:


# after
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script
from mephisto.operations.hydra_config import build_default_task_config
from omegaconf import DictConfig
from dataclasses import dataclass

CORRECT_ANSWER = "apple"

@dataclass
class OnboardingConfig(build_default_task_config('onboarding_example')): # type: ignore
    correct_answer: str = CORRECT_ANSWER


@task_script(config=OnboardingConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
```
In this case we were able to retain the custom `correct_answer` behavior while still cutting down on the overall boilerplate.

## Updating  main script contents

### Processing your config, or initializing a MephistoDB or Operator
Now that we supply your script with an `Operator`, you no longer need to use `load_db_and_process_config` or any other config processing script helper. We pre-process the `cfg` that we provide you to ensure it is valid. You can also retrieve the `MephistoDB` for your task directly from the `Operator` with `operator.db`, so no need to initialize that directly either.

### Launching a run from your operator
This change is really simple, just replace any callsites to `validate_and_run_config` with `launch_task_run`. The function signature is the same.
