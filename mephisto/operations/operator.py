#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
import shutil
import json
import os
import tempfile
import time
import threading
import shlex
import traceback
import signal

from argparse import ArgumentParser

from mephisto.operations.supervisor import Supervisor, Job

from typing import Dict, Optional, List, Any, Tuple, NamedTuple, Type, TYPE_CHECKING
from mephisto.data_model.task_config import TaskConfig
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.requester import Requester
from mephisto.abstractions.blueprint import OnboardingRequired, SharedTaskState
from mephisto.abstractions.database import MephistoDB, EntryDoesNotExistException
from mephisto.data_model.qualification import make_qualification_dict, QUAL_NOT_EXIST
from mephisto.operations.task_launcher import TaskLauncher
from mephisto.operations.registry import (
    get_blueprint_from_type,
    get_crowd_provider_from_type,
    get_architect_from_type,
)
from mephisto.operations.utils import get_mock_requester

from mephisto.operations.logger_core import get_logger, set_mephisto_log_level
from omegaconf import DictConfig, OmegaConf

logger = get_logger(name=__name__)

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.blueprint import Blueprint, TaskRunner
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.abstractions.architect import Architect
    from argparse import Namespace


RUN_STATUS_POLL_TIME = 10


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

    def __init__(self, db: "MephistoDB"):
        self.db = db
        self.supervisor = Supervisor(db)
        self._task_runs_tracked: Dict[str, TrackedRun] = {}
        self.is_shutdown = False
        self._run_tracker_thread = threading.Thread(
            target=self._track_and_kill_runs, name="Operator-tracking-thread"
        )
        self._run_tracker_thread.start()

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

    def get_running_task_runs(self):
        """Return the currently running task runs and their handlers"""
        return self._task_runs_tracked.copy()

    def parse_and_launch_run(
        self,
        arg_list: Optional[List[str]] = None,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Wrapper around parse and launch run that prints errors on failure, rather
        than throwing. Generally for use in scripts.
        """
        raise Exception(
            "Operator.parse_and_launch_run has been deprecated in favor "
            "of using Hydra for argument configuration. See the docs at "
            "https://github.com/facebookresearch/Mephisto/blob/main/docs/hydra_migration.md "
            "in order to upgrade."
        )

    def validate_and_run_config_or_die(
        self, run_config: DictConfig, shared_state: Optional[SharedTaskState] = None
    ) -> str:
        """
        Parse the given arguments and launch a job.
        """
        set_mephisto_log_level(level=run_config.get("log_level", "info"))

        # First try to find the requester:
        requester_name = run_config.provider.requester_name
        requesters = self.db.find_requesters(requester_name=requester_name)
        if len(requesters) == 0:
            if run_config.provider.requester_name == "MOCK_REQUESTER":
                requesters = [get_mock_requester(self.db)]
            else:
                raise EntryDoesNotExistException(
                    f"No requester found with name {requester_name}"
                )
        requester = requesters[0]
        requester_id = requester.db_id
        provider_type = requester.provider_type
        assert provider_type == run_config.provider._provider_type, (
            f"Found requester for name {requester_name} is not "
            f"of the specified type {run_config.provider._provider_type}, "
            f"but is instead {provider_type}."
        )

        # Next get the abstraction classes, and run validation
        # before anything is actually created in the database
        blueprint_type = run_config.blueprint._blueprint_type
        architect_type = run_config.architect._architect_type
        BlueprintClass = get_blueprint_from_type(blueprint_type)
        ArchitectClass = get_architect_from_type(architect_type)
        CrowdProviderClass = get_crowd_provider_from_type(provider_type)

        if shared_state is None:
            shared_state = BlueprintClass.SharedStateClass()

        BlueprintClass.assert_task_args(run_config, shared_state)
        ArchitectClass.assert_task_args(run_config, shared_state)
        CrowdProviderClass.assert_task_args(run_config, shared_state)

        # Find an existing task or create a new one
        task_name = run_config.task.get("task_name", None)
        if task_name is None:
            task_name = blueprint_type
            logger.warning(
                f"Task is using the default blueprint name {task_name} as a name, "
                "as no task_name is provided"
            )
        tasks = self.db.find_tasks(task_name=task_name)
        task_id = None
        if len(tasks) == 0:
            task_id = self.db.new_task(task_name, blueprint_type)
        else:
            task_id = tasks[0].db_id

        logger.info(f"Creating a task run under task name: {task_name}")

        # Create a new task run
        new_run_id = self.db.new_task_run(
            task_id,
            requester_id,
            json.dumps(OmegaConf.to_yaml(run_config, resolve=True)),
            provider_type,
            blueprint_type,
            requester.is_sandbox(),
        )
        task_run = TaskRun.get(self.db, new_run_id)

        try:
            # Register the blueprint with args to the task run,
            # ensure cached
            blueprint = task_run.get_blueprint(
                args=run_config, shared_state=shared_state
            )

            # If anything fails after here, we have to cleanup the architect
            build_dir = os.path.join(task_run.get_run_dir(), "build")
            os.makedirs(build_dir, exist_ok=True)
            architect = ArchitectClass(
                self.db, run_config, shared_state, task_run, build_dir
            )

            # Setup and deploy the server
            built_dir = architect.prepare()
            task_url = architect.deploy()

            # TODO(#102) maybe the cleanup (destruction of the server configuration?) should only
            # happen after everything has already been reviewed, this way it's possible to
            # retrieve the exact build directory to review a task for real
            architect.cleanup()

            # Create the backend runner
            task_runner = BlueprintClass.TaskRunnerClass(
                task_run, run_config, shared_state
            )

            # Small hack for auto appending block qualification
            existing_qualifications = shared_state.qualifications
            if run_config.blueprint.get("block_qualification", None) is not None:
                existing_qualifications.append(
                    make_qualification_dict(
                        run_config.blueprint.block_qualification, QUAL_NOT_EXIST, None
                    )
                )
            if run_config.blueprint.get("onboarding_qualification", None) is not None:
                existing_qualifications.append(
                    make_qualification_dict(
                        OnboardingRequired.get_failed_qual(
                            run_config.blueprint.onboarding_qualification
                        ),
                        QUAL_NOT_EXIST,
                        None,
                    )
                )
            shared_state.qualifications = existing_qualifications

            # Register the task with the provider
            provider = CrowdProviderClass(self.db)
            provider.setup_resources_for_task_run(
                task_run, run_config, shared_state, task_url
            )

            initialization_data_iterable = blueprint.get_initialization_data()

            # Link the job together
            job = self.supervisor.register_job(
                architect, task_runner, provider, existing_qualifications
            )
            if self.supervisor.sending_thread is None:
                self.supervisor.launch_sending_thread()
        except (KeyboardInterrupt, Exception) as e:
            logger.error(
                "Encountered error while launching run, shutting down", exc_info=True
            )
            try:
                architect.shutdown()
            except (KeyboardInterrupt, Exception) as architect_exception:
                logger.exception(
                    f"Could not shut down architect: {architect_exception}",
                    exc_info=True,
                )
            raise e

        launcher = TaskLauncher(
            self.db,
            task_run,
            initialization_data_iterable,
            max_num_concurrent_units=run_config.task.max_num_concurrent_units,
        )
        launcher.create_assignments()
        launcher.launch_units(task_url)

        self._task_runs_tracked[task_run.db_id] = TrackedRun(
            task_run=task_run,
            task_launcher=launcher,
            task_runner=task_runner,
            architect=architect,
            job=job,
        )
        task_run.update_completion_progress(status=False)

        return task_run.db_id

    def _track_and_kill_runs(self):
        """
        Background thread that shuts down servers when a task
        is fully done.
        """
        while not self.is_shutdown:
            runs_to_check = list(self._task_runs_tracked.values())
            for tracked_run in runs_to_check:
                task_run = tracked_run.task_run
                if tracked_run.task_launcher.finished_generators is False:
                    # If the run can still generate assignments, it's
                    # definitely not done
                    continue
                task_run.update_completion_progress(
                    task_launcher=tracked_run.task_launcher
                )
                if not task_run.get_is_completed():
                    continue
                else:
                    self.supervisor.shutdown_job(tracked_run.job)
                    tracked_run.architect.shutdown()
                    tracked_run.task_launcher.shutdown()
                    del self._task_runs_tracked[task_run.db_id]
            time.sleep(RUN_STATUS_POLL_TIME)

    def force_shutdown(self, timeout=5):
        """
        Force a best-effort shutdown of everything, letting no individual
        shutdown step suspend for more than the timeout before moving on.

        Skips waiting for in-flight assignments to rush the shutdown.

        ** Should only be used in sandbox or test environments. **
        """
        self.is_shutdown = True

        def end_launchers_and_expire_units():
            for tracked_run in self._task_runs_tracked.values():
                tracked_run.task_launcher.shutdown()
                tracked_run.task_launcher.expire_units()

        def end_architects():
            for tracked_run in self._task_runs_tracked.values():
                tracked_run.architect.shutdown()

        def shutdown_supervisor():
            if self.supervisor is not None:
                self.supervisor.shutdown()

        tasks = {
            "expire-units": end_launchers_and_expire_units,
            "kill-architects": end_architects,
            "fire-supervisor": shutdown_supervisor,
        }

        for tname, t in tasks.items():
            shutdown_thread = threading.Thread(target=t, name=f"force-shutdown-{tname}")
            shutdown_thread.start()
            start_time = time.time()
            while time.time() - start_time < timeout and shutdown_thread.is_alive():
                time.sleep(0.5)
            if not shutdown_thread.is_alive():
                # Only join if the shutdown fully completed
                shutdown_thread.join()

    def shutdown(self, skip_input=True):
        logger.info("operator shutting down")
        self.is_shutdown = True
        runs_to_check = list(self._task_runs_tracked.items())
        for run_id, tracked_run in runs_to_check:
            logger.info(f"Expiring units for task run {run_id}.")
            try:
                tracked_run.task_launcher.shutdown()
            except (KeyboardInterrupt, SystemExit) as e:
                logger.info(
                    f"Skipping waiting for launcher threads to join on task run {run_id}."
                )

            def cant_cancel_expirations(self, sig, frame):
                logging.warn(
                    "Ignoring ^C during unit expirations. ^| if you NEED to exit and you will "
                    "clean up units that hadn't been expired afterwards."
                )

            old_handler = signal.signal(signal.SIGINT, cant_cancel_expirations)
            tracked_run.task_launcher.expire_units()
            signal.signal(signal.SIGINT, old_handler)
        try:
            remaining_runs = self._task_runs_tracked.values()
            while len(remaining_runs) > 0:
                next_runs = []
                for tracked_run in remaining_runs:
                    if tracked_run.task_run.get_is_completed():
                        tracked_run.architect.shutdown()
                    else:
                        next_runs.append(tracked_run)
                if len(next_runs) > 0:
                    logger.info(
                        f"Waiting on {len(remaining_runs)} task runs with assignments in-flight "
                        f"Ctrl-C ONCE to kill running tasks and FORCE QUIT."
                    )
                    time.sleep(30)
                remaining_runs = next_runs
        except Exception as e:
            logger.exception(
                f"Encountered problem during shutting down {e}", exc_info=True
            )
            import traceback

            traceback.print_exc()
        except (KeyboardInterrupt, SystemExit) as e:
            logger.info(
                "Skipping waiting for outstanding task completions, shutting down servers now!"
            )
            for tracked_run in remaining_runs:
                logger.info(
                    f"Shutting down Architect for task run {tracked_run.task_run.db_id}"
                )
                tracked_run.architect.shutdown()
        finally:
            self.supervisor.shutdown()
            self._run_tracker_thread.join()

    def validate_and_run_config(
        self, run_config: DictConfig, shared_state: Optional[SharedTaskState] = None
    ) -> Optional[str]:
        """
        Wrapper around validate_and_run_config_or_die that prints errors on
        failure, rather than throwing. Generally for use in scripts.
        """
        try:
            return self.validate_and_run_config_or_die(
                run_config=run_config, shared_state=shared_state
            )
        except (KeyboardInterrupt, Exception) as e:
            logger.error("Ran into error while launching run: ", exc_info=True)
            return None

    def parse_and_launch_run_wrapper(
        self,
        arg_list: Optional[List[str]] = None,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Wrapper around parse and launch run that prints errors on failure, rather
        than throwing. Generally for use in scripts.
        """
        raise Exception(
            "Operator.parse_and_launch_run_wrapper has been deprecated in favor "
            "of using Hydra for argument configuration. See the docs at "
            "https://github.com/facebookresearch/Mephisto/blob/main/docs/hydra_migration.md "
            "in order to upgrade."
        )

    def print_run_details(self):
        """Print details about running tasks"""
        # TODO(#93) parse these tasks and get the full details
        for task in self.get_running_task_runs():
            logger.info(f"Operator running task ID = {task}")

    def wait_for_runs_then_shutdown(
        self, skip_input=False, log_rate: Optional[int] = None
    ) -> None:
        """
        Wait for task_runs to complete, and then shutdown.

        Set log_rate to get print statements of currently running tasks
        at the specified interval
        """
        try:
            try:
                last_log = 0.0
                while len(self.get_running_task_runs()) > 0:
                    if log_rate is not None:
                        if time.time() - last_log > log_rate:
                            last_log = time.time()
                            self.print_run_details()
                    time.sleep(RUN_STATUS_POLL_TIME)

            except Exception as e:
                if skip_input:
                    raise e

                traceback.print_exc()
                should_quit = input(
                    "The above exception happened while running a task, do "
                    "you want to shut down? (y)/n: "
                )
                if should_quit not in ["n", "N", "no", "No"]:
                    raise e

        except Exception as e:
            import traceback

            traceback.print_exc()
        except (KeyboardInterrupt, SystemExit) as e:
            logger.exception(
                "Cleaning up after keyboard interrupt, please wait!", exc_info=True
            )
        finally:
            self.shutdown()
