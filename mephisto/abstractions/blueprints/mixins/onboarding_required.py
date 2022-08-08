#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import (
    Optional,
    Dict,
    List,
    Any,
    Callable,
    TYPE_CHECKING,
)

from mephisto.abstractions.blueprint import BlueprintMixin
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.data_model.qualification import QUAL_NOT_EXIST
from mephisto.utils.qualifications import (
    make_qualification_dict,
    find_or_create_qualification,
)

if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import SharedTaskState
    from mephisto.data_model.agent import OnboardingAgent
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.worker import Worker
    from argparse import _ArgumentGroup as ArgumentGroup


@dataclass
class OnboardingRequiredArgs:
    onboarding_qualification: str = field(
        default=MISSING,
        metadata={
            "help": (
                "Specify the name of a qualification used to block workers who fail onboarding, "
                "Empty will skip onboarding."
            )
        },
    )


@dataclass
class OnboardingSharedState:
    onboarding_data: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": (
                "Task data to send for the initialTaskData available in the frontend during onboarding."
            ),
            "type": "Dict[str, Any]",
            "default": "{}",
        },
    )
    validate_onboarding: Callable[[Any], bool] = field(
        default_factory=lambda: (lambda x: True),
        metadata={
            "help": (
                "Function that takes in the result task data (from AgentState.get_data()) "
                "and returns whether or not the onboarding was successful."
            ),
            "type": "Callable[[Any], bool]",
            "default": "Returns true always",
        },
    )


class OnboardingRequired(BlueprintMixin):
    """
    Compositional class for blueprints that may have an onboarding step
    """

    shared_state: "SharedTaskState"
    ArgsMixin = OnboardingRequiredArgs
    SharedStateMixin = OnboardingSharedState

    def init_mixin_config(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Method to initialize any required attributes to make this mixin function"""
        self.init_onboarding_config(task_run, args, shared_state)

    @classmethod
    def assert_mixin_args(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Method to validate the incoming args and throw if something won't work"""
        # Is there any validation that should be done on the onboarding qualification name?
        return

    @classmethod
    def get_mixin_qualifications(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> List[Dict[str, Any]]:
        """Method to provide any required qualifications to make this mixin function"""
        onboarding_qualification_name: Optional[str] = args.blueprint.get(
            "onboarding_qualification", None
        )
        if onboarding_qualification_name is None:
            # Not using an onboarding qualification
            return []
        return [
            # We need to keep a separate qualification for failed onboarding
            # to push to a crowd provider in order to prevent workers
            # who have failed from being shown our task
            make_qualification_dict(
                cls.get_failed_qual(onboarding_qualification_name),
                QUAL_NOT_EXIST,
                None,
            )
        ]

    @staticmethod
    def get_failed_qual(qual_name: str) -> str:
        """Returns the wrapper for a qualification to represent failing an onboarding"""
        return qual_name + "-failed"

    def init_onboarding_config(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        assert isinstance(
            shared_state, OnboardingSharedState
        ), f"Cannot init onboarding config with {shared_state}, need OnboardingSharedState"
        self.onboarding_qualification_name: Optional[str] = args.blueprint.get(
            "onboarding_qualification", None
        )
        self.onboarding_data = shared_state.onboarding_data
        self.use_onboarding = self.onboarding_qualification_name is not None
        self.onboarding_qualification_id = None
        if not self.use_onboarding:
            return
        onboarding_qualification_name = self.onboarding_qualification_name
        assert onboarding_qualification_name is not None

        db = task_run.db
        self.onboarding_qualification_id = find_or_create_qualification(
            db,
            onboarding_qualification_name,
        )
        self.onboarding_failed_name = self.get_failed_qual(
            onboarding_qualification_name
        )
        self.onboarding_failed_id = find_or_create_qualification(
            db, self.onboarding_failed_name
        )

    @classmethod
    def clear_onboarding(self, worker: "Worker", qualification_name: str):
        worker.revoke_qualification(qualification_name)
        if qualification_name is not None:
            worker.revoke_crowd_qualification(self.get_failed_qual(qualification_name))

    def get_onboarding_data(self, worker_id: str) -> Dict[str, Any]:
        """
        If the onboarding task on the frontend requires any specialized data, the blueprint
        should provide it for the user.

        As onboarding qualifies a worker for all tasks from this blueprint, this should
        generally be static data that can later be evaluated against.
        """
        return self.onboarding_data

    def validate_onboarding(
        self, worker: "Worker", onboarding_agent: "OnboardingAgent"
    ) -> bool:
        """
        Check the incoming onboarding data and evaluate if the worker
        has passed the qualification or not. Return True if the worker
        has qualified.

        By default we use the validate_onboarding provided in a run_task,
        and all onboarding tasks should allow run_task to specify additional
        or entirely override what's provided in a blueprint.
        """
        shared_state = self.shared_state
        assert isinstance(
            shared_state, OnboardingSharedState
        ), f"Cannot init onboarding config with {shared_state}, need OnboardingSharedState"
        data = onboarding_agent.state.get_data()
        return shared_state.validate_onboarding(data)
