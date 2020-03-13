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

from mephisto.data_model.test.utils import get_test_requester
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from mephisto.server.architects.mock_architect import MockArchitect


class TestOperator(unittest.TestCase):
    """
    Unit testing for the Mephisto Supervisor
    """

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.requester_name, _req_id = get_test_requester(self.db)
        self.operator = None

    def tearDown(self):
        if self.operator is not None:
            self.operator.shutdown()
        self.db.shutdown()
        shutil.rmtree(self.data_dir)
        self.assertTrue(
            len(threading.enumerate()) == 1,
            f"Expected only main thread at teardown, found {threading.enumerate()}",
        )

    def test_initialize_supervisor(self):
        """Quick test to ensure that the operator can be initialized"""
        self.operator = Operator(self.db)

    def test_run_job_concurrent(self):
        """Ensure that the supervisor object can even be created"""
        self.operator = Operator(self.db)
        ARG_STRING = (
            "--blueprint-type mock "
            "--architect-type mock "
            f"--requester-name {self.requester_name} "
            "--num-assignments 1 "
            "--task-title title "
            "--task-description description "
            "--task-reward 0.3 "
            "--task-tags 1,2,3 "
            "--should-run-server true "
            "--is-concurrent true "
        )
        self.operator.parse_and_launch_run(shlex.split(ARG_STRING))
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
        TIMEOUT_TIME = 3
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
        ARG_STRING = (
            "--blueprint-type mock "
            "--architect-type mock "
            f"--requester-name {self.requester_name} "
            "--num-assignments 1 "
            "--task-title title "
            "--task-description description "
            "--task-reward 0.3 "
            "--task-tags 1,2,3 "
            "--should-run-server true "
            "--is-concurrent false "
        )
        self.operator.parse_and_launch_run(shlex.split(ARG_STRING))
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
        TIMEOUT_TIME = 3
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
