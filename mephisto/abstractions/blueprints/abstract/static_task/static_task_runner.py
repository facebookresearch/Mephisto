#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskRunner

import os
import time
import threading

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.assignment import InitializationData
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from mephisto.abstractions.blueprint import SharedTaskState
    from omegaconf import DictConfig


class StaticTaskRunner(TaskRunner):
    """
    Task runner for a static task

    Static tasks always assume single unit assignments,
    as only one person can work on them at a time
    """

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        self.is_concurrent = False
        self.assignment_duration_in_seconds = (
            task_run.get_task_args().assignment_duration_in_seconds
        )

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

    def run_onboarding(self, agent: "OnboardingAgent"):
        """
        Static onboarding flows exactly like a regular task, waiting for
        the submit to come through
        """
        agent.await_submit(self.assignment_duration_in_seconds)

    def cleanup_onboarding(self, agent: "OnboardingAgent"):
        """Nothing to clean up in a static onboarding"""
        return

    def run_unit(self, unit: "Unit", agent: "Agent") -> None:
        """
        Static runners will get the task data, send it to the user, then
        wait for the agent to act (the data to be completed)
        """
        agent.await_submit(self.assignment_duration_in_seconds)

    def cleanup_unit(self, unit: "Unit") -> None:
        """There is currently no cleanup associated with killing an incomplete task"""
        return
