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

from mephisto.abstractions.test.utils import get_test_requester
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
from mephisto.data_model.task_config import TaskConfigArgs
from omegaconf import OmegaConf

TIMEOUT_TIME = 10


MOCK_TASK_ARGS = TaskConfigArgs(
    task_title="title",
    task_description="This is a description",
    task_reward="0.3",
    task_tags="1,2,3",
)


class OperatorBaseTest(object):
    """
    Unit testing for the Mephisto Operator
    """

    DB_CLASS = None

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)
        self.requester_name, _req_id = get_test_requester(self.db)
        self.operator = None

    def tearDown(self):
        if self.operator is not None:
            self.operator.shutdown()
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)
        self.assertTrue(
            len(threading.enumerate()) == 1,
            f"Expected only main thread at teardown, found {threading.enumerate()}",
        )

    def wait_for_complete_assignment(self, assignment, timeout: int):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if assignment.get_status() == AssignmentState.COMPLETED:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, timeout, "Assignment not completed in time"
        )

    def await_server_start(self, architect: "MockArchitect"):
        start_time = time.time()
        assert architect.server is not None, "Cannot wait on empty server"
        while time.time() - start_time < 5:
            if len(architect.server.subs) > 0:
                break
            time.sleep(0.1)
        self.assertLess(time.time() - start_time, 5, "Mock server not up in time")

    def test_initialize_supervisor(self):
        """Quick test to ensure that the operator can be initialized"""
        self.operator = Operator(self.db)

    def test_run_job_concurrent(self):
        """Ensure that the supervisor object can even be created"""
        self.operator = Operator(self.db)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=1, is_concurrent=True),
            provider=MockProviderArgs(requester_name=self.requester_name),
            architect=MockArchitectArgs(should_run_server=True),
            task=MOCK_TASK_ARGS,
        )
        self.operator.validate_and_run_config(OmegaConf.structured(config))
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
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id = workers[0].db_id

        self.assertEqual(len(tracked_run.task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")
        agent = agents[0]
        self.assertIsNotNone(agent)

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id = workers[0].db_id

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(worker_id, mock_agent_details)

        # Give up to 5 seconds for whole mock task to complete
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_TIME:
            if len(self.operator.get_running_task_runs()) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Task not completed in time"
        )

        # Ensure the assignment is completed
        task_run = tracked_run.task_run
        assignment = task_run.get_assignments()[0]
        self.assertEqual(assignment.get_status(), AssignmentState.COMPLETED)

    def test_run_job_not_concurrent(self):
        """Ensure that the supervisor object can even be created"""
        self.operator = Operator(self.db)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=1, is_concurrent=False),
            provider=MockProviderArgs(requester_name=self.requester_name),
            architect=MockArchitectArgs(should_run_server=True),
            task=MOCK_TASK_ARGS,
        )
        self.operator.validate_and_run_config(OmegaConf.structured(config))
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
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id = workers[0].db_id

        self.assertEqual(len(tracked_run.task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")
        agent = agents[0]
        self.assertIsNotNone(agent)

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id = workers[0].db_id

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(worker_id, mock_agent_details)

        # Give up to 5 seconds for both tasks to complete
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_TIME:
            if len(self.operator.get_running_task_runs()) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Task not completed in time"
        )

        # Ensure the assignment is completed
        task_run = tracked_run.task_run
        assignment = task_run.get_assignments()[0]
        self.assertEqual(assignment.get_status(), AssignmentState.COMPLETED)

    def test_run_jobs_with_restrictions(self):
        """Ensure allowed_concurrent and maximum_units_per_worker work"""
        self.operator = Operator(self.db)
        provider_args = MockProviderArgs(requester_name=self.requester_name)
        architect_args = MockArchitectArgs(should_run_server=True)
        config = MephistoConfig(
            blueprint=MockBlueprintArgs(num_assignments=3, is_concurrent=True),
            provider=provider_args,
            architect=architect_args,
            task=TaskConfigArgs(
                task_title="title",
                task_description="This is a description",
                task_reward="0.3",
                task_tags="1,2,3",
                maximum_units_per_worker=2,
                allowed_concurrent=1,
                task_name="max-unit-test",
            ),
        )
        self.operator.validate_and_run_config(OmegaConf.structured(config))
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
        mock_worker_name = "MOCK_WORKER"
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id_1 = workers[0].db_id

        self.assertEqual(len(tracked_run.task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        architect.server.register_mock_agent(worker_id_1, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")
        agent = agents[0]
        self.assertIsNotNone(agent)

        # Try to register a second agent, which should fail due to concurrency
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(worker_id_1, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Second agent was created")

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id_2 = workers[0].db_id

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        architect.server.register_mock_agent(worker_id_2, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Second agent was not created")

        # wait for task to pass
        self.wait_for_complete_assignment(agents[1].get_unit().get_assignment(), 3)

        # Pass a second task as well
        mock_agent_details = "FAKE_ASSIGNMENT_3"
        architect.server.register_mock_agent(worker_id_1, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 3, "Agent was not created properly")
        mock_agent_details = "FAKE_ASSIGNMENT_4"
        architect.server.register_mock_agent(worker_id_2, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 4, "Fourth agent was not created")

        # wait for task to pass
        self.wait_for_complete_assignment(agents[3].get_unit().get_assignment(), 3)

        # Both workers should have saturated their tasks, and not be granted agents
        mock_agent_details = "FAKE_ASSIGNMENT_5"
        architect.server.register_mock_agent(worker_id_1, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 4, "Additional agent was created")
        architect.server.register_mock_agent(worker_id_2, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 4, "Additional agent was created")

        # new workers should be able to work on these just fine though
        mock_worker_name = "MOCK_WORKER_3"
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id_3 = workers[0].db_id
        mock_worker_name = "MOCK_WORKER_4"
        architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id_4 = workers[0].db_id

        # Register agents from new workers
        mock_agent_details = "FAKE_ASSIGNMENT_5"
        architect.server.register_mock_agent(worker_id_3, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 5, "Additional agent was not created")
        mock_agent_details = "FAKE_ASSIGNMENT_6"
        architect.server.register_mock_agent(worker_id_4, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 6, "Additional agent was not created")

        # wait for task to pass
        self.wait_for_complete_assignment(agents[5].get_unit().get_assignment(), 3)

        # Give up to 5 seconds for whole mock task to complete
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_TIME:
            if len(self.operator.get_running_task_runs()) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Task not completed in time"
        )

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
            task=TaskConfigArgs(
                task_title="title",
                task_description="This is a description",
                task_reward="0.3",
                task_tags="1,2,3",
                maximum_units_per_worker=2,
                allowed_concurrent=1,
                task_name="max-unit-test",
            ),
        )
        self.operator.validate_and_run_config(OmegaConf.structured(config))
        tracked_runs = self.operator.get_running_task_runs()
        self.assertEqual(len(tracked_runs), 1, "Run not launched")
        task_run_id, tracked_run = list(tracked_runs.items())[0]
        self.await_server_start(tracked_run.architect)
        architect = tracked_run.architect

        # Workers one and two still shouldn't be able to make agents
        mock_agent_details = "FAKE_ASSIGNMENT_7"
        architect.server.register_mock_agent(worker_id_1, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents),
            6,
            "Additional agent was created for worker exceeding max units",
        )
        mock_agent_details = "FAKE_ASSIGNMENT_7"
        architect.server.register_mock_agent(worker_id_2, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents),
            6,
            "Additional agent was created for worker exceeding max units",
        )

        # Three and four should though
        mock_agent_details = "FAKE_ASSIGNMENT_7"
        architect.server.register_mock_agent(worker_id_3, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 7, "Additional agent was not created")
        mock_agent_details = "FAKE_ASSIGNMENT_8"
        architect.server.register_mock_agent(worker_id_4, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 8, "Additional agent was not created")

        # Ensure the task run completed and that all assignments are done
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_TIME:
            if len(self.operator.get_running_task_runs()) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Task not completed in time"
        )
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
