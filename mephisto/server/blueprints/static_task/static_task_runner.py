#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskRunner

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment


class StaticTaskRunner(TaskRunner):
    """Task runner for a static task"""

    # TODO implement. Going to get frontend working first

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self.tracked_tasks: Dict[str, "Assignment"] = {}

    def run_assignment(self, assignment: "Assignment"):
        """
        Mock runners will pass the agents for the given assignment
        all of the required messages to finish a task.
        """
        self.tracked_tasks[assignment.db_id] = assignment
        time.sleep(0.3)
        for unit in assignment.get_units():
            agent = unit.get_assigned_agent()
            assert agent is not None, "Task was not fully assigned"
            # TODO add some observations?
            # TODO add some acts?
            # TODO improve when MockAgents are more capable
            agent.mark_done()
        del self.tracked_tasks[assignment.db_id]

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """Mock task types don't have extra options"""
        return {}

    def cleanup_assignment(self, assignment: "Assignment"):
        """No cleanup required yet for ending mock runs"""
        pass
