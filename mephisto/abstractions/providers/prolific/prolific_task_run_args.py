#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from dataclasses import field
from dataclasses import MISSING


@dataclass
class ProlificTaskRunArgs:
    """
    More details about Prolific fields:
        https://docs.prolific.co/docs/api-docs/public/#tag/Studies/The-study-object

    Usage:
        from mephisto.abstractions.providers.prolific.prolific_task_run_args import (
            ProlificTaskRunArgs
        )

        @task_script(default_config_file="example", task_run_args_cls=ProlificTaskRunArgs)
        def main(operator, cfg: DictConfig) -> None:
            operator.launch_task_run(cfg.mephisto)
            operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
    """
    task_name: str = field(
        default=MISSING,
        metadata={
            "help": "Grouping to launch this task run under, none defaults to the blueprint type"
        },
    )
    task_title: str = field(
        default=MISSING,
        metadata={
            "help": "Display title for your task on the crowd provider.",
            "required": True,
        },
    )
    task_description: str = field(
        default=MISSING,
        metadata={
            "help": "Longer form description for what your task entails.",
            "required": True,
        },
    )
    task_reward: float = field(
        default=MISSING,
        metadata={
            "help": "Amount to pay per worker per unit, in dollars.",
            "required": True,
        },
    )

    prolific_external_study_url: str = field(
        default=MISSING,
        metadata={
            'help': (
                'The external study URL of your study that you want participants to be direct to. '
                'The URL can be customized to add information to match participants '
                'in your survey. '
                'You can add query parameters with the following placeholders.'
            ),
        },
    )
    prolific_estimated_completion_time_in_minutes: int = field(
        default=5,
        metadata={
            'help': (
                'Estimated duration in minutes of the experiment or survey '
                '(`estimated_completion_time` in Prolific).'
            ),
        },
    )

    prolific_total_available_places: int = field(
        default=1,
        metadata={
            'help': 'How many participants are you looking to recruit.',
        },
    )

    no_submission_patience: int = field(
        default=60 * 60 * 12,
        metadata={
            "help": (
                "How long to wait between task submissions before shutting the run down "
                "for a presumed issue. Value in seconds, default 12 hours. "
            )
        },
    )
    allowed_concurrent: int = field(
        default=0,
        metadata={
            "help": "Maximum units a worker is allowed to work on at once. (0 is infinite)",
            "required": True,
        },
    )
    maximum_units_per_worker: int = field(
        default=0,
        metadata={
            "help": (
                "Maximum tasks of this task name that a worker can work on across all "
                "tasks that share this task_name. (0 is infinite)"
            )
        },
    )
    max_num_concurrent_units: int = field(
        default=0,
        metadata={
            "help": (
                "Maximum units that will be released simultaneously, setting a limit "
                "on concurrent connections to Mephisto overall. (0 is infinite)"
            )
        },
    )
    submission_timeout: int = field(
        default=600,
        metadata={
            "help": (
                "Time that mephisto will wait after marking a task done before abandoning "
                "waiting for the worker to actually press submit."
            )
        },
    )
    post_install_script: str = field(
        default="",
        metadata={
            "help": (
                "The name of a shell script in your webapp directory t"
                "hat will run right after npm install and before npm build."
                "This can be useful for local package development where you would want to link "
                "a package after installing dependencies from package.json"
            )
        },
    )
    assignment_duration_in_seconds: int = field(
        default=30 * 60,
        metadata={"help": "Time that workers have to work on your task once accepted."},
    )
