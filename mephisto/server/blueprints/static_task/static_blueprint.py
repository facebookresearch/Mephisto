#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.server.blueprints.static_task.static_agent_state import StaticAgentState
from mephisto.server.blueprints.static_task.static_task_runner import StaticTaskRunner
from mephisto.server.blueprints.static_task.static_task_builder import StaticTaskBuilder

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment

BLUEPRINT_TYPE = 'static_task'

class StaticBlueprint(Blueprint):
    """Blueprint for a task that runs off of templated static HTML"""

    AgentStateClass: ClassVar[Type["AgentState"]] = StaticAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = StaticTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = StaticTaskRunner
    supported_architects: ClassVar[List[str]] = ["mock"]
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """Will need to specify the HTML file!"""
        # TODO fill in eventually
        return {}
