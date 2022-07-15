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
from dataclasses import dataclass, field

from mephisto.data_model.assignment import InitializationData
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_agent_state import (
    ParlAIChatAgentState,
)
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_task_runner import (
    ParlAIChatTaskRunner,
)
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_task_builder import (
    ParlAIChatTaskBuilder,
)
from mephisto.operations.registry import register_mephisto_abstraction
from omegaconf import DictConfig, MISSING

import os
import csv
import sys
import json

from importlib import import_module

from typing import ClassVar, List, Type, Any, Dict, Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.agent import OnboardingAgent
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import AgentState, TaskRunner, TaskBuilder


BLUEPRINT_TYPE_PARLAI_CHAT = "parlai_chat"


MISSING_SOMETHING_TEXT = (
    "<h1>"
    "You didn't specify a task_description_file and also didn't override the "
    "frontend `TaskPreviewView` (if this is a preview) or the `TaskDescription` "
    "component (if this is in-task)."
    "</h1>"
)


@dataclass
class SharedParlAITaskState(OnboardingSharedState, SharedTaskState):
    frontend_task_opts: Dict[str, Any] = field(default_factory=dict)
    world_opt: Dict[str, Any] = field(default_factory=dict)
    onboarding_world_opt: Dict[str, Any] = field(default_factory=dict)
    world_module: Optional[Any] = None


@dataclass
class ParlAIChatBlueprintArgs(OnboardingRequiredArgs, BlueprintArgs):
    _blueprint_type: str = BLUEPRINT_TYPE_PARLAI_CHAT
    _group: str = field(
        default="ParlAIChatBlueprint",
        metadata={
            "help": """
                Tasks launched from ParlAI blueprints require the number of
                conversations (either an int or task data for each convo), as
                well as a world to initialize for connecting workers.
            """
        },
    )
    world_file: str = field(
        default=MISSING,
        metadata={"help": "Path to file containing ParlAI world", "required": True},
    )
    preview_source: str = field(
        default=MISSING,
        metadata={"help": "Optional path to source HTML file to preview the task"},
    )
    task_description_file: str = field(
        default=MISSING,
        metadata={
            "help": (
                "Path to file for the extended description of the task. "
                "Required if not providing a custom source bundle."
            )
        },
    )
    custom_source_bundle: str = field(
        default=MISSING,
        metadata={"help": "Optional path to a fully custom frontend bundle"},
    )
    custom_source_dir: str = field(
        default=MISSING,
        metadata={"help": "Optional path to a directory containing custom js code"},
    )
    extra_source_dir: str = field(
        default=MISSING,
        metadata={
            "help": (
                "Optional path to sources that the frontend may "
                "refer to (such as images/video/css/scripts)"
            )
        },
    )
    context_csv: str = field(
        default=MISSING,
        metadata={"help": "Optional path to csv containing task context"},
    )
    context_jsonl: str = field(
        default=MISSING,
        metadata={"help": "Optional path to jsonl file containing task context"},
    )
    num_conversations: int = field(
        default=MISSING,
        metadata={
            "help": "Optional count of conversations to have if no context provided"
        },
    )


@register_mephisto_abstraction()
class ParlAIChatBlueprint(OnboardingRequired, Blueprint):
    """Blueprint for a task that runs a parlai chat"""

    AgentStateClass: ClassVar[Type["AgentState"]] = ParlAIChatAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = ParlAIChatAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = ParlAIChatTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = ParlAIChatTaskRunner
    ArgsClass = ParlAIChatBlueprintArgs
    SharedStateClass = SharedParlAITaskState
    BLUEPRINT_TYPE = BLUEPRINT_TYPE_PARLAI_CHAT

    def __init__(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedParlAITaskState",
    ):
        super().__init__(task_run, args, shared_state)
        self._initialization_data_dicts: List[Dict[str, Any]] = []
        if args.blueprint.get("context_csv", None) is not None:
            csv_file = os.path.expanduser(args.blueprint.context_csv)
            with open(csv_file, "r", encoding="utf-8-sig") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data: Dict[str, Any] = {}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        elif args.blueprint.get("context_jsonl", None) is not None:
            jsonl_file = os.path.expanduser(args.blueprint.context_jsonl)
            with open(jsonl_file, "r", encoding="utf-8-sig") as jsonl_fp:
                line = jsonl_fp.readline()
                while line:
                    j = json.loads(line)
                    self._initialization_data_dicts.append(j)
                    line = jsonl_fp.readline()
        elif args.blueprint.get("num_conversations", None) is not None:
            self._initialization_data_dicts = [{}] * args.blueprint.num_conversations
        else:
            raise NotImplementedError(
                "Parsing parlai tasks directly from dicts or JSON is not supported yet"
            )

        if shared_state.world_module is None:
            world_file_path = os.path.expanduser(args.blueprint.world_file)
            world_module_dir = os.path.dirname(world_file_path)
            sys.path.append(world_module_dir)
            world_module_name = os.path.basename(world_file_path)[:-3]
            world_module = import_module(world_module_name)
        else:
            world_module = shared_state.world_module
        self.world_module = world_module
        assert hasattr(world_module, "make_world")
        assert hasattr(world_module, "get_world_params")
        self.agent_count = world_module.get_world_params()[  # type: ignore
            "agent_count"
        ]

        self.full_task_description = MISSING_SOMETHING_TEXT
        if args.blueprint.get("task_description_file", None) is not None:
            full_path = os.path.expanduser(args.blueprint.task_description_file)
            assert os.path.exists(
                full_path
            ), f"Target task description path {full_path} doesn't exist"
            with open(full_path, "r") as description_fp:
                self.full_task_description = description_fp.read()
        self.full_preview_description = MISSING_SOMETHING_TEXT
        if args.blueprint.get("preview_source", None) is not None:
            preview_source_file = os.path.expanduser(args.blueprint.preview_source)
            assert os.path.exists(
                preview_source_file
            ), f"Target preview source path {preview_source_file} doesn't exist"
            with open(preview_source_file, "r") as description_fp:
                self.full_preview_description = description_fp.read()

    @classmethod
    def assert_task_args(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Ensure that arguments are properly configured to launch this task"""
        # Find world module
        assert isinstance(
            shared_state, SharedParlAITaskState
        ), "Must use SharedParlAITaskState with ParlAIChatBlueprint"
        world_module = shared_state.world_module
        if world_module is None:
            world_file_path = os.path.expanduser(args.blueprint.world_file)
            world_module_dir = os.path.dirname(world_file_path)
            assert os.path.exists(
                world_file_path
            ), f"Provided world path {world_file_path} doesn't exist"
            sys.path.append(world_module_dir)
            world_module_name = os.path.basename(world_file_path)[:-3]
            world_module = import_module(world_module_name)
        # assert world file is valid
        assert hasattr(
            world_module, "make_world"
        ), "Provided world file has no `make_world` method"
        assert hasattr(
            world_module, "get_world_params"
        ), "Provided world file has no `get_world_params` method"

        # assert some method for determining quantity of conversations
        if args.blueprint.get("context_csv", None) is not None:
            csv_file = os.path.expanduser(args.blueprint.context_csv)
            assert os.path.exists(
                csv_file
            ), f"Target context_csv path {csv_file} doesn't exist"
        elif args.blueprint.get("context_jsonl", None) is not None:
            jsonl_file = os.path.expanduser(args.blueprint.context_jsonl)
            assert os.path.exists(
                jsonl_file
            ), f"Target context_jsonl path {jsonl_file} doesn't exist"
        elif args.blueprint.get("num_conversations", None) is not None:
            assert (
                args.blueprint.num_conversations > 0
            ), "Must have at least one conversation"
        else:
            raise AssertionError(
                "Must specify one of --context-csv, --context-jsonl or --num-conversations"
            )

        if args.blueprint.get("custom_source_bundle", None) is not None:
            custom_source_file_path = os.path.expanduser(
                args.blueprint.custom_source_bundle
            )
            assert os.path.exists(
                custom_source_file_path
            ), f"Provided custom bundle doesn't exist at {custom_source_file_path}"

        if args.blueprint.get("custom_source_dir", None) is not None:
            custom_source_dir_path = os.path.expanduser(
                args.blueprint.custom_source_dir
            )
            assert os.path.exists(
                custom_source_dir_path
            ), f"Provided custom source dir doesn't exist at {custom_source_dir_path}"

        if args.blueprint.get("preview_source", None) is not None:
            preview_source_file = os.path.expanduser(args.blueprint.preview_source)
            assert os.path.exists(
                preview_source_file
            ), f"Provided preview source doesn't exist at {preview_source_file}"

        if args.blueprint.get("extra_source_dir", None) is not None:
            extra_source_dir = os.path.expanduser(args.blueprint.extra_source_dir)
            assert os.path.exists(
                extra_source_dir
            ), f"Provided extra resource dir doesn't exist at {extra_source_dir}"

    def get_frontend_args(self) -> Dict[str, Any]:
        """
        Specifies what options within a task_config should be fowarded
        to the client for use by the task's frontend
        """
        # Start with standard task configuration arguments
        frontend_task_config = super().get_frontend_args()
        shared_state = self.shared_state
        assert isinstance(
            shared_state, SharedParlAITaskState
        ), "Must use SharedParlAITaskState with ParlAIChatBlueprint"
        # Add ParlAI standards
        frontend_task_config.update(
            {
                "task_description": self.full_task_description,
                "preview_html": self.full_preview_description,
                "frame_height": 650,
                "chat_title": self.args.task.task_title,
                "has_preview": self.args.blueprint.get("preview_source", None)
                is not None,
                "block_mobile": True,
                "frontend_task_opts": shared_state.frontend_task_opts,
            }
        )
        # Use overrides provided downstream
        frontend_task_config.update(self.frontend_task_config)
        return frontend_task_config

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        return [
            InitializationData(shared=d, unit_data=[{}] * self.agent_count)
            for d in self._initialization_data_dicts
        ]

    def validate_onboarding(
        self, worker: "Worker", onboarding_agent: "OnboardingAgent"
    ) -> bool:
        if hasattr(self.world_module, "validate_onboarding"):
            return self.world_module.validate_onboarding(  # type: ignore
                onboarding_agent.state.get_data()
            )
        return True
