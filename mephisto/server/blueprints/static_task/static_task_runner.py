#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskRunner

import os
import time
import threading

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment, InitializationData
    from mephisto.data_model.agent import Agent


SYSTEM_SENDER = "mephisto"  # TODO pull from somewhere
TEST_TIMEOUT = 3000  # TODO pull this from the task run max completion time


class StaticTaskRunner(TaskRunner):
    """
    Task runner for a static task

    Static tasks always assume single unit assignments,
    as only one person can work on them at a time
    """

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)

    # TODO reconnects should get the same agent as was initially given

    def get_init_data_for_agent(self, agent: "Agent") -> Dict[str, Any]:
        """
        Return the data for an agent already assigned to a particular unit
        """
        init_state = agent.state.get_init_state()
        if init_state is not None:
            # reconnecting agent, give what we've got
            return init_state
        else:
            assignment = agent.get_unit().get_assignment()
            assignment_data = self.get_data_for_assignment(assignment)
            agent.state.set_init_state(assignment_data.shared)
            return assignment_data.shared

    def run_assignment(self, assignment: "Assignment", agents: List["Agent"]) -> None:
        """
        Static runners will get the task data, send it to the user, then
        wait for the agent to act (the data to be completed)
        """
        unit = assignment.get_units()[0]
        assert unit.unit_index == 0, "Static units should always have index 0"
        agent = agents[0]
        assert agent is not None, "Task was not fully assigned"

        agent_act = agent.act(timeout=TEST_TIMEOUT)
        agent.mark_done()
        del self.running_assignments[assignment.db_id]

    def cleanup_assignment(self, assignment: "Assignment") -> None:
        """Simply mark that the assignment is no longer being tracked"""
        if assignment.db_id in self.running_assignments:
            del self.running_assignments[assignment.db_id]
