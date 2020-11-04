#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.assignment import InitializationData
from dataclasses import dataclass, field
from omegaconf import MISSING
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    StaticBlueprint,
    StaticBlueprintArgs,
)
from mephisto.abstractions.blueprints.static_react_task.static_react_task_builder import (
    StaticReactTaskBuilder,
)
from mephisto.operations.registry import register_mephisto_abstraction

import os
import time
import csv

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "static_react_task"


@dataclass
class StaticReactBlueprintArgs(StaticBlueprintArgs):
    """
    StaticReactBlueprint: Tasks launched from static blueprints need
    a prebuilt javascript bundle containing the task. We suggest building
    with our provided useMephistoTask hook.
    """

    _blueprint_type: str = BLUEPRINT_TYPE
    _group: str = field(
        default="StaticReactBlueprint",
        metadata={
            "help": """
                Tasks launched from static blueprints need
                a prebuilt javascript bundle containing the task. We suggest building
                with our provided useMephistoTask hook.
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


@register_mephisto_abstraction()
class StaticReactBlueprint(StaticBlueprint):
    """Blueprint for a task that runs off of a built react javascript bundle"""

    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = StaticReactTaskBuilder
    ArgsClass = StaticReactBlueprintArgs
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        self.js_bundle = os.path.expanduser(args.blueprint.task_source)
        if not os.path.exists(self.js_bundle):
            raise FileNotFoundError(
                f"Specified bundle file {self.js_bundle} was not found from {os.getcwd()}"
            )

    @classmethod
    def assert_task_args(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Ensure that static requirements are fulfilled, and source file exists"""
        super().assert_task_args(args, shared_state)

        found_task_source = args.blueprint.task_source
        assert (
            found_task_source is not None
        ), "Must provide a path to a javascript bundle in `task_source`"
        found_task_path = os.path.expanduser(found_task_source)
        assert os.path.exists(
            found_task_path
        ), f"Provided task source {found_task_path} does not exist."
