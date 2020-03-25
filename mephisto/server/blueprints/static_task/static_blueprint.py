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
        super().__init__(task_run, opts)
        self.html_file = os.path.expanduser(opts["task_source"])
        if not os.path.exists(self.html_file):
            raise FileNotFoundError(
                f"Specified html file {self.html_file} was not found from {os.getcwd()}"
            )

        self._initialization_data_dicts: List[Dict[str, Any]] = []
        task_file_name = os.path.basename(self.html_file)
        if opts.get("data_csv") is not None:
            csv_file = os.path.expanduser(opts["data_csv"])
            with open(csv_file, "r", encoding="utf-8-sig") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data = {"html": task_file_name}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        elif opts.get("data_json") is not None:
            # TODO handle JSON directly
            raise NotImplementedError(
                "Parsing static tasks directly from JSON is not supported yet"
            )
        elif opts.get("static_task_data") is not None:
            for entry in opts['static_task_data']:
                entry['html'] = task_file_name
            self._initialization_data_dicts = opts['static_task_data']
        else:
            # instantiating a version of the blueprint, but not necessarily needing the data
            pass

    @classmethod
    def assert_task_args(cls, opts: Any) -> None:
        """Ensure that the data can be properly loaded"""
        if opts.get("data_csv") is not None:
            csv_file = os.path.expanduser(opts["data_csv"])
            assert os.path.exists(csv_file), f"Provided csv file {csv_file} doesn't exist"
        elif opts.get("data_json") is not None:
            # TODO handle JSON directly
            raise NotImplementedError(
                "Parsing static tasks directly from JSON is not supported yet"
            )
        elif opts.get("static_task_data") is not None:
            assert len(opts.get("static_task_data")) > 0, "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, or a list of tasks"
            )

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        task_source points to the file intending to be deployed for this task
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
            "--task-source",
            dest="task_source",
            help="Path to source HTML file for the task being run",
            required=True,
        )
        group.add_argument(
            "--preview-source",
            dest="preview_source",
            help="Optional path to source HTML file to preview the task",
        )
        group.add_argument(
            "--extra-source-dir",
            dest="extra_source_dir",
            help=(
                "Optional path to sources that the HTML may "
                "refer to (such as images/video/css/scripts)"
            ),
        )
        group.add_argument(
            "--data-csv",
            dest="data_csv",
            help="Path to csv file containing task data",
            required=False,
        )
        group.add_argument(
            "--units-per-assignment",
            dest="units_per_assignment",
            help="How many workers you want to do each assignment",
            default=1,
            type=int,
        )
        return

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        return [
            InitializationData(
                shared=d, unit_data=[{}] * self.opts["units_per_assignment"]
            )
            for d in self._initialization_data_dicts
        ]
