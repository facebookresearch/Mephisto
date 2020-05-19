#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint, OnboardingRequired
from mephisto.data_model.assignment import InitializationData
from mephisto.server.blueprints.parlai_chat.parlai_chat_agent_state import (
    ParlAIChatAgentState,
)
from mephisto.server.blueprints.parlai_chat.parlai_chat_task_runner import (
    ParlAIChatTaskRunner,
)
from mephisto.server.blueprints.parlai_chat.parlai_chat_task_builder import (
    ParlAIChatTaskBuilder,
)
from mephisto.core.registry import register_mephisto_abstraction

import os
import time
import csv
import sys

from importlib import import_module

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "parlai_chat"


MISSING_SOMETHING_TEXT = (
    "<h1>"
    "You didn't specify a --task-description-file and also didn't override the "
    "frontend `TaskPreviewView` (if this is a preview) or the `TaskDescription` "
    "component (if this is in-task)."
    "</h1>"
)


@register_mephisto_abstraction()
class ParlAIChatBlueprint(Blueprint, OnboardingRequired):
    """Blueprint for a task that runs a parlai chat """

    AgentStateClass: ClassVar[Type["AgentState"]] = ParlAIChatAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = ParlAIChatAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = ParlAIChatTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = ParlAIChatTaskRunner
    supported_architects: ClassVar[List[str]] = [
        "mock",
        "heroku",
        "local",
    ]  # TODO update?
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self._initialization_data_dicts: List[Dict[str, Any]] = []
        self.init_onboarding_config(task_run, opts)
        
        if opts.get("context_csv") is not None:
            csv_file = os.path.expanduser(opts["context_csv"])
            with open(csv_file, "r", encoding="utf-8-sig") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data: Dict[str, Any] = {}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        elif opts.get("num_conversations") is not None:
            self._initialization_data_dicts = [{}] * opts.get("num_conversations")
        else:
            # TODO(#95) handle JSON and python dicts directly
            raise NotImplementedError(
                "Parsing static tasks directly from dicts or JSON is not supported yet"
            )

        world_file_path = os.path.expanduser(self.opts["world_file"])
        world_module_path = world_file_path[:-3]
        sys.path.append(world_module_path)
        world_module_name = os.path.basename(world_file_path)[:-3]
        world_module = import_module(world_module_name)
        self.world_module = world_module
        assert hasattr(world_module, "make_world")
        assert hasattr(world_module, "get_world_params")
        self.agent_count = world_module.get_world_params()[  # type: ignore
            "agent_count"
        ]

        self.full_task_description = MISSING_SOMETHING_TEXT
        if opts.get("task_description_file") is not None:
            full_path = os.path.expanduser(opts.get("task_description_file"))
            assert os.path.exists(
                full_path
            ), f"Target task description path {full_path} doesn't exist"
            with open(full_path, "r") as description_fp:
                self.full_task_description = description_fp.read()

    @classmethod
    def assert_task_args(cls, args: Any) -> None:
        """Ensure that arguments are properly configured to launch this task"""
        # assert world file is valid
        world_file_path = os.path.expanduser(args["world_file"])
        world_module_path = world_file_path[:-3]
        assert os.path.exists(
            world_file_path
        ), f"Provided world path {world_file_path} doesn't exist"
        sys.path.append(world_module_path)
        world_module_name = os.path.basename(world_file_path)[:-3]
        world_module = import_module(world_module_name)
        assert hasattr(
            world_module, "make_world"
        ), "Provided world file has no `make_world` method"
        assert hasattr(
            world_module, "get_world_params"
        ), "Provided world file has no `get_world_params` method"

        # assert some method for determining quantity of conversations
        if args.get("context_csv") is not None:
            raise AssertionError(
                "Specifying task quantity via context csv is not yet implemented"
            )
        elif args.get("num_conversations") is not None:
            assert (
                args.get("num_conversations") > 0
            ), "Must have at least one conversation"
        else:
            raise AssertionError(
                "Must specify one of --context-csv or --num-conversations"
            )

        if args.get("custom_source_bundle") is not None:
            custom_source_file_path = os.path.expanduser(args["custom_source_bundle"])
            assert os.path.exists(
                custom_source_file_path
            ), f"Provided custom source doesn't exist at {custom_source_file_path}"

        if args.get("preview_source") is not None:
            preview_source_file = os.path.expanduser(args["preview_source"])
            assert os.path.exists(
                preview_source_file
            ), f"Provided preview source doesn't exist at {preview_source_file}"

        if args.get("extra_source_dir") is not None:
            extra_source_dir = os.path.expanduser(args["extra_source_dir"])
            assert os.path.exists(
                extra_source_dir
            ), f"Provided extra resource dir doesn't exist at {extra_source_dir}"

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        task_source points to the file intending to be deployed for this task
        context_csv has the data to be deployed for this task.
        """
        super(ParlAIChatBlueprint, cls).add_args_to_group(group)
        OnboardingRequired.add_args_to_group(group)
        group.description = """
            ParlAIChatBlueprint: Tasks launched from static blueprints need a
            source html file to display to workers, as well as a csv
            containing values that will be inserted into templates in
            the html.
        """
        group.add_argument(
            "--world-file",
            dest="world_file",
            help="Path to file containing ParlAI world",
            required=True,
        )
        group.add_argument(
            "--preview-source",
            dest="preview_source",
            help="Optional path to source HTML file to preview the task",
        )
        group.add_argument(
            "--task-description-file",
            dest="task_description_file",
            help=(
                "Path to file for the extended description of the task. "
                "Required if not providing a custom source bundle."
            ),
        )
        group.add_argument(
            "--custom-source-bundle",
            dest="custom_source_bundle",
            help="Optional path to a fully custom frontend bundle",
        )
        group.add_argument(
            "--extra-source-dir",
            dest="extra_source_dir",
            help=(
                "Optional path to sources that the frontend may "
                "refer to (such as images/video/css/scripts)"
            ),
        )
        group.add_argument(
            "--context-csv",
            dest="context_csv",
            help="Optional path to csv containing task context",
        )
        group.add_argument(
            "--num-conversations",
            dest="num_conversations",
            help="Optional count of conversations to have if no context provided",
            type=int,
        )
        return

    def get_frontend_args(self) -> Dict[str, Any]:
        """
        Specifies what options within a task_config should be fowarded 
        to the client for use by the task's frontend
        """
        return {
            "task_description": self.full_task_description,
            "frame_height": 650,
            "chat_title": self.opts["task_title"],
            "has_preview": self.opts.get("preview_source") is not None,
            "block_mobile": True,
            "frontend_task_opts": self.opts.get("task_opts", {}),
        }

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
