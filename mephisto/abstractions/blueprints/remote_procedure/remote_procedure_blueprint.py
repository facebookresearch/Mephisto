#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import (
    Blueprint,
    BlueprintArgs,
    SharedTaskState,
)
from dataclasses import dataclass, field
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
    OnboardingSharedState,
    OnboardingRequiredArgs,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
    ScreenTaskRequiredArgs,
    ScreenTaskSharedState,
)
from mephisto.abstractions.blueprints.mixins.use_gold_unit import (
    UseGoldUnit,
    UseGoldUnitArgs,
    GoldUnitSharedState,
)
from mephisto.data_model.assignment import InitializationData
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_agent_state import (
    RemoteProcedureAgentState,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_task_runner import (
    RemoteProcedureTaskRunner,
)
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_task_builder import (
    RemoteProcedureTaskBuilder,
)
from mephisto.operations.registry import register_mephisto_abstraction
from omegaconf import DictConfig, MISSING

import os
import csv
import json
import types

from typing import (
    ClassVar,
    Callable,
    Type,
    Any,
    Dict,
    Iterable,
    Optional,
    Mapping,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import AgentState, TaskRunner, TaskBuilder

BLUEPRINT_TYPE_REMOTE_PROCEDURE = "remote_procedure"


@dataclass
class SharedRemoteProcedureTaskState(
    ScreenTaskSharedState, OnboardingSharedState, GoldUnitSharedState, SharedTaskState
):
    function_registry: Optional[
        Mapping[
            str,
            Callable[
                [str, Dict[str, Any], "RemoteProcedureAgentState"],
                Optional[Dict[str, Any]],
            ],
        ]
    ] = None
    static_task_data: Iterable[Any] = field(default_factory=list)


@dataclass
class RemoteProcedureBlueprintArgs(
    ScreenTaskRequiredArgs, OnboardingRequiredArgs, UseGoldUnitArgs, BlueprintArgs
):
    _blueprint_type: str = BLUEPRINT_TYPE_REMOTE_PROCEDURE
    _group: str = field(
        default="RemoteProcedureBlueprintArgs",
        metadata={
            "help": """
                Tasks launched from remote query blueprints need a
                source html file to display to workers, as well as a csv
                containing values that will be inserted into templates in
                the html.
            """
        },
    )
    task_source: str = field(
        default=MISSING,
        metadata={
            "help": "Path to file containing javascript bundle for the task",
            "required": True,
        },
    )
    link_task_source: bool = field(
        default=False,
        metadata={
            "help": """
                Symlinks the task_source file in your development folder to the
                one used for the server. Useful for local development so you can run
                a watch-based build for your task_source, allowing the UI code to
                update without having to restart the server each time.
            """,
            "required": False,
        },
    )
    units_per_assignment: int = field(
        default=1, metadata={"help": "How many workers you want to do each assignment"}
    )


@register_mephisto_abstraction()
class RemoteProcedureBlueprint(
    ScreenTaskRequired, OnboardingRequired, UseGoldUnit, Blueprint
):
    """Blueprint for a task that runs a parlai chat"""

    AgentStateClass: ClassVar[Type["AgentState"]] = RemoteProcedureAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = RemoteProcedureAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = RemoteProcedureTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = RemoteProcedureTaskRunner
    ArgsClass = RemoteProcedureBlueprintArgs
    SharedStateClass = SharedRemoteProcedureTaskState
    BLUEPRINT_TYPE = BLUEPRINT_TYPE_REMOTE_PROCEDURE

    def __init__(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedRemoteProcedureTaskState",
    ):
        super().__init__(task_run, args, shared_state)
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
                json_data = json.load(json_fp)
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
    def assert_task_args(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Ensure that arguments are properly configured to launch this task"""
        assert isinstance(
            shared_state, SharedRemoteProcedureTaskState
        ), "Must use SharedTaskState with RemoteProcedureBlueprint"
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
                    len([x for x in shared_state.static_task_data]) > 0
                ), "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, json-L, or a list of tasks"
            )
        assert shared_state.function_registry is not None, (
            "Must provide a valid function registry to use with the task, a mapping "
            "of function names to functions that take as input a string and an agent "
            "and return a string. "
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
