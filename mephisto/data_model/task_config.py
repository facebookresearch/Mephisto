#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import json
from shutil import copytree
from typing import List, Any, TYPE_CHECKING, Dict
import argparse
import shlex
from mephisto.core.utils import get_blueprint_from_type, get_crowd_provider_from_type

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup


CONFIG_FILE_PATH = "task_config.json"


class TaskConfig:
    """
    Class that queries and sets important task information
    that is required to launch for all providers and task types
    """

    # TODO(#94?) TaskConfigs should probably be immutable, and could ideally separate
    # the options that come from different parts of the ecosystem
    def __init__(self, task_run: "TaskRun"):
        self.db = task_run.db

        # Try to find existing parsed args
        arg_path = os.path.join(task_run.get_run_dir(), CONFIG_FILE_PATH)
        if os.path.exists(arg_path):
            with open(arg_path, "r") as config_file:
                args = json.load(config_file)
        else:
            # parse new arguments
            BlueprintClass = get_blueprint_from_type(task_run.task_type)
            CrowdProviderClass = get_crowd_provider_from_type(task_run.provider_type)
            param_string = task_run.param_string

            parser = argparse.ArgumentParser()
            blueprint_group = parser.add_argument_group("blueprint")
            BlueprintClass.add_args_to_group(blueprint_group)
            provider_group = parser.add_argument_group("crowd_provider")
            CrowdProviderClass.add_args_to_group(provider_group)
            task_group = parser.add_argument_group("task_config")
            TaskConfig.add_args_to_group(task_group)

            try:
                arg_namespace, _unknown = parser.parse_known_args(
                    shlex.split(param_string)
                )
            except SystemExit:
                raise Exception(f"Argparse broke on {param_string} - must fix")

            args = vars(arg_namespace)
            with open(arg_path, "w+") as config_file:
                json.dump(args, config_file)

        # Parse out specific arguments for the task_config
        self.args: Dict[str, Any] = args
        self.task_title: str = args["task_title"]
        self.task_description: str = args["task_description"]
        self.task_reward: float = args["task_reward"]
        self.task_tags: List[str] = [s.strip() for s in args["task_tags"].split(",")]
        self.assignment_duration_in_seconds: int = args["assignment_duration_seconds"]
        self.allowed_concurrent: int = args["allowed_concurrent"]
        self.maximum_units_per_worker: int = args["maximum_units_per_worker"]

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Defines options that are required to launch a task. These end up included in
        a TaskRun's additional options.
        """
        group.description = "Core task arguments required to run a task"
        group.add_argument(
            "--task-title",
            dest="task_title",
            help="Display title for your task on the crowd provider.",
            required=True,
        )
        group.add_argument(
            "--task-description",
            dest="task_description",
            help="Longer form description for what your task entails.",
            required=True,
        )
        group.add_argument(
            "--task-reward",
            dest="task_reward",
            help="Amount to pay per worker per unit.",
            type=float,
            required=True,
        )
        group.add_argument(
            "--task-tags",
            dest="task_tags",
            help="Comma seperated tags for workers to use to find your task.",
            required=True,
        )
        group.add_argument(
            "--assignment-duration-seconds",
            dest="assignment_duration_seconds",
            help="Time that workers have to work on your task once accepted.",
            default=30 * 60,
            type=int,
        )
        group.add_argument(
            "--allowed-concurrent",
            dest="allowed_concurrent",
            help="Maximum units a worker is allowed to work on at once. (0 is infinite)",
            default=0,
            type=int,
        )
        group.add_argument(
            "--maximum-units-per-worker",
            dest="maximum_units_per_worker",
            help=(
                "Maximum tasks of this task name that a worker can work on across all "
                "tasks that share this task_name. (0 is infinite)"
            ),
            default=0,
            type=int,
        )
        group.add_argument(
            "--task-name",
            dest="task_name",
            help="Grouping to launch this task run under, none defaults to the blueprint type",
        )

        return

    @classmethod
    def get_mock_params(cls) -> str:
        """Returns a param string with default / mock arguments to use for testing"""
        return (
            '--task-title "Mock Task Title" '
            "--task-reward 0.3 "
            "--task-tags mock,task,tags "
            '--task-description "This is a test description" '
            "--num-assignments 1 "
        )
