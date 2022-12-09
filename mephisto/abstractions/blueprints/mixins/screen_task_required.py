#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import (
    Optional,
    Dict,
    Any,
    Union,
    Iterable,
    Callable,
    Tuple,
    cast,
    Generator,
    TYPE_CHECKING,
)

import types
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
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.worker import Worker
    from argparse import _ArgumentGroup as ArgumentGroup


@dataclass
class ScreenTaskRequiredArgs:
    passed_qualification_name: str = field(
        default=MISSING,
        metadata={
            "help": (
                "Specify the name of a qualification used to designate "
                "workers who have passed screening."
            )
        },
    )
    max_screening_units: int = field(
        default=MISSING,
        metadata={
            "help": (
                "The maximum number of screening units that can be launched "
                "with this batch, specified to limit the number of validations "
                "you may need to pay out for."
            )
        },
    )
    use_screening_task: bool = field(
        default=False,
        metadata={"help": ("Whether or not to use a screening task in this run.")},
    )


ScreenUnitDataGenerator = Generator[Dict[str, Any], None, None]


def blank_generator():
    while True:
        yield {}


@dataclass
class ScreenTaskSharedState:
    screening_data_factory: Tuple[bool, ScreenUnitDataGenerator] = field(
        default_factory=lambda: blank_generator(),
        metadata={
            "help": (
                "Either a generator that will create task data dicts to "
                "be used as the `shared` field in InitializationData, or "
                "the bool False to use real data in screening tasks."
            ),
            "Type": "Tuple[bool, ScreenUnitDataGenerator]",
            "default": "Generator that creates empty data forever",
        },
    )


class ScreenTaskRequired(BlueprintMixin):
    """
    Compositional class for blueprints that may have a first task to
    qualify workers who have never attempted the task before
    """

    shared_state: "SharedTaskState"
    ArgsMixin = ScreenTaskRequiredArgs
    SharedStateMixin = ScreenTaskSharedState

    def init_mixin_config(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
    ) -> None:
        assert isinstance(
            shared_state, ScreenTaskSharedState
        ), "Must use ScreenTaskSharedState with ScreenTaskRequired blueprint"
        return self.init_screening_config(task_run, args, shared_state)

    def init_screening_config(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "ScreenTaskSharedState",
    ) -> None:
        self.use_screening_task = args.blueprint.get("use_screening_task", False)
        if not self.use_screening_task:
            return
        assert (
            args.blueprint.get("use_golds") is not True
        ), "Gold units currently cannot be used with screening units"
        # Runs that are using a qualification task should be able to assign
        # a specially generated unit to unqualified workers
        self.passed_qualification_name = args.blueprint.passed_qualification_name
        self.failed_qualification_name = args.blueprint.block_qualification
        self.screening_data_factory: Tuple[
            bool, ScreenUnitDataGenerator
        ] = shared_state.screening_data_factory
        self.screening_units_launched = 0
        self.screening_unit_cap = args.blueprint.max_screening_units

        find_or_create_qualification(task_run.db, self.passed_qualification_name)
        find_or_create_qualification(task_run.db, self.failed_qualification_name)

    @classmethod
    def assert_mixin_args(cls, args: "DictConfig", shared_state: "SharedTaskState"):
        use_screening_task = args.blueprint.get("use_screening_task", False)
        assert isinstance(
            shared_state, ScreenTaskSharedState
        ), "Must use ScreenTaskSharedState with ScreenTaskRequired blueprint"
        if not use_screening_task:
            return
        passed_qualification_name = args.blueprint.passed_qualification_name
        failed_qualification_name = args.blueprint.block_qualification
        assert args.task.allowed_concurrent == 1, (
            "Can only run this task type with one allowed concurrent unit at a time per worker, to ensure "
            "screening before moving into real units."
        )
        assert (
            passed_qualification_name is not None
        ), "Must supply an passed_qualification_name in Hydra args to use a qualification task"
        assert (
            failed_qualification_name is not None
        ), "Must supply an block_qualification in Hydra args to use a qualification task"
        assert hasattr(shared_state, "screening_data_factory"), (
            "You must supply a screening_data_factory generator in your SharedTaskState to use "
            "screening units, or False if you can screen on any tasks."
        )
        max_screening_units = args.blueprint.max_screening_units
        assert max_screening_units is not None, (
            "You must supply a blueprint.max_screening_units argument to set the maximum number of "
            "additional units you will pay out for the purpose of screening new workers. Note that you "
            "do pay for screening units, they are just like any other units."
        )
        screening_data_factory = shared_state.screening_data_factory
        if screening_data_factory is not False:
            assert isinstance(screening_data_factory, types.GeneratorType), (
                "Must provide a generator function to SharedTaskState.screening_data_factory if "
                "you want to generate screening tasks on the fly, or False if you can screen on any task "
            )
            assert (
                max_screening_units > 0
            ), "max_screening_units must be greater than zero if using a screening_data_factory"
        else:
            assert (
                max_screening_units == 0
            ), "max_screening_units must be zero if not using a screening_data_factory"

    def worker_needs_screening(self, worker: "Worker") -> bool:
        """Workers that are able to access the task (not blocked) but are not passed need qualification"""
        return worker.get_granted_qualification(self.passed_qualification_name) is None

    def should_generate_unit(self) -> bool:
        return self.screening_data_factory is not False

    def get_screening_unit_data(self) -> Optional[Dict[str, Any]]:
        try:
            if self.screening_units_launched >= self.screening_unit_cap:
                return None  # Exceeded the cap on these units
            else:
                data = next(
                    cast(
                        Generator[Dict[str, Any], None, None],
                        self.screening_data_factory,
                    )
                )
                self.screening_units_launched += 1
                return data
        except StopIteration:
            return None  # No screening units left...

    @classmethod
    def create_validation_function(
        cls, args: "DictConfig", screen_unit: Callable[["Unit"], bool]
    ):
        """
        Takes in a validator function to determine if validation units are
        passable, and returns a `on_unit_submitted` function to be used
        in the SharedTaskState
        """
        passed_qualification_name = args.blueprint.passed_qualification_name
        failed_qualification_name = args.blueprint.block_qualification

        def _wrapped_validate(unit):
            if args.blueprint.max_screening_units > 0 and unit.unit_index >= 0:
                return  # We only run validation on the validatable units
            agent = unit.get_assigned_agent()
            if agent is None:
                return  # Cannot validate a unit with no agent
            if (
                args.blueprint.max_screening_units == 0
                and agent.get_worker().is_qualified(passed_qualification_name)
            ):
                return  # Do not run validation if screening with regular tasks and worker is already qualified
            validation_result = screen_unit(unit)
            if validation_result is True:
                agent.get_worker().grant_qualification(passed_qualification_name)
            elif validation_result is False:
                agent.get_worker().grant_qualification(failed_qualification_name)

        return _wrapped_validate

    @classmethod
    def get_mixin_qualifications(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ):
        """Creates the relevant task qualifications for this task"""
        passed_qualification_name = args.blueprint.passed_qualification_name
        failed_qualification_name = args.blueprint.block_qualification
        return [
            make_qualification_dict(
                failed_qualification_name,
                QUAL_NOT_EXIST,
                None,
            )
        ]
