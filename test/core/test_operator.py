#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
import shutil
import shlex
import os
import tempfile
import time
import threading
from unittest.mock import patch
from tqdm import TMonitor  # type: ignore

from mephisto.utils.testing import get_test_requester
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.operations.operator import Operator
from mephisto.abstractions.architects.mock_architect import (
    MockArchitect,
    MockArchitectArgs,
)
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.abstractions.providers.mock.mock_provider import MockProviderArgs
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprintArgs
from mephisto.data_model.task_run import TaskRunArgs
from omegaconf import OmegaConf

from typing import Type, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB

TIMEOUT_TIME = 15


MOCK_TASK_ARGS = TaskRunArgs(
    task_title="title",
    task_description="This is a description",
    task_reward=0.3,
    task_tags="1,2,3",
    submission_timeout=5,
)


class OperatorBaseTest(object):
    """
    Unit testing for the Mephisto Operator
    """

    DB_CLASS: ClassVar[Type["MephistoDB"]]

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)
        self.requester_name, _req_id = get_test_requester(self.db)
        self.operator = None

    def tearDown(self):
        if self.operator is not None:
            self.operator.force_shutdown(timeout=10)
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)
        SHUTDOWN_TIMEOUT = 10
        threads = threading.enumerate()
        target_threads = [t for t in threads if not isinstance(t, TMonitor) and not t.daemon]
        start_time = time.time()
        while len(target_threads) > 1 and time.time() - start_time < SHUTDOWN_TIMEOUT:
            threads = threading.enumerate()
            target_threads = [t for t in threads if not isinstance(t, TMonitor) and not t.daemon]
            time.sleep(0.3)
        self.assertTrue(
            time.time() - start_time < SHUTDOWN_TIMEOUT,
            f"Expected only main thread at teardown after {SHUTDOWN_TIMEOUT} seconds, found {target_threads}",
        )

    def wait_for_complete_assignment(self, assignment, timeout: int):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if assignment.get_status() == AssignmentState.COMPLETED:
                break
            time.sleep(0.1)
        self.assertLess(  # type: ignore
            time.time() - start_time, timeout, "Assignment not completed in time"
        )

    def await_server_start(self, architect: "MockArchitect"):
        start_time = time.time()
        assert architect.server is not None, "Cannot wait on empty server"
        while time.time() - start_time < 5:
            if len(architect.server.subs) > 0:
                break
            time.sleep(0.1)
        self.assertLess(time.time() - start_time, 5, "Mock server not up in time")  # type: ignore

    def test_initialize_operator(self):
        """Quick test to ensure that the operator can be initialized"""
        self.operator = Operator(self.db)

    def assert_sandbox_worker_created(self, worker_name, timeout=2) -> None:
        self.assertTrue(  # type: ignore
            self.operator._run_loop_until(
                lambda: len(self.db.find_workers(worker_name=worker_name + "_sandbox")) > 0,
                timeout,
            ),
            f"Worker {worker_name} not created in time!",
        )

    def assert_agent_created(self, agent_num, timeout=2) -> str:
        self.assertTrue(  # type: ignore
            self.operator._run_loop_until(
                lambda: len(self.db.find_agents()) == agent_num,
                timeout,
            ),
            f"Agent {agent_num} not created in time!",
        )
        agents = self.db.find_agents()
        agent = agents[agent_num - 1]
        self.assertIsNotNone(agent)  # type: ignore
        return agent.db_id

    def await_channel_requests(self, tracked_run, timeout=2) -> None:
        self.assertTrue(  # type: ignore
            self.operator._run_loop_until(
                lambda: len(tracked_run.client_io.request_id_to_channel_id) == 0,
                timeout,
            ),
            f"Channeled requests not processed in time!",
        )

    @patch("mephisto.operations.operator.RUN_STATUS_POLL_TIME", 1.5)
    def test_run_job_concurrent(self):
        """Ensure that a job can be run that requires connected concurrent workers"""
        self.operator = Operator(self.db)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=1, is_concurrent=True),
            provider=MockProviderArgs(requester_name=self.requester_name),
            architect=MockArchitectArgs(should_run_server=True),
            task=MOCK_TASK_ARGS,
        )
        self.operator.launch_task_run(OmegaConf.structured(config))
        tracked_runs = self.operator.get_running_task_runs()
        self.assertEqual(len(tracked_runs), 1, "Run not launched")
        task_run_id, tracked_run = list(tracked_runs.items())[0]

        self.assertIsNotNone(tracked_run)
        self.assertIsNotNone(tracked_run.task_launcher)
        self.assertIsNotNone(tracked_run.task_runner)
        self.assertIsNotNone(tracked_run.architect)
        self.assertIsNotNone(tracked_run.task_run)
        self.assertEqual(tracked_run.task_run.db_id, task_run_id)

        # Create two agents to step through the task
        architect = tracked_run.architect
        self.assertIsInstance(architect, MockArchitect, "Must use mock in testing")
        # Register a worker
        mock_worker_name = "MOCK_WORKER"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name)
        agent_id_1 = self.assert_agent_created(1)

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name)
        agent_id_2 = self.assert_agent_created(2)

        architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        architect.server.submit_mock_unit(agent_id_2, {"completed": True})

        # Give up to 5 seconds for whole mock task to complete
        start_time = time.time()
        self.operator._wait_for_runs_in_testing(TIMEOUT_TIME)
        self.assertLess(time.time() - start_time, TIMEOUT_TIME, "Task not completed in time")

        # Ensure the assignment is completed
        task_run = tracked_run.task_run
        assignment = task_run.get_assignments()[0]
        self.assertEqual(assignment.get_status(), AssignmentState.COMPLETED)

    @patch("mephisto.operations.operator.RUN_STATUS_POLL_TIME", 1.5)
    def test_run_job_not_concurrent(self):
        """Ensure that a job can be run that doesn't require connected workers"""
        self.operator = Operator(self.db)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=1, is_concurrent=False),
            provider=MockProviderArgs(requester_name=self.requester_name),
            architect=MockArchitectArgs(should_run_server=True),
            task=MOCK_TASK_ARGS,
        )
        self.operator.launch_task_run(OmegaConf.structured(config))
        tracked_runs = self.operator.get_running_task_runs()
        self.assertEqual(len(tracked_runs), 1, "Run not launched")
        task_run_id, tracked_run = list(tracked_runs.items())[0]

        self.assertIsNotNone(tracked_run)
        self.assertIsNotNone(tracked_run.task_launcher)
        self.assertIsNotNone(tracked_run.task_runner)
        self.assertIsNotNone(tracked_run.architect)
        self.assertIsNotNone(tracked_run.task_run)
        self.assertEqual(tracked_run.task_run.db_id, task_run_id)

        # Create two agents to step through the task
        architect = tracked_run.architect
        self.assertIsInstance(architect, MockArchitect, "Must use mock in testing")
        # Register a worker
        mock_worker_name = "MOCK_WORKER"

        self.assertEqual(len(tracked_run.task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name)
        agent_id_1 = self.assert_agent_created(1)

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name)
        agent_id_2 = self.assert_agent_created(2)

        architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        architect.server.submit_mock_unit(agent_id_2, {"completed": True})

        # Give up to 5 seconds for both tasks to complete
        start_time = time.time()
        self.operator._wait_for_runs_in_testing(TIMEOUT_TIME)
        self.assertLess(time.time() - start_time, TIMEOUT_TIME, "Task not completed in time")

        # Ensure the assignment is completed
        task_run = tracked_run.task_run
        assignment = task_run.get_assignments()[0]
        self.assertEqual(assignment.get_status(), AssignmentState.COMPLETED)

    @patch("mephisto.operations.operator.RUN_STATUS_POLL_TIME", 1.5)
    def test_patience_shutdown(self):
        """Ensure that a job shuts down if patience is exceeded"""
        self.operator = Operator(self.db)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=1, is_concurrent=False),
            provider=MockProviderArgs(requester_name=self.requester_name),
            architect=MockArchitectArgs(should_run_server=True),
            task=TaskRunArgs(
                task_title="title",
                task_description="This is a description",
                task_reward=0.3,
                task_tags="1,2,3",
                submission_timeout=5,
                no_submission_patience=1,  # Expire in a second
            ),
        )

        self.operator.launch_task_run(OmegaConf.structured(config))
        tracked_runs = self.operator.get_running_task_runs()
        self.assertEqual(len(tracked_runs), 1, "Run not launched")
        task_run_id, tracked_run = list(tracked_runs.items())[0]

        self.assertIsNotNone(tracked_run)
        self.assertIsNotNone(tracked_run.task_launcher)
        self.assertIsNotNone(tracked_run.task_runner)
        self.assertIsNotNone(tracked_run.architect)
        self.assertIsNotNone(tracked_run.task_run)
        self.assertEqual(tracked_run.task_run.db_id, task_run_id)

        # Give a few seconds for the operator to shutdown
        start_time = time.time()
        self.operator._wait_for_runs_in_testing(TIMEOUT_TIME)
        self.assertLess(time.time() - start_time, TIMEOUT_TIME, "Task shutdown not enacted in time")

        # Ensure the task run was forced to shut down
        task_run = tracked_run.task_run
        self.assertTrue(tracked_run.force_shutdown)
        assignment = task_run.get_assignments()[0]
        unit = assignment.get_units()[0]
        self.assertEqual(unit.get_status(), AssignmentState.EXPIRED)

    @patch("mephisto.operations.operator.RUN_STATUS_POLL_TIME", 1.5)
    def test_run_jobs_with_restrictions(self):
        """Ensure allowed_concurrent and maximum_units_per_worker work"""
        self.operator = Operator(self.db)
        provider_args = MockProviderArgs(requester_name=self.requester_name)
        architect_args = MockArchitectArgs(should_run_server=True)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=3, is_concurrent=True),
            provider=provider_args,
            architect=architect_args,
            task=TaskRunArgs(
                task_title="title",
                task_description="This is a description",
                task_reward="0.3",
                task_tags="1,2,3",
                maximum_units_per_worker=2,
                allowed_concurrent=1,
                task_name="max-unit-test",
            ),
        )
        self.operator.launch_task_run(OmegaConf.structured(config))
        tracked_runs = self.operator.get_running_task_runs()
        self.assertEqual(len(tracked_runs), 1, "Run not launched")
        task_run_id, tracked_run = list(tracked_runs.items())[0]

        self.assertIsNotNone(tracked_run)
        self.assertIsNotNone(tracked_run.task_launcher)
        self.assertIsNotNone(tracked_run.task_runner)
        self.assertIsNotNone(tracked_run.architect)
        self.assertIsNotNone(tracked_run.task_run)
        self.assertEqual(tracked_run.task_run.db_id, task_run_id)

        self.await_server_start(tracked_run.architect)

        # Create two agents to step through the task
        architect = tracked_run.architect
        self.assertIsInstance(architect, MockArchitect, "Must use mock in testing")
        # Register a worker
        mock_worker_name_1 = "MOCK_WORKER"

        self.assertEqual(len(tracked_run.task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        architect.server.register_mock_agent(mock_worker_name_1, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name_1)
        workers = self.db.find_workers(worker_name=mock_worker_name_1 + "_sandbox")
        worker_id_1 = workers[0].db_id
        agent_id_1 = self.assert_agent_created(1)

        # Try to register a second agent, which should fail due to concurrency
        mock_agent_details = "FAKE_ASSIGNMENT_2_FAILS"
        architect.server.register_mock_agent(mock_worker_name_1, mock_agent_details)
        self.await_channel_requests(tracked_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Second agent was created")

        # Register another worker
        mock_worker_name_2 = "MOCK_WORKER_2"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(mock_worker_name_2, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name_2)
        workers = self.db.find_workers(worker_name=mock_worker_name_2 + "_sandbox")
        worker_id_2 = workers[0].db_id
        agent_id_2 = self.assert_agent_created(2)

        architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        architect.server.submit_mock_unit(agent_id_2, {"completed": True})
        self.await_channel_requests(tracked_run)

        # wait for task to pass
        agents = self.db.find_agents()
        self.wait_for_complete_assignment(agents[1].get_unit().get_assignment(), 3)

        # Pass a second task as well
        mock_agent_details = "FAKE_ASSIGNMENT_3"
        architect.server.register_mock_agent(mock_worker_name_1, mock_agent_details)
        agent_id_3 = self.assert_agent_created(3)
        mock_agent_details = "FAKE_ASSIGNMENT_4"
        architect.server.register_mock_agent(mock_worker_name_2, mock_agent_details)
        agent_id_4 = self.assert_agent_created(4)

        architect.server.send_agent_act(agent_id_3, {"text": "message3"})
        architect.server.send_agent_act(agent_id_4, {"text": "message4"})
        architect.server.submit_mock_unit(agent_id_3, {"completed": True})
        architect.server.submit_mock_unit(agent_id_4, {"completed": True})
        self.await_channel_requests(tracked_run)

        # wait for task to pass
        agents = self.db.find_agents()
        self.wait_for_complete_assignment(agents[3].get_unit().get_assignment(), 3)

        # Both workers should have saturated their tasks, and not be granted agents
        mock_agent_details = "FAKE_ASSIGNMENT_5"
        architect.server.register_mock_agent(mock_worker_name_1, mock_agent_details)
        self.await_channel_requests(tracked_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 4, "Additional agent was created")
        architect.server.register_mock_agent(mock_worker_name_2, mock_agent_details)
        self.await_channel_requests(tracked_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 4, "Additional agent was created")

        # new workers should be able to work on these just fine though
        mock_worker_name_3 = "MOCK_WORKER_3"
        mock_worker_name_4 = "MOCK_WORKER_4"

        # Register agents from new workers
        mock_agent_details = "FAKE_ASSIGNMENT_5"
        architect.server.register_mock_agent(mock_worker_name_3, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name_3)
        agent_id_5 = self.assert_agent_created(5)
        mock_agent_details = "FAKE_ASSIGNMENT_6"
        architect.server.register_mock_agent(mock_worker_name_4, mock_agent_details)
        self.assert_sandbox_worker_created(mock_worker_name_4)
        agent_id_6 = self.assert_agent_created(6)

        architect.server.send_agent_act(agent_id_5, {"text": "message5"})
        architect.server.send_agent_act(agent_id_6, {"text": "message6"})
        architect.server.submit_mock_unit(agent_id_5, {"completed": True})
        architect.server.submit_mock_unit(agent_id_6, {"completed": True})
        self.await_channel_requests(tracked_run)

        # wait for task to pass
        agents = self.db.find_agents()
        self.wait_for_complete_assignment(agents[5].get_unit().get_assignment(), 3)

        # Give up to 5 seconds for whole mock task to complete
        start_time = time.time()
        self.operator._wait_for_runs_in_testing(TIMEOUT_TIME)
        self.assertLess(time.time() - start_time, TIMEOUT_TIME, "Task not completed in time")

        self.operator.shutdown()
        # Create a new operator, shutdown is a one-time thing
        self.operator = Operator(self.db)

        # Ensure all assignments are completed
        task_run = tracked_run.task_run
        assignments = task_run.get_assignments()
        for assignment in assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.COMPLETED)

        # Create a new task
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=1, is_concurrent=True),
            provider=MockProviderArgs(requester_name=self.requester_name),
            architect=MockArchitectArgs(should_run_server=True),
            task=TaskRunArgs(
                task_title="title",
                task_description="This is a description",
                task_reward="0.3",
                task_tags="1,2,3",
                maximum_units_per_worker=2,
                allowed_concurrent=1,
                task_name="max-unit-test",
            ),
        )
        self.operator.launch_task_run(OmegaConf.structured(config))
        tracked_runs = self.operator.get_running_task_runs()
        self.assertEqual(len(tracked_runs), 1, "Run not launched")
        task_run_id, tracked_run = list(tracked_runs.items())[0]
        self.await_server_start(tracked_run.architect)
        architect = tracked_run.architect

        # Workers one and two still shouldn't be able to make agents
        mock_agent_details = "FAKE_ASSIGNMENT_7"
        architect.server.register_mock_agent(mock_worker_name_1, mock_agent_details)
        self.await_channel_requests(tracked_run)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents),
            6,
            "Additional agent was created for worker exceeding max units",
        )
        mock_agent_details = "FAKE_ASSIGNMENT_7"
        architect.server.register_mock_agent(mock_worker_name_2, mock_agent_details)
        self.await_channel_requests(tracked_run)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents),
            6,
            "Additional agent was created for worker exceeding max units",
        )

        # Three and four should though
        mock_agent_details = "FAKE_ASSIGNMENT_7"
        architect.server.register_mock_agent(mock_worker_name_3, mock_agent_details)
        agent_id_7 = self.assert_agent_created(7)
        mock_agent_details = "FAKE_ASSIGNMENT_8"
        architect.server.register_mock_agent(mock_worker_name_4, mock_agent_details)
        agent_id_8 = self.assert_agent_created(8)

        architect.server.send_agent_act(agent_id_7, {"text": "message7"})
        architect.server.send_agent_act(agent_id_8, {"text": "message8"})
        architect.server.submit_mock_unit(agent_id_7, {"completed": True})
        architect.server.submit_mock_unit(agent_id_8, {"completed": True})
        self.await_channel_requests(tracked_run)

        # Ensure the task run completed and that all assignments are done
        start_time = time.time()
        self.operator._wait_for_runs_in_testing(TIMEOUT_TIME)
        self.assertLess(time.time() - start_time, TIMEOUT_TIME, "Task not completed in time")
        task_run = tracked_run.task_run
        assignments = task_run.get_assignments()
        for assignment in assignments:
            self.assertEqual(assignment.get_status(), AssignmentState.COMPLETED)


class TestOperatorLocal(OperatorBaseTest, unittest.TestCase):
    DB_CLASS = LocalMephistoDB


class TestOperatorSingleton(OperatorBaseTest, unittest.TestCase):
    DB_CLASS = MephistoSingletonDB


if __name__ == "__main__":
    unittest.main()
