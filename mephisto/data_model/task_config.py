#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import json
from dataclasses import dataclass, field
from shutil import copytree
from typing import List, Any, TYPE_CHECKING, Optional, Dict
from omegaconf import MISSING, OmegaConf
import argparse
import shlex

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup


CONFIG_FILE_PATH = "task_config.json"


@dataclass
class TaskConfigArgs:
    """Object for grouping the contents to configure a class"""

    task_name: Optional[str] = field(
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
    task_tags: str = field(
        default=MISSING,
        metadata={
            "help": "Comma seperated tags for workers to use to find your task.",
            "required": True,
        },
    )
    assignment_duration_in_seconds: int = field(
        default=30 * 60,
        metadata={"help": "Time that workers have to work on your task once accepted."},
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


class TaskConfig:
    """
    Class that queries and sets important task information
    that is required to launch for all providers and task types
    """

    ArgsClass = TaskConfigArgs

    # TODO(#94?) TaskConfigs should probably be removed in favor of relying on
    # just hydra arguments
    def __init__(self, task_run: "TaskRun"):
        self.db = task_run.db
        args = task_run.args
        if args is None:
            return

        # Parse out specific arguments for the task_config
        self.args: Dict[str, Any] = args.task
        self.task_title: str = self.args["task_title"]
        self.task_description: str = self.args["task_description"]
        self.task_reward: float = self.args["task_reward"]
        self.task_tags: List[str] = [
            s.strip() for s in self.args["task_tags"].split(",")
        ]
        self.assignment_duration_in_seconds: int = self.args[
            "assignment_duration_in_seconds"
        ]
        self.allowed_concurrent: int = self.args["allowed_concurrent"]
        self.maximum_units_per_worker: int = self.args["maximum_units_per_worker"]

    @classmethod
    def get_mock_params(cls) -> str:
        """Returns a param string with default / mock arguments to use for testing"""
        from mephisto.operations.hydra_config import MephistoConfig

        return OmegaConf.structured(
            MephistoConfig(
                task=TaskConfigArgs(
                    task_title="Mock Task Title",
                    task_reward=0.3,
                    task_tags="mock,task,tags",
                    task_description="This is a test description",
                )
            )
        )
