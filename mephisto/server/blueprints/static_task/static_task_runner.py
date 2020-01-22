#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskRunner

import os
import time
import threading

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

from recordclass import RecordClass

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.agent import Agent


class TrackedAssignment(RecordClass):
    assignment: "Assignment"
    thread: threading.Thread


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
        self.running_assignments: Dict[str, TrackedAssignment] = {}

    def get_data_for_assignment(self, assignment: "Assignment") -> List[Dict[str, Any]]:
        """
        Finds the right data to get for the given assignment.
        """
        return assignment.get_assignment_data()

    # TODO reconnects should get the same agent as was initially given

    def get_init_data_for_agent(self, agent: "Agent") -> Dict[str, Any]:
        """
        Return the data for an agent already assigned to a particular unit
        """
        init_state = agent.state.get_init_state()
        if init_state is not None:
            # reconnecting agent, give everything we've got
            # TODO implememnt
            return {}
        else:
            assignment = agent.get_unit().get_assignment()
            assignment_data = self.get_data_for_assignment(assignment)
            assert len(assignment_data) == 1, "Should only be one unit for static tasks"
            agent.state.set_init_state(assignment_data[0])
            self.launch_assignment(assignment, agent)
            return agent.state.get_init_state()

    def launch_assignment(self, assignment: "Assignment", agent: "Agent") -> None:
        """
        Launch a thread for the given assignment, if one doesn't
        exist already
        """
        if assignment.db_id in self.running_assignments:
            print(f"Assignment {assignment.db_id} is already running")
            return

        print(f"Assignment {assignment.db_id} is launching with {agent}")
        run_thread = threading.Thread(
            target=self.run_assignment, args=(assignment, [agent])
        )
        self.running_assignments[assignment.db_id] = TrackedAssignment(
            assignment=assignment, thread=run_thread
        )
        run_thread.start()
        return

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
