#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
import shutil
import os
import tempfile
import time
import threading

from argparse import ArgumentParser

from mephisto.core.supervisor import Supervisor, Job

from typing import Dict, Optional, List, Any, Tuple, NamedTuple, Type, TYPE_CHECKING
from mephisto.data_model.task_config import TaskConfig
from mephisto.data_model.task import TaskRun
from mephisto.data_model.requester import Requester
from mephisto.data_model.database import MephistoDB, EntryDoesNotExistException
from mephisto.core.argparse_parser import get_default_arg_dict
from mephisto.core.task_launcher import TaskLauncher
from mephisto.core.utils import (
    get_blueprint_from_type,
    get_crowd_provider_from_type,
    get_architect_from_type,
)

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.blueprint import Blueprint, TaskRunner
    from mephisto.data_model.crowd_provider import CrowdProvider
    from mephisto.data_model.architect import Architect
    from argparse import Namespace


class TrackedRun(NamedTuple):
    task_run: TaskRun
    architect: "Architect"
    task_runner: "TaskRunner"
    task_launcher: TaskLauncher
    job: Job


class Operator:
    """
    Acting as the controller behind the curtain, the Operator class
    is responsible for managing the knobs, switches, and dials 
    of the rest of the Mephisto architecture. 

    Most convenience scripts for using Mephisto will use an Operator
    to get the job done, though this class itself is also a 
    good model to use to understand how the underlying 
    architecture works in order to build custom jobs or workflows.
    """

    def __init__(self, db: "MephistoDB", extra_args: Optional[Dict[str, Any]] = None):
        self.db = db
        self.supervisor = Supervisor(db)
        self._task_runs_tracked: Dict[str, TrackedRun] = {}
        self.is_shutdown = False
        self._run_tracker_thread = threading.Thread(
            target=self._track_and_kill_runs, name="Operator-tracking-thread"
        )
        self._run_tracker_thread.start()
        self.extra_args = extra_args if extra_args is not None else {}

    @staticmethod
    def _get_baseline_argparser() -> ArgumentParser:
        """Return a parser for the baseline requirements to launch a job"""
        parser = ArgumentParser()
        parser.add_argument(
            "--blueprint-type",
            dest="blueprint_type",
            help="Name of the blueprint to launch",
            required=True,
        )
        parser.add_argument(
            "--architect-type",
            dest="architect_type",
            help="Name of the architect to launch with",
            required=True,
        )
        parser.add_argument(
            "--requester-name",
            dest="requester_name",
            help="Identifier for the requester to launch as",
            required=True,
        )
        return parser

    @staticmethod
    def _parse_args_from_classes(
        BlueprintClass: Type["Blueprint"],
        ArchitectClass: Type["Architect"],
        CrowdProviderClass: Type["CrowdProvider"],
        argument_list: List[str],
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Parse the given arguments over the parsers for the given types"""
        # Create the parser
        parser = ArgumentParser()
        blueprint_group = parser.add_argument_group("blueprint")
        BlueprintClass.add_args_to_group(blueprint_group)
        provider_group = parser.add_argument_group("crowd_provider")
        CrowdProviderClass.add_args_to_group(provider_group)
        architect_group = parser.add_argument_group("architect")
        ArchitectClass.add_args_to_group(architect_group)
        task_group = parser.add_argument_group("task_config")
        TaskConfig.add_args_to_group(task_group)

        # Return parsed args
        try:
            known, unknown = parser.parse_known_args(argument_list)
        except SystemExit:
            raise Exception("Argparse broke - must fix")
        return vars(known), unknown

    def get_running_task_runs(self):
        """Return the currently running task runs and their handlers"""
        return self._task_runs_tracked.copy()

    # TODO there should be a way to provide default arguments via a config file

    # TODO there should be a thread that shuts down servers when a task run is done

    def parse_and_launch_run(self, arg_list: Optional[List[str]] = None):
        """
        Parse the given arguments and launch a job.

        Read in arguments from the command line if none are provided
        """
        # Extract the abstractions being used
        parser = self._get_baseline_argparser()
        type_args, task_args_string = parser.parse_known_args(arg_list)

        requesters = self.db.find_requesters(requester_name=type_args.requester_name)
        if len(requesters) == 0:
            raise EntryDoesNotExistException(
                f"No requester found with name {type_args.requester_name}"
            )
        requester = requesters[0]
        requester_id = requester.db_id
        provider_type = requester.provider_type

        # Parse the arguments for the abstractions to ensure
        # everything required is set
        BlueprintClass = get_blueprint_from_type(type_args.blueprint_type)
        ArchitectClass = get_architect_from_type(type_args.architect_type)
        CrowdProviderClass = get_crowd_provider_from_type(provider_type)
        task_args, _unknown = self._parse_args_from_classes(
            BlueprintClass, ArchitectClass, CrowdProviderClass, task_args_string
        )

        task_args.update(self.extra_args)

        # Load the classes to force argument validation before anything
        # is actually created in the database
        # TODO perhaps parse the arguments for these things one at a time?
        BlueprintClass.assert_task_args(task_args)
        ArchitectClass.assert_task_args(task_args)
        CrowdProviderClass.assert_task_args(task_args)

        # Find an existing task or create a new one
        task_name = task_args.get("task_name", type_args.blueprint_type)
        tasks = self.db.find_tasks(task_name=task_name)
        task_id = None
        if len(tasks) == 0:
            task_id = self.db.new_task(task_name, type_args.blueprint_type)
        else:
            task_id = tasks[0].db_id

        # Create a new task run
        new_run_id = self.db.new_task_run(
            task_id,
            requester_id,
            " ".join(task_args_string),
            provider_type,
            type_args.blueprint_type,
            requester.is_sandbox(),
        )
        task_run = TaskRun(self.db, new_run_id)

        build_dir = os.path.join(task_run.get_run_dir(), "build")
        os.makedirs(build_dir, exist_ok=True)
        # TODO maybe this can be simplifies, and the task_run can be responsible for task_args?
        architect = ArchitectClass(self.db, task_args, task_run, build_dir)

        # Setup and deploy the server
        built_dir = architect.prepare()
        task_url = architect.deploy()

        # TODO maybe the cleanup (destruction of the server configuration?) should only
        # happen after everything has already been reviewed, this way it's possible to
        # retrieve the exact build directory to review a task for real
        architect.cleanup()

        socket_urls = architect.get_socket_urls()

        # Create the backend runner
        task_runner = BlueprintClass.TaskRunnerClass(task_run, task_args)

        # Register the task with the provider
        provider = CrowdProviderClass(self.db)
        provider.setup_resources_for_task_run(task_run, task_url)

        blueprint = BlueprintClass(task_run, task_args)
        initialization_data_array = blueprint.get_initialization_data()
        # TODO extend
        if not isinstance(initialization_data_array, list):
            raise NotImplementedError(
                "Non-list initialization data is not yet supported"
            )

        launcher = TaskLauncher(self.db, task_run, initialization_data_array)
        launcher.create_assignments()
        launcher.launch_units(task_url)

        # Link the job together
        job = self.supervisor.register_job(architect, task_runner, provider)
        if self.supervisor.sending_thread is None:
            self.supervisor.launch_sending_thread()

        self._task_runs_tracked[task_run.db_id] = TrackedRun(
            task_run=task_run,
            task_launcher=launcher,
            task_runner=task_runner,
            architect=architect,
            job=job,
        )

    def _track_and_kill_runs(self):
        """
        Background thread that shuts down servers when a task
        is fully done.
        """
        while not self.is_shutdown:
            runs_to_check = list(self._task_runs_tracked.values())
            for tracked_run in runs_to_check:
                task_run = tracked_run.task_run
                if task_run.get_is_completed():
                    self.supervisor.shutdown_job(tracked_run.job)
                    tracked_run.architect.shutdown()
                    # TODO kill the runner too?
                    del self._task_runs_tracked[task_run.db_id]
            # TODO find a way to subscribe to completed or
            # expired tasks to be able to avoid a sleep call
            time.sleep(2)

    def shutdown(self):
        print("operator shutting down")  # TODO logger
        self.is_shutdown = True
        for tracked_run in self._task_runs_tracked.values():
            tracked_run.task_launcher.expire_units()
            # TODO wait for the run to be marked complete in general
            # TODO perhaps kill things in the task runner?
            tracked_run.architect.shutdown()
        self.supervisor.shutdown()
        self._run_tracker_thread.join()
