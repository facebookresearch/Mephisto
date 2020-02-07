#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.data_model.assignment import InitializationData
from mephisto.server.blueprints.mock.mock_agent_state import MockAgentState
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner
from mephisto.server.blueprints.mock.mock_task_builder import MockTaskBuilder

import os
import time

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "mock"


class MockBlueprint(Blueprint):
    """Mock of a task type, for use in testing"""

    AgentStateClass: ClassVar[Type["AgentState"]] = MockAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = MockTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = MockTaskRunner
    supported_architects: ClassVar[List[str]] = ["mock"]
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        MockBlueprints specify a count of assignments, as there 
        is no real data being sent
        """
        super(MockBlueprint, cls).add_args_to_group(group)
        group.description = "MockBlueprint arguments"
        group.add_argument(
            "--num-assignments",
            dest="num_assignments",
            help="Number of assignments to launch",
            type=int,
            required=True,
        )
        return

    def get_initialization_data(self) -> Iterable[InitializationData]:
        """
        Return the number of empty assignments specified in --num-assignments
        """
        return [self.TaskRunnerClass.get_mock_assignment_data() for i in range(self.opts['num_assignments'])]
