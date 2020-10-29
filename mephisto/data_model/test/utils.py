#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import shutil
import tempfile
from abc import ABC

from typing import Optional, Tuple, ClassVar, Type, List

from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.task_launcher import TaskLauncher
from mephisto.data_model.blueprint import SharedTaskState

from mephisto.data_model.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)

from mephisto.data_model.agent import Agent
from mephisto.data_model.assignment import Unit, Assignment, InitializationData
from mephisto.data_model.task_config import TaskConfig
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task, TaskRun
from omegaconf import OmegaConf
import json

from mephisto.providers.mock.mock_provider import MockProviderArgs, MockProvider
from mephisto.server.blueprints.mock.mock_blueprint import MockBlueprintArgs
from mephisto.server.architects.mock_architect import MockArchitectArgs, MockArchitect
from mephisto.data_model.task_config import TaskConfigArgs
from mephisto.core.hydra_config import MephistoConfig
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner

MOCK_TASK_ARGS = TaskConfigArgs(
    task_title="title",
    task_description="This is a description",
    task_reward="0.3",
    task_tags="1,2,3",
)

MOCK_PROVIDER_ARGS = MockProviderArgs()
MOCK_ARCHITECT_ARGS = MockArchitectArgs()
MOCK_BLUEPRINT_ARGS = MockBlueprintArgs()

MOCK_CONFIG = MephistoConfig(
    provider=MOCK_PROVIDER_ARGS,
    blueprint=MOCK_BLUEPRINT_ARGS,
    architect=MOCK_ARCHITECT_ARGS,
    task=MOCK_TASK_ARGS,
)


def get_test_project(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a project for tests"""
    project_name = "test_project"
    project_id = db.new_project(project_name)
    return project_name, project_id


def get_test_worker(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a worker for tests"""
    worker_name = "test_worker"
    provider_type = "mock"
    worker_id = db.new_worker(worker_name, provider_type)
    return worker_name, worker_id


def get_test_requester(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a requester for tests"""
    requester_name = "test_requester"
    provider_type = "mock"
    requester_id = db.new_requester(requester_name, provider_type)
    return requester_name, requester_id


def get_test_task(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a task for tests"""
    task_name = "test_task"
    task_type = "mock"
    task_id = db.new_task(task_name, task_type)
    return task_name, task_id


def get_test_task_run(db: MephistoDB) -> str:
    """Helper to create a task run for tests"""
    task_name, task_id = get_test_task(db)
    requester_name, requester_id = get_test_requester(db)
    init_params = OmegaConf.to_yaml(OmegaConf.structured(MOCK_CONFIG))
    return db.new_task_run(
        task_id, requester_id, json.dumps(init_params), "mock", "mock"
    )


def get_test_assignment(db: MephistoDB) -> str:
    """Helper to create an assignment for tests"""
    task_run_id = get_test_task_run(db)
    task_run = TaskRun(db, task_run_id)
    return db.new_assignment(
        task_run.task_id,
        task_run_id,
        task_run.requester_id,
        task_run.task_type,
        task_run.provider_type,
    )


def get_test_unit(db: MephistoDB, unit_index=0) -> str:
    # Check creation and retrieval of a unit
    assignment_id = get_test_assignment(db)
    pay_amount = 15.0
    assignment = Assignment(db, assignment_id)
    return db.new_unit(
        assignment.task_id,
        assignment.task_run_id,
        assignment.requester_id,
        assignment.db_id,
        0,
        pay_amount,
        assignment.provider_type,
        assignment.task_type,
    )


def get_test_agent(db: MephistoDB, unit_id=None) -> str:
    # Check creation and retrieval of a agent
    worker_name, worker_id = get_test_worker(db)
    if unit_id is None:
        unit_id = get_test_unit(db)
    provider_type = "mock"
    task_type = "mock"
    unit = Unit(db, unit_id)
    return db.new_agent(
        worker_id,
        unit.db_id,
        unit.task_id,
        unit.task_run_id,
        unit.assignment_id,
        unit.task_type,
        unit.provider_type,
    )


def make_completed_unit(db: MephistoDB) -> str:
    """
    Creates a completed unit for the most recently created task run
    using some worker. Assumes
    """
    workers = db.find_workers()
    assert len(workers) > 0, "Must have at least one worker in database"
    worker = workers[-1]
    task_runs = db.find_task_runs(is_completed=False)
    assert len(task_runs) > 0, "Must be at least one incomplete task run"
    task_run = task_runs[-1]
    assign_id = db.new_assignment(
        task_run.task_id,
        task_run.db_id,
        task_run.requester_id,
        task_run.task_type,
        task_run.provider_type,
    )
    unit_id = db.new_unit(
        task_run.task_id,
        task_run.db_id,
        task_run.requester_id,
        assign_id,
        0,
        0.2,
        task_run.provider_type,
        task_run.task_type,
    )
    agent_id = db.new_agent(
        worker.db_id,
        unit_id,
        task_run.task_id,
        task_run.db_id,
        assign_id,
        task_run.task_type,
        task_run.provider_type,
    )
    agent = Agent(db, agent_id)
    agent.mark_done()
    unit = Unit(db, unit_id)
    unit.sync_status()
    return unit.db_id


EMPTY_STATE = SharedTaskState()


class AbstractTestSupervisor(ABC):
    """
    Abstract test class utilizing the Mephisto Supervisor.

    Subclasses will use the MockArchitect and the MockProvider, and they must specify a
    BlueprintClass to test.
    """

    BlueprintClass: ClassVar[Type["Blueprint"]]

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.task_id = self.db.new_task("test_mock", self.BlueprintClass.BLUEPRINT_TYPE)
        self.task_run_id = get_test_task_run(self.db)
        self.task_run = TaskRun(self.db, self.task_run_id)

        architect_config = OmegaConf.structured(
            MephistoConfig(architect=MockArchitectArgs(should_run_server=True))
        )

        self.architect = MockArchitect(
            self.db, architect_config, EMPTY_STATE, self.task_run, self.data_dir
        )
        self.architect.prepare()
        self.architect.deploy()
        self.urls = self.architect._get_socket_urls()  # FIXME
        self.url = self.urls[0]
        self.provider = MockProvider(self.db)
        self.provider.setup_resources_for_task_run(
            self.task_run, self.task_run.args, EMPTY_STATE, self.url
        )
        self.launcher = TaskLauncher(
            self.db, self.task_run, self.get_mock_assignment_data_array()
        )
        self.launcher.create_assignments()
        self.launcher.launch_units(self.url)
        self.sup = None

    def tearDown(self):
        if self.sup is not None:
            self.sup.shutdown()
        self.launcher.expire_units()
        self.architect.cleanup()
        self.architect.shutdown()
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def get_mock_assignment_data_array(self) -> List[InitializationData]:
        mock_data = MockTaskRunner.get_mock_assignment_data()
        return [mock_data, mock_data]
