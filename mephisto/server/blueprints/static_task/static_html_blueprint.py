#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.server.blueprints.abstract.static_task.static_blueprint import (
    StaticBlueprint,
)
from mephisto.server.blueprints.static_task.static_html_task_builder import (
    StaticHTMLTaskBuilder,
)
from mephisto.core.registry import register_mephisto_abstraction

import os
import time
import csv

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.agent import OnboardingAgent
    from argparse import _ArgumentGroup as ArgumentGroup

BLUEPRINT_TYPE = "static_task"


@register_mephisto_abstraction()
class StaticHTMLBlueprint(StaticBlueprint):
    """Blueprint for a task that runs off of a built react javascript bundle"""

    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = StaticHTMLTaskBuilder
    BLUEPRINT_TYPE = BLUEPRINT_TYPE

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        self.html_file = os.path.expanduser(opts["task_source"])
        if not os.path.exists(self.html_file):
            raise FileNotFoundError(
                f"Specified html file {self.html_file} was not found from {os.getcwd()}"
            )

        self.onboarding_html_file = opts.get("onboarding_source", None)
        if self.onboarding_html_file is not None:
            self.onboarding_html_file = os.path.expanduser(self.onboarding_html_file)
            if not os.path.exists(self.onboarding_html_file):
                raise FileNotFoundError(
                    f"Specified onboarding html file {self.onboarding_html_file} was not found from {os.getcwd()}"
                )

        task_file_name = os.path.basename(self.html_file)
        for entry in self._initialization_data_dicts:
            entry["html"] = task_file_name

    @classmethod
    def assert_task_args(cls, opts: Any) -> None:
        """Ensure that the data can be properly loaded"""
        if opts.get("data_csv") is not None:
            csv_file = os.path.expanduser(opts["data_csv"])
            assert os.path.exists(
                csv_file
            ), f"Provided csv file {csv_file} doesn't exist"
        elif opts.get("data_json") is not None:
            # TODO(#95) handle JSON directly
            raise NotImplementedError(
                "Parsing static tasks directly from JSON is not supported yet"
            )
        elif opts.get("static_task_data") is not None:
            assert (
                len(opts.get("static_task_data")) > 0
            ), "Length of data dict provided was 0"
        else:
            raise AssertionError(
                "Must provide one of a data csv, json, or a list of tasks"
            )

        if opts.get("onboarding_qualification") is not None:
            assert opts.get("onboarding_source") is not None, (
                "Must use onboarding html with an onboarding qualification to "
                "use onboarding."
            )
            assert opts.get("validate_onboarding") is not None, (
                "Must use an onboarding validation function to use onboarding "
                "with static tasks."
            )


    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds required options for StaticBlueprints.

        task_source points to the file intending to be deployed for this task
        data_csv has the data to be deployed for this task.
        """
        super().add_args_to_group(group)

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
            "--onboarding-source",
            dest="onboarding_source",
            help="Optional path to source HTML file to onboarding the task",
        )
        return

    def validate_onboarding(
        self, worker: "Worker", onboarding_agent: "OnboardingAgent"
    ) -> bool:
        """
        Check the incoming onboarding data and evaluate if the worker
        has passed the qualification or not. Return True if the worker
        has qualified.
        """
        return self.opts['validate_onboarding'](onboarding_agent.state.get_data())