#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskBuilder

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup


class MockTaskBuilder(TaskBuilder):
    """Builder for a mock task, for use in testing"""

    BUILT_FILE = "done.built"
    BUILT_MESSAGE = "built!"

    def build_in_dir(self, build_dir: str):
        """Mock tasks don't really build anything (yet)"""
        with open(os.path.join(build_dir, self.BUILT_FILE), "w+") as built_file:
            built_file.write(self.BUILT_MESSAGE)

    @staticmethod
    def task_dir_is_valid(task_dir: str) -> bool:
        """Mocks are always valid, we don't have any special resources"""
        return True

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        MockTaskBuilders don't have any arguments (yet)
        """
        super(MockTaskBuilder, cls).add_args_to_group(group)
        return
