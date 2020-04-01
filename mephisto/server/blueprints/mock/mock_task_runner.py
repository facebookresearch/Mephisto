#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskRunner
from mephisto.data_model.assignment import InitializationData
from mephisto.core.argparse_parser import str2bool

import os
import time

from typing import ClassVar, List, Type, Any, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment, Unit
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from argparse import _ArgumentGroup as ArgumentGroup


class MockTaskRunner(TaskRunner):
    """Mock of a task runner, for use in testing"""

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self.timeout = opts["timeout_time"]
        self.tracked_tasks: Dict[str, Union["Assignment", "Unit"]] = {}
        self.is_concurrent = opts.get("is_concurrent", True)
        print(f"Blueprint is concurrent: {self.is_concurrent}, {opts}")

    @staticmethod
    def get_mock_assignment_data() -> InitializationData:
        return InitializationData(shared={}, unit_data=[{}, {}])

    @staticmethod
    def get_data_for_assignment(assignment: "Assignment") -> InitializationData:
        """
        Mock tasks have no data unless given during testing
        """
        return MockTaskRunner.get_mock_assignment_data()

    def get_init_data_for_agent(self, agent: "Agent") -> Dict[str, Any]:
        """
        Return the data for an agent already assigned to a particular unit
        """
        # TODO implement
        pass

    def run_onboarding(self, onboarding_agent: "OnboardingAgent"):
        """
        Mock runners simply wait for an act to come in with whether 
        or not onboarding is complete
        """
        packet = onboarding_agent.act(timeout=self.timeout)
        onboarding_agent.did_submit.set()
        onboarding_agent.mark_done()

    def run_unit(self, unit: "Unit", agent: "Agent"):
        """
        Mock runners will pass the agents for the given assignment
        all of the required messages to finish a task.
        """
        self.tracked_tasks[unit.db_id] = unit
        time.sleep(0.3)
        assigned_agent = unit.get_assigned_agent()
        assert assigned_agent is not None, "No agent was assigned"
        assert (
            assigned_agent.db_id == agent.db_id
        ), "Task was not given to assigned agent"
        packet = agent.act(timeout=self.timeout)
        if packet is not None:
            agent.observe(packet)
        agent.did_submit.set()
        agent.mark_done()
        del self.tracked_tasks[unit.db_id]

    def run_assignment(self, assignment: "Assignment", agents: List["Agent"]):
        """
        Mock runners will pass the agents for the given assignment
        all of the required messages to finish a task.
        """
        self.tracked_tasks[assignment.db_id] = assignment
        agent_dict = {a.db_id: a for a in agents}
        time.sleep(0.3)
        for unit in assignment.get_units():
            assigned_agent = unit.get_assigned_agent()
            assert assigned_agent is not None, "Task was not fully assigned"
            agent = agent_dict.get(assigned_agent.db_id)
            assert agent is not None, "Task was not launched with assigned agents"
            packet = agent.act(timeout=self.timeout)
            if packet is not None:
                agent.observe(packet)
            agent.did_submit.set()
            agent.mark_done()
        del self.tracked_tasks[assignment.db_id]

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        MockTaskRunners don't have any arguments (yet)
        """
        super(MockTaskRunner, cls).add_args_to_group(group)

        group.description = """
            MockArchitect: Mock Task Runners can specify a timeout to
            make the task actually take time to run.
        """
        group.add_argument(
            "--timeout-time",
            dest="timeout_time",
            help="Whether acts in the run assignment should have a timeout",
            default=0,
            type=int,
        )
        group.add_argument(
            "--is-concurrent",
            dest="is_concurrent",
            help="Whether to run this mock task as a concurrent task or not",
            default=True,
            type=str2bool,
        )
        return

    def cleanup_assignment(self, assignment: "Assignment"):
        """No cleanup required yet for ending mock runs"""
        pass

    def cleanup_unit(self, unit: "Unit"):
        """No cleanup required yet for ending mock runs"""
        pass

    def cleanup_onboarding(self, onboarding_agent: "OnboardingAgent"):
        """No cleanup required yet for ending onboarding in mocks"""
        pass
