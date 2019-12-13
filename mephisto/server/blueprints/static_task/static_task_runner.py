#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskRunner
from mephisto.data_model.packet import Packet, PACKET_TYPE_INIT_DATA

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment

SYSTEM_SENDER = 'mephisto'  # TODO pull from somewhere
TEST_TIMEOUT = 3000  # TODO pull this from the task run max completion time

class StaticTaskRunner(TaskRunner):
    """
    Task runner for a static task

    Static tasks always assume single unit assignments,
    as only one person can work on them at a time
    """

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self.tracked_tasks: Dict[str, "Assignment"] = {}

    def get_data_for_assignment(self, assigment: "Assignment") -> List[Dict[str, Any]]:
        """
        Finds the right data to get for the given assignment.
        """
        return [
            {
                'character_name': "Loaded Character",
                'character_description': "I'm a character loaded from Mephisto!",
            }
        ]
        # TODO pull this directly from the assignment
        # return assignment.get_data_for_assignment()

    def run_assignment(self, assignment: "Assignment") -> None:
        """
        Static runners will get the task data, send it to the user, then
        wait for the agent to act (the data to be completed)
        """
        # Load the unit data
        assignment_data = self.get_data_for_assignment(assignment)
        assert len(assignment_data) == 1, "Should only be one unit for static tasks"
        unit_data = assignment_data[0]
        unit = assignment.get_units()[0]
        assert unit.unit_index == 0, "Static units should always have index 0"
        agent = unit.get_assigned_agent()
        assert agent is not None, "Task was not fully assigned"

        self.tracked_tasks[assignment.db_id] = assignment

        agent.observe(Packet(
            packet_type=PACKET_TYPE_INIT_DATA,
            sender_id=SYSTEM_SENDER,
            receiver_id=agent.db_id,
            data=unit_data,
        ))

        # TODO How do we handle disconnects on static tasks?
        agent_act = agent.act(timeout=TEST_TIMEOUT)
        agent.mark_done()
        del self.tracked_tasks[assignment.db_id]

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """Mock task types don't have extra options"""
        return {}

    def cleanup_assignment(self, assignment: "Assignment") -> None:
        """No cleanup required yet for ending mock runs"""
        del self.tracked_tasks[assignment.db_id]
