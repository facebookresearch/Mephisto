#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import List, Type, ClassVar, cast
import tempfile
import os
import shutil
import threading
import time
from mephisto.abstractions.blueprint import (
    Blueprint,
    AgentState,
    TaskRunner,
    TaskBuilder,
)
from mephisto.abstractions._subcomponents.task_runner import RunningAssignment
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.task_run import TaskRun
from mephisto.utils.testing import get_test_task_run
from mephisto.abstractions.providers.mock.mock_agent import MockAgent
from mephisto.data_model.agent import Agent
from mephisto.operations.hydra_config import MephistoConfig
from omegaconf import OmegaConf


class BlueprintTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable for a blueprint. Runs the tests on the Blueprint,
    which is the entry point the components to run the task.
    """

    BlueprintClass: ClassVar[Type[Blueprint]]
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

    def assignment_is_tracked(
        self, task_runner: TaskRunner, assignment: Assignment
    ) -> bool:
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
        # TODO(#97) we need to actually pull the task type from the Blueprint
        self.task_run = TaskRun.get(self.db, get_test_task_run(self.db))
        # TODO(#97) create a mock agent with the given task type?
        self.TaskRunnerClass = self.BlueprintClass.TaskRunnerClass
        self.AgentStateClass = self.BlueprintClass.AgentStateClass
        self.TaskBuilderClass = self.BlueprintClass.TaskBuilderClass

    def tearDown(self) -> None:
        """
        tearDown should clear up anything that was set up or
        used in any of the tests in this class.

        Generally this means cleaning up the database that was
        set up.
        """
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    def _get_init_task_runner(self) -> TaskRunner:
        """Get an initialized task runner of TaskRunnerClass"""
        args = self.BlueprintClass.ArgsClass()
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        shared_state = self.BlueprintClass.SharedStateClass()
        return self.TaskRunnerClass(self.task_run, config, shared_state)

    def _get_init_task_builder(self) -> TaskBuilder:
        """Get an initialized task runner of TaskBuilderClass"""
        args = self.BlueprintClass.ArgsClass()
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        shared_state = self.BlueprintClass.SharedStateClass()
        return self.TaskBuilderClass(self.task_run, config)

    def prep_mock_agents_to_complete(self, agents: List["MockAgent"]) -> None:
        """Handle initializing mock agents to be able to pass their task"""
        pass

    def test_options(self) -> None:
        """Test the default options, and try to break the initialization"""
        # TODO(#94?) implement with options implementations
        pass

    def test_ensure_valid_statuses(self):
        """Test that all the statuses are represented"""
        a_state = self.BlueprintClass.AgentStateClass
        found_valid = a_state.valid()
        found_complete = a_state.complete()
        found_keys = [k for k in dir(a_state) if k.startswith("STATUS_")]
        found_vals = [getattr(a_state, k) for k in found_keys]
        for v in found_vals:
            self.assertIn(
                v, found_valid, f"Expected to find {v} in valid list {found_valid}"
            )
        for v in found_complete:
            self.assertIn(
                v,
                found_vals,
                f"Expected to find {v} in {a_state} attributes, not in {found_vals}",
            )
        for v in found_valid:
            self.assertIn(
                v,
                found_vals,
                f"Expected to find {v} in {a_state} attributes, not in {found_vals}",
            )

    def test_has_required_class_members(self) -> None:
        """Ensures that the BluePrint is well-formatted"""
        self.assertTrue(
            issubclass(self.AgentStateClass, AgentState),
            "Implemented AgentStateClass does not extend AgentState",
        )
        self.assertNotEqual(
            self.AgentStateClass,
            AgentState,
            "Can not use base AgentState in a Blueprint implementation",
        )
        self.assertTrue(
            issubclass(self.TaskRunnerClass, TaskRunner),
            "Implemented TaskRunnerClass does not extend TaskRunner",
        )
        self.assertNotEqual(
            self.TaskRunnerClass,
            TaskRunner,
            "Can not use base TaskRunner in a Blueprint implementation",
        )
        self.assertTrue(
            issubclass(self.TaskBuilderClass, TaskBuilder),
            "Implemented TaskBuilderClass does not extend TaskBuilder",
        )
        self.assertNotEqual(
            self.TaskBuilderClass,
            TaskBuilder,
            "Can not use base TaskBuilder in a Blueprint implementation",
        )
        # TODO(#94?) implement getting the defaults of TaskRunnerClass.get_extra_options() when
        # options are improved

    def test_abstract_initialization_works(self) -> None:
        """
        Test that initialization from the abstract class produces the
        correct class.
        """
        args = self.BlueprintClass.ArgsClass()
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        shared_state = self.BlueprintClass.SharedStateClass()
        runner = TaskRunner(self.task_run, config, shared_state)  # type: ignore
        self.assertTrue(isinstance(runner, self.TaskRunnerClass))
        builder = TaskBuilder(self.task_run, config)  # type: ignore
        self.assertTrue(isinstance(builder, self.TaskBuilderClass))

    def test_can_init_subclasses(self) -> None:
        """Ensure the subclasses of a Blueprint can be properly initialized"""
        task_runner = self._get_init_task_runner()
        task_builder = self._get_init_task_builder()
        # TODO(#97) uncomment after creating a mock agent as part of this test
        # agent_state = self.AgentStateClass(self.agent)

    def test_can_build_task(self) -> None:
        """Ensure a task can be built up from scratch in the given directory"""
        task_builder = self._get_init_task_builder()
        task_builder.build_in_dir(self.build_dir)
        self.assertTrue(self.task_is_built(self.build_dir))

    def test_can_run_task(self) -> None:
        """Ensure that a task can be run to completion in the basic case"""
        task_runner = self._get_init_task_runner()
        assignment = self.get_test_assignment()
        mock_agents: List["MockAgent"] = [
            cast("MockAgent", u.get_assigned_agent()) for u in assignment.get_units()
        ]

        self.prep_mock_agents_to_complete(mock_agents)

        agents: List["Agent"] = [cast("Agent", a) for a in mock_agents]
        task_runner.running_assignments[assignment.db_id] = RunningAssignment(
            None, None, None  # type: ignore
        )
        task_runner._launch_and_run_assignment(assignment, agents)
        self.assertTrue(self.assignment_completed_successfully(assignment))

    def test_can_exit_gracefully(self) -> None:
        """Ensure that a task can be run to completion when an agent disconnects"""
        task_runner = self._get_init_task_runner()
        assignment = self.get_test_assignment()
        fail_agent = assignment.get_units()[0].get_assigned_agent()
        assert fail_agent is not None, "No agent set for first unit of test assignment"
        assert isinstance(fail_agent, MockAgent), "Agent must be mock agent for testing"
        fail_agent.mark_disconnected()
        try:
            task_runner._launch_and_run_assignment(assignment, [fail_agent])
        except Exception as e:
            task_runner.cleanup_assignment(assignment)

        self.assertFalse(self.assignment_completed_successfully(assignment))
        self.assertFalse(self.assignment_is_tracked(task_runner, assignment))
