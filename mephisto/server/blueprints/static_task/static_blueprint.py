#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.data_model.assignment import InitializationData
from mephisto.server.blueprints.static_task.static_agent_state import StaticAgentState
from mephisto.server.blueprints.static_task.static_task_runner import StaticTaskRunner
from mephisto.server.blueprints.static_task.static_task_builder import StaticTaskBuilder

import os
import time
import csv

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

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

    def __init__(self, task_run: "TaskRun", opts: Any):
        super(StaticBlueprint, self).__init__(task_run, opts)
        self._initialization_data_dicts: List[Dict[str, Any]] = []
        if opts.get("data_csv") is not None:
            csv_file = opts["data_csv"]
            with open(csv_file, "r") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data = {}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        else:
            # TODO handle JSON and python dicts directly
            raise NotImplementedError(
                "Parsing static tasks directly from dicts or JSON is not supported yet"
            )

        self.html_file = opts["html_source"]
        if not os.path.exists(self.html_file):
            raise FileNotFoundError(
                f"Specified html file {self.html_file} was not found from {os.getcwd()}"
            )

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        html_source points to the file intending to be deployed for this task
        data_csv has the data to be deployed for this task.
        """
        super(StaticBlueprint, cls).add_args_to_group(group)

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

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        return [
            InitializationData(shared=d, unit_data=[])
            for d in self._initialization_data_dicts
        ]
