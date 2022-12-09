#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import json
import os
import time
import threading
import signal
import asyncio
import traceback

from mephisto.operations.datatypes import LiveTaskRun, LoopWrapper

from typing import (
    Dict,
    Optional,
    Type,
    Callable,
    TYPE_CHECKING,
)
from mephisto.data_model.task_run import TaskRun
from mephisto.abstractions.blueprint import SharedTaskState
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
)
from mephisto.abstractions.database import MephistoDB, EntryDoesNotExistException
from mephisto.data_model.qualification import QUAL_NOT_EXIST
from mephisto.utils.qualifications import make_qualification_dict
from mephisto.operations.task_launcher import TaskLauncher
from mephisto.operations.client_io_handler import ClientIOHandler
from mephisto.operations.worker_pool import WorkerPool
from mephisto.operations.registry import (
    get_blueprint_from_type,
    get_crowd_provider_from_type,
    get_architect_from_type,
)
from mephisto.utils.testing import get_mock_requester
from mephisto.utils.metrics import (
    launch_prometheus_server,
    start_metrics_server,
    shutdown_prometheus_server,
)
from mephisto.utils.logger_core import (
    get_logger,
    set_mephisto_log_level,
    format_loud,
    warn_once,
)
from omegaconf import DictConfig, OmegaConf

logger = get_logger(name=__name__)

if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import Blueprint
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.abstractions.architect import Architect


RUN_STATUS_POLL_TIME = 10


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
        self._task_runs_tracked: Dict[str, LiveTaskRun] = {}
        self.is_shutdown = False

        # Try to get an event loop. Only should be one
        # operator per thread
        has_loop = None
        try:
            has_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass  # We want there to be no running loop
        assert has_loop is None, "Can only run one operator loop per thread."

        # Create the event loop for this operator.
        self._event_loop = asyncio.new_event_loop()
        self._loop_wrapper = LoopWrapper(self._event_loop)
        self._run_tracker_task = self._event_loop.create_task(
            self._track_and_kill_runs(),
        )
        self._stop_task: Optional[asyncio.Task] = None
        self._using_prometheus = launch_prometheus_server()
        start_metrics_server()

    def get_running_task_runs(self) -> Dict[str, LiveTaskRun]:
        """Return the currently running task runs and their handlers"""
        return self._task_runs_tracked.copy()

    def _get_requester_and_provider_from_config(self, run_config: DictConfig):
        """
        Retrieve the desired provider from the config, raising an error
        if there's a mismatch between the found provider and desired requester
        """
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
        return requester, provider_type

    def _create_live_task_run(
        self,
        run_config: DictConfig,
        shared_state: SharedTaskState,
        task_run: TaskRun,
        architect_class: Type["Architect"],
        blueprint_class: Type["Blueprint"],
        provider_class: Type["CrowdProvider"],
    ) -> LiveTaskRun:
        """
        Initialize all of the members of a live task run object
        """
        # Register the blueprint with args to the task run to ensure cached
        blueprint = task_run.get_blueprint(args=run_config, shared_state=shared_state)

        # prepare the architect
        build_dir = os.path.join(task_run.get_run_dir(), "build")
        os.makedirs(build_dir, exist_ok=True)
        architect = architect_class(
            self.db, run_config, shared_state, task_run, build_dir
        )
        # Create the backend runner
        task_runner = blueprint_class.TaskRunnerClass(
            task_run, run_config, shared_state
        )

        # Small hack for auto appending block qualification
        # TODO(OWN) we can use blueprint.mro() to discover BlueprintMixins and extract from there
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

        # Create provider
        provider = provider_class(self.db)

        # Create the launcher
        initialization_data_iterable = blueprint.get_initialization_data()
        launcher = TaskLauncher(
            self.db,
            task_run,
            initialization_data_iterable,
            max_num_concurrent_units=run_config.task.max_num_concurrent_units,
        )

        worker_pool = WorkerPool(self.db)
        client_io = ClientIOHandler(self.db)
        live_run = LiveTaskRun(
            task_run=task_run,
            architect=architect,
            blueprint=blueprint,
            provider=provider,
            qualifications=shared_state.qualifications,
            task_runner=task_runner,
            task_launcher=launcher,
            client_io=client_io,
            worker_pool=worker_pool,
            loop_wrap=self._loop_wrapper,
        )
        worker_pool.register_run(live_run)
        client_io.register_run(live_run)

        return live_run

    def validate_and_run_config_or_die(
        self, run_config: DictConfig, shared_state: Optional[SharedTaskState] = None
    ) -> str:
        warn_once(
            "`validate_and_run_config` functions are deprecated in 1.0, and will "
            "be removed in Mephisto 1.1. Use `launch_task_run` versions instead."
        )
        return self.launch_task_run_or_die(run_config, shared_state=shared_state)

    def launch_task_run_or_die(
        self, run_config: DictConfig, shared_state: Optional[SharedTaskState] = None
    ) -> str:
        """
        Parse the given arguments and launch a job.
        """
        set_mephisto_log_level(level=run_config.get("log_level", "info"))

        requester, provider_type = self._get_requester_and_provider_from_config(
            run_config
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
            requester.db_id,
            json.dumps(OmegaConf.to_yaml(run_config, resolve=True)),
            provider_type,
            blueprint_type,
            requester.is_sandbox(),
        )
        task_run = TaskRun.get(self.db, new_run_id)

        live_run = self._create_live_task_run(
            run_config,
            shared_state,
            task_run,
            ArchitectClass,
            BlueprintClass,
            CrowdProviderClass,
        )

        try:
            # If anything fails after here, we have to cleanup the architect
            # Setup and deploy the server
            built_dir = live_run.architect.prepare()
            task_url = live_run.architect.deploy()

            # TODO(#102) maybe the cleanup (destruction of the server configuration?) should only
            # happen after everything has already been reviewed, this way it's possible to
            # retrieve the exact build directory to review a task for real
            live_run.architect.cleanup()

            # Register the task with the provider
            live_run.provider.setup_resources_for_task_run(
                task_run, run_config, shared_state, task_url
            )

            live_run.client_io.launch_channels()
        except (KeyboardInterrupt, Exception) as e:
            logger.error(
                "Encountered error while launching run, shutting down", exc_info=True
            )
            try:
                live_run.architect.shutdown()
            except (KeyboardInterrupt, Exception) as architect_exception:
                logger.exception(
                    f"Could not shut down architect: {architect_exception}",
                    exc_info=True,
                )
            raise e

        live_run.task_launcher.create_assignments()
        live_run.task_launcher.launch_units(url=task_url)

        self._task_runs_tracked[task_run.db_id] = live_run
        task_run.update_completion_progress(status=False)

        return task_run.db_id

    async def _track_and_kill_runs(self):
        """
        Background task that shuts down servers when a task
        is fully done.
        """
        # TODO(#649) only trigger these on a status change?
        while not self.is_shutdown:
            runs_to_check = list(self._task_runs_tracked.values())
            for tracked_run in runs_to_check:
                await asyncio.sleep(0.01)  # Low pri, allow to be interrupted
                patience = tracked_run.task_run.get_task_args().no_submission_patience
                if patience < time.time() - tracked_run.client_io.last_submission_time:
                    logger.warn(
                        f"It has been greater than the set no_submission_patience of {patience} "
                        f"for {tracked_run.task_run} since the last submission, shutting this run down."
                    )
                    tracked_run.force_shutdown = True
                if not tracked_run.force_shutdown:
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

                tracked_run.client_io.shutdown()
                tracked_run.worker_pool.shutdown()
                tracked_run.task_launcher.shutdown()
                tracked_run.task_launcher.expire_units()
                tracked_run.architect.shutdown()
                del self._task_runs_tracked[task_run.db_id]
            await asyncio.sleep(RUN_STATUS_POLL_TIME)
            if self._using_prometheus:
                launch_prometheus_server()

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

        def cleanup_runs():
            runs_to_close = list(self._task_runs_tracked.keys())
            for run_id in runs_to_close:
                self._task_runs_tracked[run_id].shutdown()

        tasks = {
            "expire-units": end_launchers_and_expire_units,
            "end-architects": end_architects,
            "cleanup-runs": cleanup_runs,
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
        if self._event_loop.is_running():
            self._event_loop.stop()
        self._event_loop.run_until_complete(self.shutdown_async())

    async def shutdown_async(self):
        """Shut down the asyncio parts of the Operator"""

        if self._stop_task is not None:
            await self._stop_task
        await self._run_tracker_task

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
                logger.warn(
                    "Ignoring ^C during unit expirations. ^| if you NEED to exit and you will "
                    "have to clean up units that hadn't been expired afterwards."
                )

            old_handler = signal.signal(signal.SIGINT, cant_cancel_expirations)
            tracked_run.task_launcher.expire_units()
            signal.signal(signal.SIGINT, old_handler)
        try:
            remaining_runs = self._task_runs_tracked.values()

            while len(remaining_runs) > 0:
                logger.info(
                    f"Waiting on {len(remaining_runs)} task runs with assignments in-flight. "
                    f"{format_loud('Ctrl-C ONCE')} to kill running tasks and FORCE QUIT."
                )
                next_runs = []
                for tracked_run in remaining_runs:
                    if tracked_run.task_run.get_is_completed():
                        tracked_run.shutdown()
                        tracked_run.architect.shutdown()
                    else:
                        next_runs.append(tracked_run)
                if len(next_runs) > 0:
                    time.sleep(30)
                remaining_runs = next_runs
        except Exception as e:
            logger.exception(
                f"Encountered problem during shutting down {e}", exc_info=True
            )

            traceback.print_exc()
        except (KeyboardInterrupt, SystemExit) as e:
            logger.warning(
                "Skipping waiting for outstanding task completions, shutting down servers now!"
                f"Follow cleanup instructions {format_loud('closely')} for proper cleanup.",
            )
            for tracked_run in remaining_runs:
                logger.warning(
                    f"Cleaning up run {tracked_run.task_run.db_id}. {format_loud('Ctrl-C once per step')} to skip that step."
                )
                try:
                    logger.warning(f"Shutting down active Units in-flight.")
                    tracked_run.worker_pool.disconnect_active_agents()
                    tracked_run.task_runner.shutdown()
                except (KeyboardInterrupt, SystemExit) as e:
                    logger.warning("Skipped!")
                try:
                    logger.warning(f"Cleaning up remaining workers.")
                    tracked_run.worker_pool.shutdown()
                except (KeyboardInterrupt, SystemExit) as e:
                    logger.warning("Skipped!")
                try:
                    logger.warning(f"Closing client communications.")
                    tracked_run.client_io.shutdown()
                except (KeyboardInterrupt, SystemExit) as e:
                    logger.warning("Skipped!")
                try:
                    logger.warning(f"Shutting down servers")
                    tracked_run.architect.shutdown()
                except (KeyboardInterrupt, SystemExit) as e:
                    logger.warning("Skipped!")
        finally:
            runs_to_close = list(self._task_runs_tracked.keys())
            for run_id in runs_to_close:
                self._task_runs_tracked[run_id].shutdown()
            if self._event_loop.is_running():
                self._event_loop.stop()
            self._event_loop.run_until_complete(self.shutdown_async())
            if self._using_prometheus:
                shutdown_prometheus_server()

    def validate_and_run_config(
        self, run_config: DictConfig, shared_state: Optional[SharedTaskState] = None
    ) -> Optional[str]:
        warn_once(
            "`validate_and_run_config` functions are deprecated in 1.0, and will "
            "be removed in Mephisto 1.1. Use `launch_task_run` versions instead."
        )
        return self.launch_task_run(run_config, shared_state=shared_state)

    def launch_task_run(
        self, run_config: DictConfig, shared_state: Optional[SharedTaskState] = None
    ) -> Optional[str]:
        """
        Wrapper around validate_and_run_config_or_die that prints errors on
        failure, rather than throwing. Generally for use in scripts.
        """
        assert (
            not self.is_shutdown
        ), "Cannot run a config on a shutdown operator. Create a new one."
        try:
            return self.launch_task_run_or_die(
                run_config=run_config, shared_state=shared_state
            )
        except (KeyboardInterrupt, Exception) as e:
            logger.error("Ran into error while launching run: ", exc_info=True)
            return None

    def print_run_details(self):
        """Print details about running tasks"""
        for task in self.get_running_task_runs():
            logger.info(f"Operator running task ID = {task}")

    async def _stop_loop_when_no_running_tasks(self, log_rate: Optional[int] = None):
        """
        Stop this operator's event loop when no tasks are
        running anymore
        """
        last_log = 0.0
        while len(self.get_running_task_runs()) > 0 and not self.is_shutdown:
            if log_rate is not None:
                if time.time() - last_log > log_rate:
                    last_log = time.time()
                    self.print_run_details()
            await asyncio.sleep(RUN_STATUS_POLL_TIME)
        self._event_loop.stop()

    def _run_loop_until(self, condition_met: Callable[[], bool], timeout) -> bool:
        """
        Function to run the event loop until a specific condition is met, or
        a timeout elapses
        """
        asyncio.set_event_loop(self._event_loop)

        async def wait_for_condition_or_timeout():
            condition_was_met = False
            start_time = time.time()
            while time.time() - start_time < timeout:
                if condition_met():
                    condition_was_met = True
                    break
                await asyncio.sleep(0.2)
            return condition_was_met

        return self._event_loop.run_until_complete(wait_for_condition_or_timeout())

    def _wait_for_runs_in_testing(self, timeout_time) -> None:
        """
        Function to kick off the operator main event loop
        specifically in testing, run until timeout time is exceeded

        generally replaces wait_for_runs_then_shutdown in testing
        """
        asyncio.set_event_loop(self._event_loop)
        self._stop_task = self._event_loop.create_task(
            self._stop_loop_when_no_running_tasks(log_rate=timeout_time),
        )

        def trigger_shutdown():
            self.is_shutdown = True

        self._event_loop.call_later(timeout_time, trigger_shutdown)
        self._event_loop.run_forever()

    def wait_for_runs_then_shutdown(
        self, skip_input=False, log_rate: Optional[int] = None
    ) -> None:
        """
        Wait for task_runs to complete, and then shutdown.

        Set log_rate to get print statements of currently running tasks
        at the specified interval
        """
        asyncio.set_event_loop(self._event_loop)
        self._stop_task = self._event_loop.create_task(
            self._stop_loop_when_no_running_tasks(log_rate=log_rate),
        )
        try:
            self._event_loop.run_forever()
        except Exception as e:
            traceback.print_exc()
        except (KeyboardInterrupt, SystemExit) as e:
            logger.exception(
                "Cleaning up after keyboard interrupt, please "
                f"{format_loud('wait to Ctrl-C again')} until instructed to.",
                exc_info=False,
            )
        finally:
            self.shutdown()
