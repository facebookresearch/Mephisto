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
    Generator,
    TYPE_CHECKING,
)

import types
import random
from mephisto.abstractions.blueprint import BlueprintMixin, AgentState
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.data_model.qualification import make_qualification_dict, QUAL_NOT_EXIST
from mephisto.operations.utils import find_or_create_qualification
from mephisto.operations.task_launcher import GOLD_UNIT_INDEX


if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.worker import Worker
    from argparse import _ArgumentGroup as ArgumentGroup

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


@dataclass
class UseGoldUnitArgs:
    gold_qualification_base: str = field(
        default=MISSING,
        metadata={
            "help": ("Basename for a qualification that tracks gold completion rates")
        },
    )
    use_golds: bool = field(
        default=False,
        metadata={"help": ("Whether or not to use gold tasks in this run.")},
    )
    min_golds: int = field(
        default=1,
        metadata={
            "help": (
                "Minimum golds a worker needs to complete before " "getting real units."
            )
        },
    )
    max_incorrect_golds: int = field(
        default=0,
        metadata={
            "help": (
                "Maximum number of golds a worker can get incorrect before being disqualified"
            )
        },
    )


GoldFactory = Callable[["Worker"], Dict[str, Any]]


def get_gold_factory(golds: List[Dict[str, Any]]) -> GoldFactory:
    """
    Returns a gold factory that can be used to distribute golds to workers
    Usage of golds only persists within a single TaskRun, so golds may repeat
    on future task runs.
    """
    worker_golds_map: Dict[str, List[int]] = {}
    num_golds = len(golds)

    def get_gold_for_worker(worker: "Worker"):
        if (
            worker.db_id not in worker_gold_maps
            or len(worker_golds_map[worker.db_id]) == 0
        ):
            # create a list of gold indices a worker hasn't done
            worker_golds_map[worker.db_id] = [x for x in range(num_golds)]
        # select a random gold index from what remains
        rg = worker_golds_map[worker.db_id]
        selected_idx = random.randInt(0, len(rg))
        rg[selected_idx], rg[-1] = rg[-1], rg[selected_idx]
        gold_idx = rg.pop()
        return golds[gold_idx]

    return get_gold_for_worker


def worker_needs_gold(
    units_completed: int, num_correct: int, num_incorrect: int, min_golds: int
) -> bool:
    """
    Return a bool of whether or not a worker needs to be shown a gold unit in the current slot.
    Generally we show a lot of of golds to begin with, (up until min_golds), and then scale down.
    """


def worker_qualifies(
    units_completed: int, num_correct: int, num_incorrect: int, max_incorrect_golds: int
) -> bool:
    """
    Return a bool of whether or not a worker is qualified to continue working on these tasks.
    """


@dataclass
class GoldUnitSharedState:
    get_gold_for_worker: GoldFactory = field(
        default_factory=lambda: get_gold_factory([{}])
    )
    worker_needs_gold: Callable[[int, int, int, int], bool] = field(
        default_factory=lambda: worker_needs_gold,
    )
    worker_qualifies: Callable[[int, int, int, int], bool] = field(
        default_factory=lambda: worker_qualifies,
    )


class UseGoldUnit(BlueprintMixin):
    """
    Compositional class for blueprints that want to inject gold units
    into worker queues.

    # TODO add support for adding gold subunits
    """

    ArgsMixin = UseGoldUnitArgs
    SharedStateMixin = GoldUnitSharedState

    def init_mixin_config(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "GoldUnitSharedState",
    ) -> None:
        return self.init_gold_config(task_run, args, shared_state)

    def init_screening_config(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "GoldUnitSharedState",
    ) -> None:
        self.use_golds = args.blueprint.get("use_golds", False)
        if not self.use_golds:
            return

        # Runs using gold units need to keep track of the frequency and
        # usage of golds
        self.base_qual_name = args.blueprint.gold_qualification_base
        self.golds_correct_qual_name = f"{self.base_qual_name}-correct-golds"
        self.golds_failed_qual_name = f"{self.base_qual_name}-wrong-golds"
        self.disqualified_qual_name = f"{self.base_qual_name}-disqualified"
        self.task_count_qual_name = f"{self.base_qual_name}-completed-count"

        self.get_gold_for_worker = shared_state.get_gold_for_worker
        self.worker_needs_gold = shared_state.worker_needs_gold
        self.worker_qualifies = shared_state.worker_qualifies

        self.min_golds = args.blueprint.min_golds
        self.max_incorrect_golds = args.blueprint.max_incorrect_golds

        find_or_create_qualification(task_run.db, self.golds_correct_qual_name)
        find_or_create_qualification(task_run.db, self.golds_failed_qual_name)
        find_or_create_qualification(task_run.db, self.disqualified_qual_name)
        find_or_create_qualification(task_run.db, self.task_count_qual_name)

    @classmethod
    def assert_mixin_args(cls, args: "DictConfig", shared_state: "SharedTaskState"):
        use_screening_task = args.blueprint.get("use_screening_task", False)
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

    def get_current_qual_or_default(
        self, worker: "Worker", qual_name: str, default_val: Any = 0
    ) -> Any:
        """Return the qualification of this name for the worker, or the default value"""
        found_qual = worker.get_granted_qualification(qual_name)
        return default_val if found_qual is None else found_qual.value

    def get_completion_stats_for_worker(self, worker: "Worker") -> Tuple[int, int, int]:
        """Return the correct and incorrect gold counts, as well as the total count for a worker"""
        completed_units = self.get_current_qual_or_default(
            worker, self.task_count_qual_name
        )
        correct_golds = self.get_current_qual_or_default(
            worker, self.golds_correct_qual_name
        )
        incorrect_golds = self.get_current_qual_or_default(
            worker, self.golds_failed_qual_name
        )
        return completed_units, correct_units, incorrect_units

    def should_produce_gold_for_worker(self, worker: "Worker") -> bool:
        """Workers that can access the task should be evaluated to do a gold"""
        (
            completed_units,
            correct_units,
            incorrect_units,
        ) = self.get_completion_stats_for_worker(worker)
        return self.worker_needs_gold(
            completed_units, correct_units, incorrect_units, self.min_golds
        )

    def update_qualified_status(self, worker: "Worker") -> bool:
        """Workers qualification status may change after failing a unit"""
        (
            completed_units,
            correct_units,
            incorrect_units,
        ) = self.get_completion_stats_for_worker(worker)
        if not self.worker_qualifies(
            completed_units, correct_units, incorrect_units, self.max_incorrect_golds
        ):
            worker.grant_qualification(self.disqualified_qual_name)

    def get_gold_unit_data_for_worker(
        self, worker: "Worker"
    ) -> Optional[Dict[str, Any]]:
        try:
            return self.get_gold_for_worker(worker)
        except Exception as e:
            logger.warning(f"Could not generate gold for {worker} due to {e}")
            return None

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
            if unit.unit_index != GOLD_UNIT_INDEX:
                agent = unit.get_assigned_agent()
                if (
                    agent is not None
                    and agent.get_status() == AgentState.STATUS_COMPLETED
                ):
                    worker = agent.get_worker()
                    completed_units = self.get_current_qual_or_default(
                        worker, self.task_count_qual_name
                    )
                    worker.grant_qualification(
                        self.task_count_qual_name,
                        value=completed_units + 1,
                        skip_crowd=True,
                    )
                return  # We only run validation on the validatable units

            validation_result = screen_unit(unit)
            agent = unit.get_assigned_agent()
            worker = agent.get_worker()
            _, correct_units, incorrect_units = self.get_completion_stats_for_worker(
                worker
            )

            if validation_result is True:
                worker.grant_qualification(
                    self.golds_correct_qual_name, correct_units + 1, skip_crowd=True
                )
            elif validation_result is False:
                worker.grant_qualification(
                    self.golds_failed_qual_name, incorrect_units + 1, skip_crowd=True
                )

        return _wrapped_validate

    @classmethod
    def get_mixin_qualifications(cls, args: "DictConfig"):
        """Creates the relevant task qualifications for this task"""
        base_qual_name = args.blueprint.gold_qualification_base
        golds_failed_qual_name = f"{base_qual_name}-wrong-golds"
        return [
            make_qualification_dict(
                golds_failed_qual_name,
                QUAL_NOT_EXIST,
                None,
            )
        ]
