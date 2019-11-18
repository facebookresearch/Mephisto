#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.task_runner import TaskRunner
from mephisto.server.blueprints.mock.mock_agent_state import MockAgentState

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.agent_state import AgentState
    from mephisto.data_model.assignment import Assignment

class MockTaskRunner(TaskRunner):
    """Mock of a task type, for use in testing"""

    AgentStateClass: ClassVar[Type['AgentState']] = MockAgentState
    supported_architects: ClassVar[List[str]] = ['mock']

    BUILT_FILE = 'done.built'
    BUILT_MESSAGE = 'built!'

    def __init__(self, task_run: 'TaskRun', opts: Any):
        self.opts = opts
        self.tracked_tasks: Dict[str, 'Assignment'] = {}

    def build_in_dir(self, task_run: 'TaskRun', build_dir: str):
        """Mock task types don't build anything (yet)"""
        with open(os.path.join(build_dir, self.BUILT_FILE), 'w+') as built_file:
            built_file.write(self.BUILT_MESSAGE)

    def run_assignment(self, assignment: 'Assignment'):
        """
        Mock runners will pass the agents for the given assignment
        all of the required messages to finish a task.
        """
        self.tracked_tasks[assignment.db_id] = assignment
        time.sleep(0.3)
        for unit in assignment.get_units():
            agent = unit.get_assigned_agent()
            assert agent is not None, 'Task was not fully assigned'
            # TODO add some observations?
            # TODO add some acts?
            # TODO improve when MockAgents are more capable
            agent.mark_done()
        del self.tracked_tasks[assignment.db_id]

    @staticmethod
    def task_dir_is_valid(task_dir: str) -> bool:
        """Mocks are always valid"""
        return True

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """Mock task types don't have extra options"""
        return {}

    def cleanup_assignment(self, assignment: 'Assignment'):
        """No cleanup required yet for ending mock runs"""
        pass
