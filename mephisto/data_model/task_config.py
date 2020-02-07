#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from shutil import copytree
from typing import List, Any, TYPE_CHECKING
import argparse
import shlex

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup


class TaskConfig:
    """
    Class that queries and sets important task information
    that is required to launch for all providers and task types
    """

    # TODO TaskConfigs should probably be immutable, and could ideally separate
    # the options that come from different parts of the ecosystem
    def __init__(self, task_run: "TaskRun"):
        self.db = task_run.db
        BlueprintClass = task_run.get_blueprint()
        CrowdProviderClass = task_run.get_provider()
        param_string = task_run.param_string

        parser = argparse.ArgumentParser()
        blueprint_group = parser.add_argument_group("blueprint")
        BlueprintClass.add_args_to_group(blueprint_group)
        provider_group = parser.add_argument_group("crowd_provider")
        CrowdProviderClass.add_args_to_group(provider_group)
        task_group = parser.add_argument_group("task_config")
        TaskConfig.add_args_to_group(task_group)

        try:
            arg_namespace, _unknown = parser.parse_known_args(shlex.split(param_string))
        except SystemExit:
            raise Exception("Argparse broke - must fix")
        args = vars(arg_namespace)
        self.args = args
        self.task_title: str = args["task_title"]
        self.task_description: str = args["task_description"]
        self.task_reward: float = args["task_reward"]
        self.task_tags: List[str] = [s.strip() for s in args["task_tags"].split(",")]
        self.assignment_duration_in_seconds: int = args["assignment_duration_seconds"]
        self.qualifications: List[Any] = []

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
