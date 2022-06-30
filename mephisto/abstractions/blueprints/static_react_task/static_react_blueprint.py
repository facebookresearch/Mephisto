#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from dataclasses import dataclass, field
from omegaconf import MISSING
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    StaticBlueprint,
    StaticBlueprintArgs,
    SharedStaticTaskState,
)
from mephisto.abstractions.blueprints.static_react_task.static_react_task_builder import (
    StaticReactTaskBuilder,
)
from mephisto.operations.registry import register_mephisto_abstraction

import os

from typing import ClassVar, Type, Any, Dict, TYPE_CHECKING
from mephisto.abstractions.blueprint import (
    SharedTaskState,
)

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import (
        TaskBuilder,
    )
    from omegaconf import DictConfig

BLUEPRINT_TYPE_STATIC_REACT = "static_react_task"


@dataclass
class StaticReactBlueprintArgs(StaticBlueprintArgs):
    """
    StaticReactBlueprint: Tasks launched from static blueprints need
    a prebuilt javascript bundle containing the task. We suggest building
    with our provided useMephistoTask hook.
    """

    _blueprint_type: str = BLUEPRINT_TYPE_STATIC_REACT
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


@register_mephisto_abstraction()
class StaticReactBlueprint(StaticBlueprint):
    """Blueprint for a task that runs off of a built react javascript bundle"""

    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = StaticReactTaskBuilder
    ArgsClass = StaticReactBlueprintArgs
    BLUEPRINT_TYPE = BLUEPRINT_TYPE_STATIC_REACT

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        assert isinstance(
            shared_state, SharedStaticTaskState
        ), "Cannot initialize with a non-static state"
        super().__init__(task_run, args, shared_state)
        self.task_run = task_run
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
        assert isinstance(
            shared_state, SharedStaticTaskState
        ), "Cannot assert args on a non-static state"
        super().assert_task_args(args, shared_state)

        found_task_source = args.blueprint.task_source
        assert (
            found_task_source is not None
        ), "Must provide a path to a javascript bundle in `task_source`"

        found_task_path = os.path.expanduser(found_task_source)
        assert os.path.exists(
            found_task_path
        ), f"Provided task source {found_task_path} does not exist."

        link_task_source = args.blueprint.link_task_source
        current_architect = args.architect._architect_type
        allowed_architects = ["local"]
        assert link_task_source == False or (
            link_task_source == True and current_architect in allowed_architects
        ), f"`link_task_source={link_task_source}` is not compatible with architect type: {args.architect._architect_type}. Please check your task configuration."

    def get_frontend_args(self) -> Dict[str, Any]:
        """
        Specifies what options within a task_config should be fowarded
        to the client for use by the task's frontend
        """
        # Start with standard task configuration arguments
        frontend_task_config = super().get_frontend_args()
        shared_state = self.shared_state
        assert isinstance(
            shared_state, SharedTaskState
        ), "Must use SharedTaskState with StaticReactBlueprint"
        task_name = self.task_run.to_dict()["task_name"]
        db = LocalMephistoDB()
        mephisto_data_browser = MephistoDataBrowser(db)
        metadata = mephisto_data_browser.get_metadata_from_task_name(task_name)
        front_end_task_config_with_metadata = super().update_task_config_with_metadata(
            metadata, frontend_task_config
        )
        # Use overrides provided downstream
        front_end_task_config_with_metadata.update(self.frontend_task_config)
        return front_end_task_config_with_metadata
