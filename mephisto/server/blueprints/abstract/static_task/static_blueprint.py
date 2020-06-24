#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint, OnboardingRequired
from mephisto.data_model.assignment import InitializationData
from mephisto.server.blueprints.abstract.static_task.static_agent_state import (
    StaticAgentState,
)
from mephisto.server.blueprints.abstract.static_task.static_task_runner import (
    StaticTaskRunner,
)
from mephisto.server.blueprints.abstract.static_task.empty_task_builder import (
    EmptyStaticTaskBuilder,
)
from mephisto.core.registry import register_mephisto_abstraction

import os
import time
import csv
import json

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import (
        AgentState,
        TaskRunner,
        TaskBuilder,
        OnboardingAgent,
    )
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.worker import Worker
    from argparse import _ArgumentGroup as ArgumentGroup


class StaticBlueprint(Blueprint, OnboardingRequired):
    """
    Abstract blueprint for a task that runs without any extensive backend. 
    These are generally one-off tasks sending data to the frontend and then
    awaiting a response.
    """

    AgentStateClass: ClassVar[Type["AgentState"]] = StaticAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = StaticAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = EmptyStaticTaskBuilder
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = StaticTaskRunner
    supported_architects: ClassVar[List[str]] = ["mock"]  # TODO update

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self.init_onboarding_config(task_run, opts)

        self._initialization_data_dicts: List[Dict[str, Any]] = []
        if opts.get("data_csv") is not None:
            csv_file = os.path.expanduser(opts["data_csv"])
            with open(csv_file, "r", encoding="utf-8-sig") as csv_fp:
                csv_reader = csv.reader(csv_fp)
                headers = next(csv_reader)
                for row in csv_reader:
                    row_data = {}
                    for i, col in enumerate(row):
                        row_data[headers[i]] = col
                    self._initialization_data_dicts.append(row_data)
        elif opts.get("data_json") is not None:
            json_file = os.path.expanduser(opts["data_json"])
            with open(json_file, "r", encoding="utf-8-sig") as json_fp:
                json_data = json.loads(json_fp)
            for jd in json_data:
                self._initialization_data_dicts.append(jd)
        elif opts.get("data_jsonl") is not None:
            jsonl_file = os.path.expanduser(opts["data_jsonl"])
            with open(jsonl_file, "r", encoding="utf-8-sig") as jsonl_fp:
                line = jsonl_fp.readline()
                while (line):
                    j = json.loads(line)
                    self._initialization_data_dicts.append(j)
                    line = jsonl_fp.readline()
        elif opts.get("static_task_data") is not None:
            self._initialization_data_dicts = opts["static_task_data"]
        else:
            # instantiating a version of the blueprint, but not necessarily needing the data
            pass

    @classmethod
    def assert_task_args(cls, opts: Any) -> None:
        """Ensure that the data can be properly loaded"""
        if opts.get("data_csv") is not None:
            csv_file = os.path.expanduser(opts["data_csv"])
            assert os.path.exists(
                csv_file
            ), f"Provided csv file {csv_file} doesn't exist"
        elif opts.get("data_json") is not None:
            json_file = os.path.expanduser(opts["data_json"])
            assert os.path.exists(
                json_file
            ), f"Provided JSON file {json_file} doesn't exist"
        elif opts.get("data_jsonl") is not None:
            jsonl_file = os.path.expanduser(opts["data_jsonl"])
            assert os.path.exists(
                jsonl_file
            ), f"Provided JSON-L file {jsonl_file} doesn't exist"
        elif opts.get("static_task_data") is not None:
            assert (
                len(opts.get("static_task_data")) > 0
            ), "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, json-L, or a list of tasks"
            )

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        task_source points to the file intending to be deployed for this task
        data_csv has the data to be deployed for this task.
        """
        super(StaticBlueprint, cls).add_args_to_group(group)
        OnboardingRequired.add_args_to_group(group)

        group.description = """
            StaticBlueprint: Static tasks need to be launched 
            using some source frontend (set by the child), and 
            the data to parse and render in the frontend templates.
        """
        group.add_argument(
            "--extra-source-dir",
            dest="extra_source_dir",
            help=(
                "Optional path to sources that the HTML may "
                "refer to (such as images/video/css/scripts)"
            ),
            required=False,
        )
        group.add_argument(
            "--data-json",
            dest="data_json",
            help="Path to JSON file containing task data",
            required=False,
        )
        group.add_argument(
            "--data-jsonl",
            dest="data_jsonl",
            help="Path to JSON-L file containing task data",
            required=False,
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
        group.add_argument(
            "--subtasks-per-unit",
            dest="subtasks_per_unit",
            type=int,
            default=5,
            help="number of subtasks/comparisons to do per unit",
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

    def validate_onboarding(
        self, worker: "Worker", onboarding_agent: "OnboardingAgent"
    ) -> bool:
        """
        Check the incoming onboarding data and evaluate if the worker
        has passed the qualification or not. Return True if the worker
        has qualified.
        """
        data = onboarding_agent.state.get_data()
        return data["outputs"].get("success", True)
