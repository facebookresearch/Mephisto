from typing import Optional, Tuple

from mephisto.data_model.database import MephistoDB, MephistoDBException, EntryAlreadyExistsException, EntryDoesNotExistException


def get_test_project(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a project for tests"""
    project_name = 'test_project'
    project_id = db.new_project(project_name)
    return project_name, project_id


def get_test_worker(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a worker for tests"""
    worker_name = 'test_worker'
    provider_type = 'mock'
    worker_id = db.new_worker(worker_name, provider_type)
    return worker_name, worker_id


def get_test_requester(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a requester for tests"""
    requester_name = 'test_requester'
    provider_type = 'mock'
    requester_id = db.new_requester(requester_name, provider_type)
    return requester_name, requester_id


def get_test_task(db: MephistoDB) -> Tuple[str, str]:
    """Helper to create a task for tests"""
    task_name = 'test_task'
    task_type = 'mock'
    task_id = db.new_task(task_name, task_type)
    return task_name, task_id


def get_test_task_run(db: MephistoDB) -> str:
    """Helper to create a task run for tests"""
    task_name, task_id = get_test_task(db)
    requester_name, requester_id = get_test_requester(db)
    init_params = "--test --params"
    return db.new_task_run(task_id, requester_id, init_params)


def get_test_assignment(db: MephistoDB) -> str:
    """Helper to create an assignment for tests"""
    task_run_id = get_test_task_run(db)
    return db.new_assignment(task_run_id)


def get_test_unit(db:MephistoDB, unit_index=0) -> str:
    # Check creation and retrieval of a unit
    assignment_id = get_test_assignment(db)
    pay_amount = 15.0
    provider_type = 'mock'

    return db.new_unit(assignment_id, unit_index, pay_amount, provider_type)


def get_test_agent(db: MephistoDB, unit_id=None) -> str:
    # Check creation and retrieval of a agent
    worker_name, worker_id = get_test_worker(db)
    if unit_id is None:
        unit_id = get_test_unit(db)
    provider_type = 'mock'
    task_type = 'mock'

    return db.new_agent(worker_id, unit_id, task_type, provider_type)
