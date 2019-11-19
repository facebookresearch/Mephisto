#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.server.blueprints.mock.mock_agent_state import MockAgentState
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner
from mephisto.server.blueprints.mock.mock_task_builder import MockTaskBuilder

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment


class MockBlueprint(Blueprint):
    """Mock of a task type, for use in testing"""

    AgentStateClass: ClassVar[Type["AgentState"]] = MockAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = MockTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = MockTaskRunner
    supported_architects: ClassVar[List[str]] = ["mock"]

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """Mock task types don't have extra options"""
        return {}
