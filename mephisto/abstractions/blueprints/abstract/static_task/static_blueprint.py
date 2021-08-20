#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import (
    Blueprint,
    OnboardingRequired,
    BlueprintArgs,
    SharedTaskState,
)
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.data_model.assignment import InitializationData
from mephisto.abstractions.blueprints.abstract.static_task.static_agent_state import (
    StaticAgentState,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_task_runner import (
    StaticTaskRunner,
)
from mephisto.abstractions.blueprints.abstract.static_task.empty_task_builder import (
    EmptyStaticTaskBuilder,
)
from mephisto.operations.registry import register_mephisto_abstraction

import os
import time
import csv
import json
import types

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import (
        AgentState,
        TaskRunner,
        TaskBuilder,
        OnboardingAgent,
    )
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.worker import Worker
    from argparse import _ArgumentGroup as ArgumentGroup


BLUEPRINT_TYPE = "abstract_static"


@dataclass
class SharedStaticTaskState(SharedTaskState):
    static_task_data: Iterable[Any] = field(default_factory=list)


@dataclass
class StaticBlueprintArgs(BlueprintArgs):
    _blueprint_type: str = BLUEPRINT_TYPE
    _group: str = field(
        default="StaticBlueprint",
        metadata={
            "help": (
                "Abstract Static Blueprints should not be launched manually, but "
                "include all tasks with units containing just one input and output "
                "of arbitrary data, with no live component. "
            )
        },
    )
    units_per_assignment: int = field(
        default=1, metadata={"help": "How many workers you want to do each assignment"}
    )
    extra_source_dir: str = field(
        default=MISSING,
        metadata={
            "help": (
                "Optional path to sources that the HTML may "
                "refer to (such as images/video/css/scripts)"
            )
        },
    )
    data_json: str = field(
        default=MISSING, metadata={"help": "Path to JSON file containing task data"}
    )
    data_jsonl: str = field(
        default=MISSING, metadata={"help": "Path to JSON-L file containing task data"}
    )
    data_csv: str = field(
        default=MISSING, metadata={"help": "Path to csv file containing task data"}
    )


class StaticBlueprint(Blueprint, OnboardingRequired):
    """
    Abstract blueprint for a task that runs without any extensive backend.
    These are generally one-off tasks sending data to the frontend and then
    awaiting a response.
    """

    AgentStateClass: ClassVar[Type["AgentState"]] = StaticAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = StaticAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = EmptyStaticTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = StaticTaskRunner
    ArgsClass: ClassVar[Type["BlueprintArgs"]] = StaticBlueprintArgs
    supported_architects: ClassVar[List[str]] = ["mock"]  # TODO update
    SharedStateClass = SharedStaticTaskState

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        self.init_onboarding_config(task_run, args, shared_state)

        # Originally just a list of dicts, but can also be a generator of dicts
        self._initialization_data_dicts: Iterable[Dict[str, Any]] = []
        blue_args = args.blueprint
        if blue_args.get("data_csv", None) is not None:
            csv_file = os.path.expanduser(blue_args.data_csv)
            with open(csv_file, "r", encoding="utf-8-sig") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data = {}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        elif blue_args.get("data_json", None) is not None:
            json_file = os.path.expanduser(blue_args.data_json)
            with open(json_file, "r", encoding="utf-8-sig") as json_fp:
                json_data = json.loads(json_fp)
            for jd in json_data:
                self._initialization_data_dicts.append(jd)
        elif blue_args.get("data_jsonl", None) is not None:
            jsonl_file = os.path.expanduser(blue_args.data_jsonl)
            with open(jsonl_file, "r", encoding="utf-8-sig") as jsonl_fp:
                line = jsonl_fp.readline()
                while line:
                    j = json.loads(line)
                    self._initialization_data_dicts.append(j)
                    line = jsonl_fp.readline()
        elif shared_state.static_task_data is not None:
            self._initialization_data_dicts = shared_state.static_task_data
        else:
            # instantiating a version of the blueprint, but not necessarily needing the data
            pass

    @classmethod
    def assert_task_args(cls, args: DictConfig, shared_state: "SharedTaskState"):
        """Ensure that the data can be properly loaded"""
        blue_args = args.blueprint
        if blue_args.get("data_csv", None) is not None:
            csv_file = os.path.expanduser(blue_args.data_csv)
            assert os.path.exists(
                csv_file
            ), f"Provided csv file {csv_file} doesn't exist"
        elif blue_args.get("data_json", None) is not None:
            json_file = os.path.expanduser(blue_args.data_json)
            assert os.path.exists(
                json_file
            ), f"Provided JSON file {json_file} doesn't exist"
        elif blue_args.get("data_jsonl", None) is not None:
            jsonl_file = os.path.expanduser(blue_args.data_jsonl)
            assert os.path.exists(
                jsonl_file
            ), f"Provided JSON-L file {jsonl_file} doesn't exist"
        elif shared_state.static_task_data is not None:
            if isinstance(shared_state.static_task_data, types.GeneratorType):
                # TODO can we check something about this?
                pass
            else:
                assert (
                    len(shared_state.static_task_data) > 0
                ), "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, json-L, or a list of tasks"
            )

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        if isinstance(self._initialization_data_dicts, types.GeneratorType):

            def data_generator() -> Iterable["InitializationData"]:
                for item in self._initialization_data_dicts:
                    yield InitializationData(
                        shared=item,
                        unit_data=[{}] * self.args.blueprint.units_per_assignment,
                    )

            return data_generator()
        else:
            return [
                InitializationData(
                    shared=d, unit_data=[{}] * self.args.blueprint.units_per_assignment
                )
                for d in self._initialization_data_dicts
            ]

    def validate_onboarding(
        self, worker: "Worker", onboarding_agent: "OnboardingAgent"
    ) -> bool:
        """
        Check the incoming onboarding data and evaluate if the worker
        has passed the qualification or not. Return True if the worker
        has qualified.
        """
        data = onboarding_agent.state.get_data()
        return self.shared_state.validate_onboarding(
            data
        )  # data["outputs"].get("success", True)
