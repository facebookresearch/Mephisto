#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from typing import Type, ClassVar, List
from mephisto.abstractions.test.blueprint_tester import BlueprintTests
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.abstractions.blueprints.mock.mock_task_builder import MockTaskBuilder
from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.blueprint import (
    Blueprint,
    AgentState,
    TaskRunner,
    TaskBuilder,
)
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.task_run import TaskRun
from mephisto.utils.testing import get_test_task_run

# TODO(#97) Update operator to be able to provide mock setups to test against a blueprint
from mephisto.abstractions.providers.mock.mock_agent import MockAgent
from mephisto.abstractions.providers.mock.mock_unit import MockUnit
from mephisto.abstractions.providers.mock.mock_worker import MockWorker
from mephisto.abstractions.providers.mock.provider_type import (
    PROVIDER_TYPE as MOCK_PROVIDER_TYPE,
)


class MockBlueprintTests(BlueprintTests):
    """
    This class contains the basic data model tests that should
    be passable for a blueprint. Runs the tests on the MockBlueprint,
    which is the entry point for all blueprints.
    """

    BlueprintClass = MockBlueprint
    db: LocalMephistoDB
    data_dir: str
    build_dir: str

    def task_is_built(self, build_dir) -> bool:
        """Ensure that a properly built version of this task is present in this dir"""
        expected_build_path = os.path.join(build_dir, MockTaskBuilder.BUILT_FILE)
        if not os.path.exists(expected_build_path):
            return False
        with open(expected_build_path, "r") as built_file:
            file_contents = built_file.read()
            return file_contents.strip() == MockTaskBuilder.BUILT_MESSAGE

    def assignment_completed_successfully(self, assignment: Assignment) -> bool:
        """Validate that an assignment is able to be run successfully"""
        return assignment.get_status() == AssignmentState.COMPLETED

    def get_test_assignment(self) -> Assignment:
        """Create a test assignment for self.task_run using mock agents"""
        task_run = self.task_run
        assignment_id = self.db.new_assignment(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
        )
        assign = Assignment.get(self.db, assignment_id)
        unit_id = self.db.new_unit(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            assignment_id,
            0,
            0,
            task_run.provider_type,
            task_run.task_type,
        )
        unit = MockUnit.get(self.db, unit_id)
        worker_id = self.db.new_worker("MOCK_TEST_WORKER", MOCK_PROVIDER_TYPE)
        worker = MockWorker.get(self.db, worker_id)
        agent_id = self.db.new_agent(
            worker.db_id,
            unit_id,
            task_run.task_id,
            task_run.db_id,
            assignment_id,
            task_run.task_type,
            task_run.provider_type,
        )
        Agent = MockAgent.get(self.db, agent_id)
        return assign

    def assignment_is_tracked(self, task_runner: TaskRunner, assignment: Assignment) -> bool:
        """
        Return whether or not this task is currently being tracked (run)
        by the given task runner. This should be false unless
        run_assignment is still ongoing for a task.
        """
        assert isinstance(task_runner, MockTaskRunner), "Must be a mock runner"
        return assignment.db_id in task_runner.tracked_tasks

    def prep_mock_agents_to_complete(self, agents: List["MockAgent"]) -> None:
        """Handle initializing mock agents to be able to pass their task"""
        for agent in agents:
            agent.enqueue_mock_live_update({"text": "message"})
            agent.enqueue_mock_submit_event({"submitted": True})

    # TODO(#97) are there any other unit tests we'd like to have?


if __name__ == "__main__":
    unittest.main()
