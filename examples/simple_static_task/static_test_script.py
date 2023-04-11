#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from dataclasses import field
from mephisto.abstractions.blueprints.static_html_task.static_html_blueprint import (
    BLUEPRINT_TYPE_STATIC_HTML,
)
from mephisto.data_model.task_run import TaskRunArgs
from mephisto.tools.scripts import task_script
from omegaconf import DictConfig


@dataclass
class TaskRunArgs2(TaskRunArgs):
    test: int = field(
        default=500,
    )


@task_script(default_config_file="example", task_run_args_cls=TaskRunArgs2)
def main(operator, cfg: DictConfig) -> None:
    operator.launch_task_run(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
