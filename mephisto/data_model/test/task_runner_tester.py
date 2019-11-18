#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import Type, ClassVar
import tempfile
import os
import shutil
import threading
import time
from mephisto.data_model.agent_state import AgentState
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.task_runner import TaskRunner
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.task import TaskRun
from mephisto.data_model.test.utils import get_test_task_run


class BlueprintTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable for a blueprint. Runs the tests on the TaskRunner,
    which is the entry point for all blueprints.
    """

    TaskRunnerClass: ClassVar[Type[TaskRunner]]
    db: LocalMephistoDB
    data_dir: str
    build_dir: str

    @classmethod
    def setUpClass(cls):
        """
        Only run tests on subclasses of this class, as this class is just defining the
        testing interface and the tests to run any class that implements the TaskRunner
        interface
        """
        if cls is BlueprintTests:
            raise unittest.SkipTest("Skip BlueprintTests tests, it's a base class")
        super(BlueprintTests, cls).setUpClass()

    # Implementations of this test suite should implement the following methods.
    # See the mock blueprint for examples

    def task_is_built(self, build_dir) -> bool:
        """Ensure that a properly built version of this task is present in this dir"""
        raise NotImplementedError()

    def assignment_completed_successfully(self, assignment: Assignment) -> bool:
        """Validate that an assignment is able to be run successfully"""
        raise NotImplementedError()

    def get_test_assignment(self) -> Assignment:
        """Create a test assignment for self.task_run using mock agents"""
        raise NotImplementedError()

    def assignment_is_tracked(self, assignment: Assignment) -> bool:
        """
        Return whether or not this task is currently being tracked (run)
        by the given task runner. This should be false unless
        run_assignment is still ongoing for a task.
        """
        raise NotImplementedError()

    # Test suite methods

    def setUp(self) -> None:
        """
        Setup should put together any requirements for starting the database for a test.
        """
        self.data_dir = tempfile.mkdtemp()
        self.build_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.task_run = TaskRun(self.db, get_test_task_run(self.db))
        self.task_runner = self._get_init_task_runner()

    def tearDown(self) -> None:
        """
        tearDown should clear up anything that was set up or
        used in any of the tests in this class.

        Generally this means cleaning up the database that was
        set up.
        """
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    def _get_agent_state_class(self) -> Type[AgentState]:
        """Return the agent state class being tested"""
        return self.TaskRunnerClass.AgentStateClass

    def _get_init_task_runner(self) -> TaskRunner:
        """Get an initialized task runner of TaskRunnerClass"""
        # TODO call get_extra_options and apply the defaults here
        return self.TaskRunnerClass(self.task_run, {})

    def test_options(self) -> None:
        """Test the default options, and try to break the initialization"""
        # TODO implement with options implementations
        pass

    def test_has_required_class_members(self) -> None:
        """Ensures that the TaskRunner is well-formatted"""
        ImplementedAgentState = self._get_agent_state_class()
        self.assertTrue(
            issubclass(ImplementedAgentState, AgentState),
            "Implemented AgentStateClass does not extend AgentState",
        )
        self.assertNotEqual(
            ImplementedAgentState,
            AgentState,
            "Can not use base AgentState in a TaskRunner implementation",
        )
        self.assertIn(
            "mock",
            self.TaskRunnerClass.supported_architects,
            "Must support at least the mock architecture for testing",
        )
        # TODO implement getting the defaults of TaskRunnerClass.get_extra_options() when
        # options are improved

    def test_can_build_task(self) -> None:
        """Ensure a task can be built up from scratch in the given directory"""
        task_runner = self.task_runner
        task_runner.build_in_dir(self.task_run, self.build_dir)
        self.assertTrue(self.task_is_built(self.build_dir))

    def test_can_run_task(self) -> None:
        """Ensure that a task can be run to completion in the basic case"""
        task_runner = self.task_runner
        assignment = self.get_test_assignment()
        task_runner.run_assignment(assignment)
        self.assertTrue(self.assignment_completed_successfully(assignment))

    def test_can_exit_gracefully(self) -> None:
        """Ensure that a task can be run to completion when an agent disconnects"""
        task_runner = self.task_runner
        assignment = self.get_test_assignment()
        fail_agent = assignment.get_units()[0].get_assigned_agent()
        assert fail_agent is not None, "No agent set for first unit of test assignment"
        fail_agent.mark_disconnected()
        try:
            task_runner.run_assignment(assignment)
        except Exception as e:
            task_runner.cleanup_assignment(assignment)

        self.assertFalse(self.assignment_completed_successfully(assignment))
        self.assertFalse(self.assignment_is_tracked(assignment))

    def test_run_tracked(self) -> None:
        """Run a task in a thread, ensure we see it is being tracked"""
        task_runner = self.task_runner
        assignment = self.get_test_assignment()
        task_thread = threading.Thread(
            target=task_runner.run_assignment, args=(assignment,)
        )
        self.assertFalse(self.assignment_is_tracked(assignment))
        task_thread.start()
        time.sleep(0.1)  # Sleep to give the task_runner time to register
        self.assertTrue(self.assignment_is_tracked(assignment))
        task_thread.join()
        self.assertFalse(self.assignment_is_tracked(assignment))
        self.assertTrue(self.assignment_completed_successfully(assignment))
