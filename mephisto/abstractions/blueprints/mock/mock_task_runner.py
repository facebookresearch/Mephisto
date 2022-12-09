#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskRunner, SharedTaskState
from mephisto.data_model.assignment import InitializationData

import os
import time

from typing import ClassVar, List, Type, Any, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from argparse import _ArgumentGroup as ArgumentGroup
    from omegaconf import DictConfig


class MockTaskRunner(TaskRunner):
    """Mock of a task runner, for use in testing"""

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        self.timeout = args.blueprint.timeout_time
        self.tracked_tasks: Dict[str, Union["Assignment", "Unit"]] = {}
        self.is_concurrent = args.blueprint.get("is_concurrent", True)

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
        # TODO(#97) implement
        pass

    def run_onboarding(self, onboarding_agent: "OnboardingAgent"):
        """
        Mock runners simply wait for an act to come in with whether
        or not onboarding is complete
        """
        onboarding_agent.await_submit(self.timeout)

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
        packet = agent.get_live_update(timeout=self.timeout)
        if packet is not None:
            agent.observe(packet)
        agent.await_submit(self.args.task.submission_timeout)
        del self.tracked_tasks[unit.db_id]

    def run_assignment(self, assignment: "Assignment", agents: List["Agent"]):
        """
        Mock runners will pass the agents for the given assignment
        all of the required messages to finish a task.
        """
        self.tracked_tasks[assignment.db_id] = assignment
        agent_dict = {a.db_id: a for a in agents}
        time.sleep(0.3)
        agents = []
        for unit in assignment.get_units():
            assigned_agent = unit.get_assigned_agent()
            assert assigned_agent is not None, "Task was not fully assigned"
            agent = agent_dict.get(assigned_agent.db_id)
            assert agent is not None, "Task was not launched with assigned agents"
            agents.append(agent)
        for agent in agents:
            packet = agent.get_live_update(timeout=self.timeout)
            if packet is not None:
                agent.observe(packet)
        for agent in agents:
            agent.await_submit(self.args.task.submission_timeout)
        del self.tracked_tasks[assignment.db_id]

    def cleanup_assignment(self, assignment: "Assignment"):
        """No cleanup required yet for ending mock runs"""
        pass

    def cleanup_unit(self, unit: "Unit"):
        """No cleanup required yet for ending mock runs"""
        pass

    def cleanup_onboarding(self, onboarding_agent: "OnboardingAgent"):
        """No cleanup required yet for ending onboarding in mocks"""
        pass
