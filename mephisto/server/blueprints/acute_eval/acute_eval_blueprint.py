#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import Blueprint
from mephisto.data_model.assignment import InitializationData
from mephisto.server.blueprints.acute_eval.acute_eval_agent_state import AcuteEvalAgentState
from mephisto.server.blueprints.acute_eval.acute_eval_runner import AcuteEvalRunner
from mephisto.server.blueprints.acute_eval.acute_eval_builder import AcuteEvalBuilder

import os
import time
import csv

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "acute_eval"


# WISH AcuteEval's blueprint can probably be extended to compare more than just convos
class AcuteEvalBlueprint(Blueprint):
    """
    Blueprint for a task that asks humans to compare conversational outputs
    """

    AgentStateClass: ClassVar[Type["AgentState"]] = AcuteEvalAgentState
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = AcuteEvalRunner
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = AcuteEvalBuilder
    supported_architects: ClassVar[List[str]] = ["mock"]  # TODO update
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self._initialization_data_dicts: List[Dict[str, Any]] = []
        task_file_name = os.path.basename(self.html_file)
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
            # TODO handle JSON directly
            raise NotImplementedError(
                "Parsing static tasks directly from JSON is not supported yet"
            )
        elif opts.get("pairings_task_data") is not None:
            self._initialization_data_dicts = opts["pairings_task_data"]
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
            # TODO handle JSON directly
            raise NotImplementedError(
                "Parsing static tasks directly from JSON is not supported yet"
            )
        elif opts.get("pairings_task_data") is not None:
            assert (
                len(opts.get("pairings_task_data")) > 0
            ), "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, or a list of tasks"
            )

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for AcuteEvalBlueprints.

        task_source points to the file intending to be deployed for this task
        data_csv has the data to be deployed for this task.
        """
        super(AcuteEvalBlueprint, cls).add_args_to_group(group)

        group.description = """
            AcuteEvalBlueprint: Tasks launched from acute eval blueprints
            require sets of pairings for workers to be able to compare to.

            These pairings can be provided as a csv or by passing a 
            pairings_task_data dict into extra_args.
        """
        group.add_argument(
            "--data-csv",
            dest="data_csv",
            help="Path to csv file containing task data",
            required=False,
        )
        return

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        return [
            InitializationData(
                shared=d, unit_data=[{}]
            )
            for d in self._initialization_data_dicts
        ]
