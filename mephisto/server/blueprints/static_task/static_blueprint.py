#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.server.blueprints.static_task.static_agent_state import StaticAgentState
from mephisto.server.blueprints.static_task.static_task_runner import StaticTaskRunner
from mephisto.server.blueprints.static_task.static_task_builder import StaticTaskBuilder

import os
import time

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "static_task"


class StaticBlueprint(Blueprint):
    """Blueprint for a task that runs off of templated static HTML"""

    AgentStateClass: ClassVar[Type["AgentState"]] = StaticAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = StaticTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = StaticTaskRunner
    supported_architects: ClassVar[List[str]] = ["mock"]  # TODO update
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        html_source points to the file intending to be deployed for this task
        data_csv has the data to be deployed for this task.
        """
        super(cls).add_args_to_group(group)

        group.description = """
            StaticBlueprint: Tasks launched from static blueprints need a
            source html file to display to workers, as well as a csv
            containing values that will be inserted into templates in
            the html.
        """
        group.add_argument(
            "--html-source",
            dest="html_source",
            help="Path to source HTML file for the task being run",
        )
        group.add_argument(
            "--data-csv", dest="data_csv", help="Path to csv file containing task data"
        )
        return
