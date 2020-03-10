#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.data_model.assignment import InitializationData
from mephisto.server.blueprints.parlai_chat.parlai_chat_agent_state import ParlAIChatAgentState
from mephisto.server.blueprints.parlai_chat.parlai_chat_task_runner import ParlAIChatTaskRunner
from mephisto.server.blueprints.parlai_chat.parlai_chat_task_builder import ParlAIChatTaskBuilder

import os
import time
import csv
import sys

from importlib import import_module

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "parlai_chat"


class ParlAIChatBlueprint(Blueprint):
    """Blueprint for a task that runs a parlai chat """

    AgentStateClass: ClassVar[Type["AgentState"]] = ParlAIChatAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = ParlAIChatTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = ParlAIChatTaskRunner
    supported_architects: ClassVar[List[str]] = ["mock", "heroku", "local"]  # TODO update?
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    def __init__(self, task_run: "TaskRun", opts: Any):
        self._initialization_data_dicts: List[Dict[str, Any]] = []
        super().__init__(task_run, opts)
        if opts.get("context_csv") is not None:
            csv_file = os.path.expanduser(opts["context_csv"])
            with open(csv_file, "r", encoding="utf-8-sig") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data = {"html": task_file_name}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        elif opts.get("num_conversations") is not None:
            self._initialization_data_dicts = [{}] * opts.get("num_conversations")
        else:
            # TODO handle JSON and python dicts directly
            raise NotImplementedError(
                "Parsing static tasks directly from dicts or JSON is not supported yet"
            )

        world_file_path = os.path.expanduser(self.opts['world_file'])
        world_module_path = world_file_path[:-3]
        sys.path.append(world_module_path)
        world_module_name = os.path.basename(world_file_path)[:-3]
        world_module = import_module(world_module_name)
        # TODO assert this is a ParlAI world after figuring out 
        # how to get ParlAI to play with Poetry
        assert hasattr(world_module, "make_world")
        assert hasattr(world_module, "get_world_params")
        self.agent_count = world_module.get_world_params()['agent_count']

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        task_source points to the file intending to be deployed for this task
        context_csv has the data to be deployed for this task.
        """
        super(ParlAIChatBlueprint, cls).add_args_to_group(group)

        group.description = """
            ParlAIChatBlueprint: Tasks launched from static blueprints need a
            source html file to display to workers, as well as a csv
            containing values that will be inserted into templates in
            the html.
        """
        group.add_argument(
            '--world-file',
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
            "--custom-source-bundle",
            dest="custom_source-bundle",
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
            'task_description': "This is a test task description for rendering in a task!",
            'frame_height': 650,
            'chat_title': "Example Chat",
            'has_preview': self.opts.get('preview_source') is not None,
            'block_mobile': True,
        }

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        return [
            InitializationData(shared=d, unit_data=[{}] * self.agent_count)
            for d in self._initialization_data_dicts
        ]
