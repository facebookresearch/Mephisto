#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from typing import (
    Dict,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from omegaconf import DictConfig

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class TaskBuilder(ABC):
    """
    Class to manage building a task of a specific type in a directory
    that will be used to deploy that task.
    """

    def __init__(self, task_run: "TaskRun", args: "DictConfig"):
        self.args = args
        self.task_run = task_run

    def __new__(cls, task_run: "TaskRun", args: "DictConfig") -> "TaskBuilder":
        """Get the correct TaskBuilder for this task run"""
        from mephisto.operations.registry import get_blueprint_from_type

        if cls == TaskBuilder:
            # We are trying to construct an TaskBuilder, find what type to use and
            # create that instead
            correct_class = get_blueprint_from_type(task_run.task_type).TaskBuilderClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    @abstractmethod
    def build_in_dir(self, build_dir: str) -> None:
        """
        Build the server for the given task run into the provided directory
        """
        raise NotImplementedError()
