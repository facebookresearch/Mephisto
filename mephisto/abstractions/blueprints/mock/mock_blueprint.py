#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import (
    Blueprint,
    BlueprintArgs,
    SharedTaskState,
)
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
    OnboardingSharedState,
    OnboardingRequiredArgs,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
    ScreenTaskSharedState,
    ScreenTaskRequiredArgs,
)
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.data_model.assignment import InitializationData
from mephisto.abstractions.blueprints.mock.mock_agent_state import MockAgentState
from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner
from mephisto.abstractions.blueprints.mock.mock_task_builder import MockTaskBuilder
from mephisto.operations.registry import register_mephisto_abstraction

import os
import time

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from mephisto.data_model.agent import OnboardingAgent
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.unit import Unit

BLUEPRINT_TYPE_MOCK = "mock"


@dataclass
class MockBlueprintArgs(BlueprintArgs, OnboardingRequiredArgs, ScreenTaskRequiredArgs):
    _blueprint_type: str = BLUEPRINT_TYPE_MOCK
    num_assignments: int = field(
        default=MISSING,
        metadata={
            "help": "How many workers you want to do each assignment",
            "required": True,
        },
    )
    use_onboarding: bool = field(
        default=False, metadata={"help": "Whether onboarding should be required"}
    )
    timeout_time: int = field(
        default=0,
        metadata={"help": "Whether acts in the run assignment should have a timeout"},
    )
    is_concurrent: bool = field(
        default=True,
        metadata={"help": "Whether to run this mock task as a concurrent task or not"},
    )


# Mock tasks right now inherit all mixins, this way we can test them.
# In the future, we'll likely want to compose mock tasks for mixin testing
@dataclass
class MockSharedState(SharedTaskState, OnboardingSharedState, ScreenTaskSharedState):
    pass


@register_mephisto_abstraction()
class MockBlueprint(Blueprint, OnboardingRequired, ScreenTaskRequired):
    """Mock of a task type, for use in testing"""

    AgentStateClass: ClassVar[Type["AgentState"]] = MockAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = MockAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = MockTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = MockTaskRunner
    ArgsClass: ClassVar[Type["BlueprintArgs"]] = MockBlueprintArgs
    SharedStateClass: ClassVar[Type["SharedTaskState"]] = MockSharedState
    BLUEPRINT_TYPE = BLUEPRINT_TYPE_MOCK

    # making Mypy happy, these aren't used in a blueprint, only mixins
    ArgsMixin: ClassVar[Any]
    SharedStateMixin: ClassVar[Any]

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "MockSharedState"
    ):
        super().__init__(task_run, args, shared_state)

    def get_initialization_data(self) -> Iterable[InitializationData]:
        """
        Return the number of empty assignments specified in --num-assignments
        """
        return [
            MockTaskRunner.get_mock_assignment_data()
            for i in range(self.args.blueprint.num_assignments)
        ]

    def validate_onboarding(
        self, worker: "Worker", onboarding_agent: "OnboardingAgent"
    ) -> bool:
        """
        Onboarding validation for MockBlueprints just returns the 'should_pass' field
        """
        return onboarding_agent.state.get_data()["should_pass"]
