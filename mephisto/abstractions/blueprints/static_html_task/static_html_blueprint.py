#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    StaticBlueprint,
    StaticBlueprintArgs,
    SharedStaticTaskState,
)
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.abstractions.blueprint import Blueprint
from mephisto.abstractions.blueprints.static_html_task.static_html_task_builder import (
    StaticHTMLTaskBuilder,
)
from mephisto.operations.registry import register_mephisto_abstraction

import os
import time
import csv
import types

from typing import ClassVar, List, Type, Any, Dict, Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import (
        AgentState,
        TaskRunner,
        TaskBuilder,
        SharedTaskState,
    )
    from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
        SharedStaticTaskState,
    )
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.agent import OnboardingAgent
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.unit import Unit

BLUEPRINT_TYPE_STATIC_HTML = "static_task"


@dataclass
class StaticHTMLBlueprintArgs(StaticBlueprintArgs):
    """
    Adds required options for StaticBlueprints.
    task_source points to the file intending to be deployed for this task
    data_csv has the data to be deployed for this task.
    """

    _blueprint_type: str = BLUEPRINT_TYPE_STATIC_HTML
    _group: str = field(
        default="StaticBlueprint",
        metadata={
            "help": (
                "Tasks launched from static blueprints need a "
                "source html file to display to workers, as well as a csv "
                "containing values that will be inserted into templates in "
                "the html. "
            )
        },
    )
    task_source: str = field(
        default=MISSING,
        metadata={
            "help": "Path to source HTML file for the task being run",
            "required": True,
        },
    )
    preview_source: Optional[str] = field(
        default=MISSING,
        metadata={"help": "Optional path to source HTML file to preview the task"},
    )
    onboarding_source: Optional[str] = field(
        default=MISSING,
        metadata={"help": "Optional path to source HTML file to onboarding the task"},
    )


@register_mephisto_abstraction()
class StaticHTMLBlueprint(StaticBlueprint):
    """Blueprint for a task that runs off of a built react javascript bundle"""

    TaskBuilderClass = StaticHTMLTaskBuilder
    ArgsClass = StaticHTMLBlueprintArgs
    BLUEPRINT_TYPE = BLUEPRINT_TYPE_STATIC_HTML

    def __init__(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
    ):
        assert isinstance(
            shared_state, SharedStaticTaskState
        ), "Cannot initialize with a non-static state"
        super().__init__(task_run, args, shared_state)
        self.html_file = os.path.expanduser(args.blueprint.task_source)
        if not os.path.exists(self.html_file):
            raise FileNotFoundError(
                f"Specified html file {self.html_file} was not found from {os.getcwd()}"
            )

        self.onboarding_html_file = args.blueprint.get("onboarding_source", None)
        if self.onboarding_html_file is not None:
            self.onboarding_html_file = os.path.expanduser(self.onboarding_html_file)
            if not os.path.exists(self.onboarding_html_file):
                raise FileNotFoundError(
                    f"Specified onboarding html file {self.onboarding_html_file} was not found from {os.getcwd()}"
                )

        task_file_name = os.path.basename(self.html_file)
        for entry in self._initialization_data_dicts:
            entry["html"] = task_file_name

    @classmethod
    def assert_task_args(cls, args: DictConfig, shared_state: "SharedTaskState"):
        """Ensure that the data can be properly loaded"""
        Blueprint.assert_task_args(args, shared_state)
        blue_args = args.blueprint
        assert isinstance(
            shared_state, SharedStaticTaskState
        ), "Cannot assert args on a non-static state"
        if isinstance(shared_state.static_task_data, types.GeneratorType):
            raise AssertionError("You can't launch an HTML static task on a generator")
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
            assert (
                len([w for w in shared_state.static_task_data]) > 0
            ), "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, json-L, or a list of tasks"
            )

        if blue_args.get("onboarding_qualification", None) is not None:
            assert blue_args.get("onboarding_source", None) is not None, (
                "Must use onboarding html with an onboarding qualification to "
                "use onboarding."
            )
            assert shared_state.validate_onboarding is not None, (
                "Must use an onboarding validation function to use onboarding "
                "with static tasks."
            )
