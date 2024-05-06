#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from typing import List
from typing import Optional
from typing import Tuple

from omegaconf import OmegaConf

from mephisto.abstractions.architects.mock_architect import MockArchitectArgs
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprintArgs
from mephisto.abstractions.database import (
    MephistoDB,
)
from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.abstractions.providers.mock.mock_provider import MockProviderArgs
from mephisto.data_model.agent import Agent
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.requester import Requester
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.task_run import TaskRunArgs
from mephisto.data_model.unit import Unit
from mephisto.operations.hydra_config import MephistoConfig

MOCK_TASK_ARGS = TaskRunArgs(
    task_title="title",
    task_description="This is a description",
    task_reward=0.3,
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


def get_test_project(db: MephistoDB, project_name: Optional[str] = None) -> Tuple[str, str]:
    """Helper to create a project for tests"""
    project_name = project_name or "test_project"
    project_id = db.new_project(project_name)
    return project_name, project_id


def get_test_worker(db: MephistoDB, worker_name: Optional[str] = None) -> Tuple[str, str]:
    """Helper to create a worker for tests"""
    worker_name = worker_name or "test_worker"
    provider_type = "mock"
    worker_id = db.new_worker(worker_name, provider_type)
    return worker_name, worker_id


def get_test_requester(
    db: MephistoDB,
    requester_name: Optional[str] = None,
    provider_type: Optional[str] = None,
) -> Tuple[str, str]:
    """Helper to create a requester for tests"""
    requester_name = requester_name or "test_requester"
    provider_type = provider_type or "mock"
    requester_id = db.new_requester(requester_name, provider_type)
    return requester_name, requester_id


def get_mock_requester(db) -> "Requester":
    """Get or create a mock requester to use for test tasks"""
    mock_requesters = db.find_requesters(provider_type="mock")
    if len(mock_requesters) == 0:
        db.new_requester("MOCK_REQUESTER", "mock")
    mock_requesters = db.find_requesters(provider_type="mock")
    return mock_requesters[0]


def get_test_task(db: MephistoDB, task_name: Optional[str] = None) -> Tuple[str, str]:
    """Helper to create a task for tests"""
    task_name = task_name or "test_task"
    task_type = "mock"
    task_id = db.new_task(task_name, task_type)
    return task_name, task_id


def get_test_task_run(
    db: MephistoDB,
    task_id: Optional[str] = None,
    requester_id: Optional[str] = None,
) -> str:
    """Helper to create a task run for tests"""
    if not task_id:
        _, task_id = get_test_task(db)

    if not requester_id:
        _, requester_id = get_test_requester(db)

    init_params = OmegaConf.to_yaml(OmegaConf.structured(MOCK_CONFIG))
    return db.new_task_run(task_id, requester_id, json.dumps(init_params), "mock", "mock")


def get_test_assignment(db: MephistoDB, task_run: Optional[TaskRun] = None) -> str:
    """Helper to create an assignment for tests"""
    if not task_run:
        task_run_id = get_test_task_run(db)
        task_run = TaskRun.get(db, task_run_id)

    return db.new_assignment(
        task_run.task_id,
        task_run.db_id,
        task_run.requester_id,
        task_run.task_type,
        task_run.provider_type,
    )


def get_test_unit(db: MephistoDB, unit_index=0, assignment: Optional[Assignment] = None) -> str:
    # Check creation and retrieval of a unit
    if not assignment:
        assignment_id = get_test_assignment(db)
        assignment = Assignment.get(db, assignment_id)

    pay_amount = 15.0
    return db.new_unit(
        assignment.task_id,
        assignment.task_run_id,
        assignment.requester_id,
        assignment.db_id,
        unit_index,
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
    unit = Unit.get(db, unit_id)
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
    agent = Agent.get(db, agent_id)
    agent.mark_done()
    unit = Unit.get(db, unit_id)
    unit.sync_status()
    return unit.db_id


def get_test_qualification(db: MephistoDB, name: str = "test_qualification") -> str:
    return db.make_qualification(name)


def grant_test_qualification(db: MephistoDB, qualification_id: str, worker_id: str, value: int = 1):
    return db.grant_qualification(qualification_id, worker_id, value)


def find_unit_reviews(
    db,
    qualification_id: str,
    worker_id: str,
    task_id: Optional[str] = None,
) -> List[StringIDRow]:
    """
    Return unit reviews in the db by the given Qualification ID, Worker ID and Task ID
    """

    params = [nonesafe_int(qualification_id), nonesafe_int(worker_id)]
    task_query = "AND (task_id = ?3)" if task_id else ""
    if task_id:
        params.append(nonesafe_int(task_id))

    with db.table_access_condition:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute(
            f"""
            SELECT * FROM unit_review
            WHERE
                (updated_qualification_id = ?1) OR
                (revoked_qualification_id = ?1) AND
                (worker_id = ?2)
                {task_query}
            ORDER BY creation_date ASC;
            """,
            params,
        )

        results = c.fetchall()
        return results
