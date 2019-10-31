#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from shutil import copytree
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun


class TaskConfig:
    """
    Class that queries and sets important task information
    that is required to launch for all providers and task types
    """

    def __init__(self, task_run: "TaskRun"):
        self.db = task_run.db
        # TODO implement with TaskParams, some of these
        # should be removed or populated customly
        # based on the task type and provider
        self.task_title = "test"
        self.task_description = "test"
        self.task_reward = 0.3
        self.task_tags = ["test", "test", "test"]
        self.assignment_duration_in_seconds = 60 * 30
        self.qualifications: List[Any] = []
