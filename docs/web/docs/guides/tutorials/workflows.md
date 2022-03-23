---
sidebar_position: 4
---

# Developing a workflow

While it's nice to imagine that you'll be able to collect quality data on the first pass, crowdsourcing can be a bit more trial-and-error. This guide focuses on setting up a good workflow, and extending your run-script to support additional functionality. 

This tutorial is pretty loose at the moment, as many of these practices are _about_ clever Mephisto usage rather than specific features that are codified yet. We aim to be flexible, and while these workflows have worked for us we expect many to adapt from and expand on them.

## Proper use of `task_name`

It's generally advisable to use different `task_name`s for every iteration you do on a task, generally moving from `testing` through `pilots` to deploys. Mephisto does not prescribe a specific method for what you must do, but you may find this framework a good starting point.

```python
# for local use while testing and debugging
my-cool-task-local-testing
# For rounds of pilots
my-cool-task-pilot-1
my-cool-task-pilot-2
...
# For actual launches
my-cool-task-live-batch-1
my-cool-task-live-batch-2
...
```
Generally it's best to put the `task_name` _into_ your Hydra `.yaml` config and create different configs for different purposes. For instance:
```yaml
# local_testing.yaml
#@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
mephisto:
  blueprint:
    ...
    onboarding_qualification: my-task-onboarding-qualification-sandbox
  task:
    task_name: my-task-local-testing
    ...
num_tasks: 2

# live_batch_1.yaml
#@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: heroku
  - /mephisto/provider: mturk
mephisto:
  blueprint:
    ...
    onboarding_qualification: my-task-onboarding-qualification
  task:
    task_name: react-static-task-example
    ...
    max_num_concurrent_units: 100
num_tasks: 2000
```
This also means you can go back and find the configuration details for a specific task run that you launched.

**Note:** The `mephisto.task.maximum_units_per_worker` argument is tied specifically to tasks sharing the same `task_name`, so if you want to limit the number of times a worker can do a task in this way you'll have to use the same `task_name` for all tasks you want to instill the limit on.


## Multi-purpose run scripts

For complex tasks with many configuration arguments, we make it possible to add arguments to your run script to simplify your workflows and allow for code reuse. For instance, say you had the following script:
```python
# examples/static_react_task/run_task.py
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script, build_and_return_custom_bundle
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)

from omegaconf import DictConfig


@task_script(default_config_file="example")
def main(operator: Operator, cfg: DictConfig) -> None:
    def onboarding_always_valid(onboarding_data):
        return True

    shared_state = SharedStaticTaskState(
        static_task_data=[
            {"text": "This text is good text!"},
            {"text": "This text is bad text!"},
        ],
        validate_onboarding=onboarding_always_valid,
    )

    task_dir = cfg.task_dir
    build_and_return_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
```

And you collected some initial pilot data, reviewed, and chose some specific high-quality workers to assign an [allowlist qualification](../../how_to_use/worker_quality/common_qualification_flows#allowlists-and-blocklists) to.

Now sometimes you want to launch with that allowlist, while othertimes you want to specifically look for new workers to add to your allowlist. Rather than require two separate scripts, you may create something like the following:
```python
from mephisto.data_model.qualification import QUAL_NOT_EXIST, QUAL_EXISTS
from mephisto.utils.qualifications import make_qualification_dict
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)

from omegaconf import DictConfig
from dataclasses import dataclass


@dataclass
class MyTaskConfig(build_default_task_config("onboarding_example")):  # type: ignore
    am_qualifiying_new_workers: str = False
    allowlist_qualification: str = 'my-allowlist-qual'


@task_script(config=MyTaskConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
    correct_config_answer = cfg.correct_answer

    def onboarding_is_valid(onboarding_data):
        inputs = onboarding_data["inputs"]
        outputs = onboarding_data["outputs"]
        return outputs.get("answer") == correct_config_answer


    if cfg.am_qualifiying_new_workers:
        use_qualifications = [
            make_qualification_dict(
                cfg.allowlist_qualification,
                QUAL_NOT_EXIST,
            ),
        ]
    else:
        use_qualifications = [
            make_qualification_dict(
                cfg.allowlist_qualification,
                QUAL_EXISTS,
            ),
        ]

    shared_state = SharedStaticTaskState(
        onboarding_data={"correct_answer": correct_config_answer},
        validate_onboarding=onboarding_is_valid,
        qualifications=use_qualifications
    )

    if cfg.am_qualifiying_new_workers:
        shared_state.mturk_specific_qualifications = [
            # MTurk-specific quality control qualifications
        ]

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()

```

Now you can launch the same tasks in the two different contexts, adding workers to the pool when you want to extend the workers who are qualified, and using the allowlist when you just want to collect.

