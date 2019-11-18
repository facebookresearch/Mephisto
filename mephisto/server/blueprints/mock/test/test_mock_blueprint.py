#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from typing import Type, ClassVar
from mephisto.data_model.test.task_runner_tester import BlueprintTests
from mephisto.data_model.task_runner import TaskRunner
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner

from mephisto.data_model.agent_state import AgentState
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.task_runner import TaskRunner
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.task import TaskRun
from mephisto.data_model.test.utils import get_test_task_run

# TODO be able to pull the assignment mocking process out from
# somewhere else, such as the worker pool or matcher
from mephisto.providers.mock.mock_agent import MockAgent
from mephisto.providers.mock.mock_unit import MockUnit
from mephisto.providers.mock.mock_worker import MockWorker
from mephisto.providers.mock.provider_type import PROVIDER_TYPE as MOCK_PROVIDER_TYPE


class MockBlueprintTests(BlueprintTests):
    """
    This class contains the basic data model tests that should
    be passable for a blueprint. Runs the tests on the TaskRunner,
    which is the entry point for all blueprints.
    """

    TaskRunnerClass = MockTaskRunner
    db: LocalMephistoDB
    data_dir: str
    build_dir: str

    def task_is_built(self, build_dir) -> bool:
        """Ensure that a properly built version of this task is present in this dir"""
        expected_build_path = os.path.join(build_dir, MockTaskRunner.BUILT_FILE)
        if not os.path.exists(expected_build_path):
            return False
        with open(expected_build_path, 'r') as built_file:
            file_contents = built_file.read()
            return file_contents.strip() == MockTaskRunner.BUILT_MESSAGE

    def assignment_completed_successfully(self, assignment: Assignment) -> bool:
        """Validate that an assignment is able to be run successfully"""
        return assignment.get_status() == AssignmentState.COMPLETED

    def get_test_assignment(self) -> Assignment:
        """Create a test assignment for self.task_run using mock agents"""
        task_run = self.task_run
        assignment_id = self.db.new_assignment(task_run.db_id)
        assign = Assignment(self.db, assignment_id)
        # TODO move mock worker assignment to a more appropriate location
        unit_id = self.db.new_unit(assignment_id, 0, 0, MOCK_PROVIDER_TYPE)
        unit = MockUnit(self.db, unit_id)
        worker_id = self.db.new_worker('MOCK_TEST_WORKER', MOCK_PROVIDER_TYPE)
        worker = MockWorker(self.db, worker_id)
        # TODO pull the task type name from the right location
        agent_id = self.db.new_agent(worker_id, unit_id, "mock", MOCK_PROVIDER_TYPE)
        Agent = MockAgent(self.db, agent_id)
        return assign

    def assignment_is_tracked(self, assignment: Assignment) -> bool:
        """
        Return whether or not this task is currently being tracked (run)
        by the given task runner. This should be false unless
        run_assignment is still ongoing for a task.
        """
        assert isinstance(self.task_runner, MockTaskRunner), 'Must be a mock runner'
        return assignment.db_id in self.task_runner.tracked_tasks

    # TODO are there any other unit tests we'd like to have?


if __name__ == "__main__":
    unittest.main()
