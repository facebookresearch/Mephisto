#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from typing import ClassVar, List, Dict, Any, Type, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    # from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.agent_state import AgentState
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment


class TaskRunner(ABC):
    """
    Class to manage running a task of a specific type. Includes
    building the dependencies to a directory to be deployed to
    the server, and spawning threads that manage the process of
    passing agents through a task.
    """

    AgentStateClass: ClassVar[Type["AgentState"]]
    supported_architects: ClassVar[List[str]]

    def __init__(self, task_run: "TaskRun", opts: Any):
        self.opts = opts
        # TODO populate some kind of local state for tasks that are being run
        # by this runner from the database.

    @abstractmethod
    def build_in_dir(self, task_run: "TaskRun", build_dir: str) -> None:
        """
        Build the server for the given task run into the provided directory
        """
        raise NotImplementedError()

    @abstractmethod
    def run_assignment(self, assignment: "Assignment"):
        """
        Handle setup for any resources required to get this assignment running.
        This will be run in a background thread, and should be tolerant to
        being interrupted by cleanup_assignment.
        """
        # TODO send some messages to the agents?
        raise NotImplementedError()

    @abstractmethod
    def cleanup_assignment(self, assignment: "Assignment"):
        """
        Handle ensuring resources for a given assignment are cleaned up following
        a disconnect or other crash event

        Does not need to be implemented if the run_assignment method is
        already error catching and handles its own cleanup
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def task_dir_is_valid(task_dir: str) -> bool:
        """
        Check the given task dir, and assert that the contents
        would be runnable with this task runner.
        """
        raise NotImplementedError()

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """
        Defines options that are potentially usable for this task type.
        """
        # TODO update to a format that will be rendererable on the frontend.
        # These are options that are available to the task
        return {}
