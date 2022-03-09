#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import Optional, Tuple
from mephisto.utils.testing import (
    get_test_assignment,
    get_test_project,
    get_test_requester,
    get_test_task,
    get_test_task_run,
    get_test_worker,
    get_test_unit,
    get_test_agent,
)
from mephisto.abstractions.providers.mock.provider_type import PROVIDER_TYPE
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.unit import Unit
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun, TaskRunArgs
from mephisto.data_model.qualification import Qualification
from mephisto.data_model.worker import Worker
from mephisto.abstractions.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)

from omegaconf import OmegaConf
import json


class BaseDatabaseTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable by any database that intends to be an implementation
    of the MephistoDB class.
    """

    is_base = True

    db: Optional[MephistoDB] = None

    @classmethod
    def setUpClass(cls):
        """
        Only run tests on subclasses of this class, as this class is just defining the
        testing interface and the tests to run on a DB that adheres to that interface
        """
        if cls is BaseDatabaseTests:
            raise unittest.SkipTest("Skip BaseDatabaseTests tests, it's a base class")
        super(BaseDatabaseTests, cls).setUpClass()

    def setUp(self) -> None:
        """
        Setup should put together any requirements for starting the
        database for a test.

        Generally this means initializing a database somewhere
        temporary and setting self.db
        """
        if self.is_base:
            raise unittest.SkipTest("Skip BaseDatabaseTests tests, it's a base class")
        raise NotImplementedError()

    def tearDown(self) -> None:
        """
        tearDown should clear up anything that was set up or
        used in any of the tests in this class.

        Generally this means cleaning up the database that was
        set up.
        """
        raise NotImplementedError()

    def get_fake_id(self, id_type: str = None) -> str:
        """
        Return a fake task id to be used to fail loading
        something that shouldn't exist yet. Takes as input
        the object type string being created
        """
        return "999"

    def test_all_types_init_empty(self) -> None:
        """Ensure all of the tables on an empty database are empty"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db
        self.assertListEqual(db.find_projects(), [])
        self.assertListEqual(db.find_tasks(), [])
        self.assertListEqual(db.find_task_runs(), [])
        self.assertListEqual(db.find_assignments(), [])
        self.assertListEqual(db.find_units(), [])
        self.assertListEqual(db.find_requesters(), [])
        self.assertListEqual(db.find_workers(), [])
        self.assertListEqual(db.find_agents(), [])

    def test_project(self) -> None:
        """Ensure projects can be created and queried as expected"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Check creation and retrieval of a project
        project_name = "test_project"
        project_id = db.new_project(project_name)
        self.assertIsNotNone(project_id)
        self.assertTrue(isinstance(project_id, str))
        project_row = db.get_project(project_id)
        self.assertEqual(project_row["project_name"], project_name)
        project = Project.get(db, project_id)
        self.assertEqual(project.project_name, project_name)

        # Check finding for projects
        projects = db.find_projects()
        self.assertEqual(len(projects), 1)
        self.assertTrue(isinstance(projects[0], Project))
        self.assertEqual(projects[0].db_id, project_id)
        self.assertEqual(projects[0].project_name, project_name)

        # Check finding for specific projects
        projects = db.find_projects(project_name=project_name)
        self.assertEqual(len(projects), 1)
        self.assertTrue(isinstance(projects[0], Project))
        self.assertEqual(projects[0].db_id, project_id)
        self.assertEqual(projects[0].project_name, project_name)

        projects = db.find_projects(project_name="fake_name")
        self.assertEqual(len(projects), 0)

    def test_project_fails(self) -> None:
        """Ensure projects fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            project = Project.get(db, self.get_fake_id("Project"))

        project_name = "test_project"
        project_id = db.new_project(project_name)

        # Can't create same project again
        with self.assertRaises(EntryAlreadyExistsException):
            project_id = db.new_project(project_name)

        # Can't use reserved name
        with self.assertRaises(MephistoDBException):
            project_id = db.new_project(NO_PROJECT_NAME)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            project_id = db.new_project("")

        # Ensure no projects were created
        projects = db.find_projects()
        self.assertEqual(len(projects), 1)

    def test_task(self) -> None:
        """Ensure tasks can be created and queried as expected"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        project_name, project_id = get_test_project(db)

        # Check creation and retrieval of a task
        task_name_1 = "test_task"
        task_type = "mock"
        task_id_1 = db.new_task(task_name_1, task_type, project_id=project_id)
        self.assertIsNotNone(task_id_1)
        self.assertTrue(isinstance(task_id_1, str))
        task_row = db.get_task(task_id_1)
        self.assertEqual(task_row["task_name"], task_name_1)
        self.assertEqual(task_row["task_type"], task_type)
        self.assertEqual(task_row["project_id"], project_id)
        self.assertIsNone(task_row["parent_task_id"])
        task = Task.get(db, task_id_1)
        self.assertEqual(task.task_name, task_name_1)

        # Check creation of a task with a parent task, but no project
        task_name_2 = "test_task_2"
        task_id_2 = db.new_task(task_name_2, task_type)
        self.assertIsNotNone(task_id_2)
        self.assertTrue(isinstance(task_id_2, str))
        task_row = db.get_task(task_id_2)
        self.assertEqual(task_row["task_name"], task_name_2)
        self.assertEqual(task_row["task_type"], task_type)
        self.assertIsNone(task_row["parent_task_id"])
        self.assertIsNone(task_row["project_id"])
        task = Task.get(db, task_id_2)
        self.assertEqual(task.task_name, task_name_2)

        # Check finding for tasks
        tasks = db.find_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertTrue(isinstance(tasks[0], Task))

        # Check finding for specific tasks
        tasks = db.find_tasks(task_name=task_name_1)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(isinstance(tasks[0], Task))
        self.assertEqual(tasks[0].db_id, task_id_1)
        self.assertEqual(tasks[0].task_name, task_name_1)

        tasks = db.find_tasks(project_id=project_id)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(isinstance(tasks[0], Task))
        self.assertEqual(tasks[0].db_id, task_id_1)
        self.assertEqual(tasks[0].task_name, task_name_1)

        tasks = db.find_tasks(task_name="fake_name")
        self.assertEqual(len(tasks), 0)

    def test_task_fails(self) -> None:
        """Ensure task creation fails under specific cases"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            task = Task.get(db, self.get_fake_id("Task"))

        task_name = "test_task"
        task_name_2 = "test_task_2"
        task_type = "mock"
        task_id = db.new_task(task_name, task_type)

        # Can't create same task again
        with self.assertRaises(EntryAlreadyExistsException):
            task_id = db.new_task(task_name, task_type)

        # Can't create task with invalid project
        with self.assertRaises(EntryDoesNotExistException):
            fake_id = self.get_fake_id("Project")
            task_id = db.new_task(task_name_2, task_type, project_id=fake_id)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            task_id = db.new_task("", task_type)

        # Ensure no tasks were created
        tasks = db.find_tasks()
        self.assertEqual(len(tasks), 1)

    def test_update_task(self) -> None:
        """Ensure tasks can be updated (when not run yet)"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        project_name, project_id = get_test_project(db)

        # Check creation and retrieval of a task
        task_name_1 = "test_task"
        task_name_2 = "test_task_2"
        task_type = "mock"
        task_id_1 = db.new_task(task_name_1, task_type)

        tasks = db.find_tasks(project_id=project_id)
        self.assertEqual(len(tasks), 0)

        tasks = db.find_tasks(task_name=task_name_2)
        self.assertEqual(len(tasks), 0)

        db.update_task(task_id_1, task_name=task_name_2, project_id=project_id)

        # Ensure the task is now findable under the new details
        tasks = db.find_tasks(project_id=project_id)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].db_id, task_id_1)
        self.assertEqual(tasks[0].task_name, task_name_2)

        tasks = db.find_tasks(task_name=task_name_2)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].db_id, task_id_1)
        self.assertEqual(tasks[0].task_name, task_name_2)

    def test_update_task_failures(self) -> None:
        """Ensure failure conditions trigger for updating tasks"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        task_name = "test_task"
        task_type = "mock"
        task_id = db.new_task(task_name, task_type)

        task_name_2 = "test_task_2"
        task_id_2 = db.new_task(task_name_2, task_type)

        task_name_3 = "test_task_3"

        # Can't update a task to existing name
        with self.assertRaises(EntryAlreadyExistsException):
            db.update_task(task_id_2, task_name=task_name)

        # Can't update to an invalid name
        with self.assertRaises(MephistoDBException):
            db.update_task(task_id_2, task_name="")

        # Can't update to a nonexistent project id
        with self.assertRaises(EntryDoesNotExistException):
            fake_id = self.get_fake_id("Project")
            db.update_task(task_id_2, project_id=fake_id)

        # can update a task though
        db.update_task(task_id_2, task_name=task_name_3)

        # But not after we've created a task run
        requester_name, requester_id = get_test_requester(db)
        init_params = json.dumps(OmegaConf.to_yaml(TaskRunArgs.get_mock_params()))
        task_run_id = db.new_task_run(
            task_id_2, requester_id, init_params, "mock", "mock"
        )
        with self.assertRaises(MephistoDBException):
            db.update_task(task_id_2, task_name=task_name_2)

    def test_requester(self) -> None:
        """Test creation and querying of requesters"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Check creation and retrieval of a requester
        requester_name = "test_requester"
        provider_type = PROVIDER_TYPE
        requester_id = db.new_requester(requester_name, provider_type)
        self.assertIsNotNone(requester_id)
        self.assertTrue(isinstance(requester_id, str))
        requester_row = db.get_requester(requester_id)
        self.assertEqual(requester_row["requester_name"], requester_name)

        requester = Requester.get(db, requester_id)
        self.assertEqual(requester.requester_name, requester_name)

        # Check finding for requesters
        requesters = db.find_requesters()
        self.assertEqual(len(requesters), 1)
        self.assertTrue(isinstance(requesters[0], Requester))
        self.assertEqual(requesters[0].db_id, requester_id)
        self.assertEqual(requesters[0].requester_name, requester_name)

        # Check finding for specific requesters
        requesters = db.find_requesters(requester_name=requester_name)
        self.assertEqual(len(requesters), 1)
        self.assertTrue(isinstance(requesters[0], Requester))
        self.assertEqual(requesters[0].db_id, requester_id)
        self.assertEqual(requesters[0].requester_name, requester_name)

        requesters = db.find_requesters(requester_name="fake_name")
        self.assertEqual(len(requesters), 0)

    def test_requester_fails(self) -> None:
        """Ensure requesters fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            requester = Requester.get(db, self.get_fake_id("Requester"))

        requester_name = "test_requester"
        provider_type = PROVIDER_TYPE
        requester_id = db.new_requester(requester_name, provider_type)

        # Can't create same requester again
        with self.assertRaises(EntryAlreadyExistsException):
            requester_id = db.new_requester(requester_name, provider_type)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            requester_id = db.new_requester("", provider_type)

        # Ensure no requesters were created
        requesters = db.find_requesters()
        self.assertEqual(len(requesters), 1)

    def test_worker(self) -> None:
        """Test creation and querying of workers"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Check creation and retrieval of a worker
        worker_name = "test_worker"
        provider_type = PROVIDER_TYPE
        worker_id = db.new_worker(worker_name, provider_type)
        self.assertIsNotNone(worker_id)
        self.assertTrue(isinstance(worker_id, str))
        worker_row = db.get_worker(worker_id)
        self.assertEqual(worker_row["worker_name"], worker_name)

        worker = Worker.get(db, worker_id)
        self.assertEqual(worker.worker_name, worker_name)

        # Check finding for workers
        workers = db.find_workers()
        self.assertEqual(len(workers), 1)
        self.assertTrue(isinstance(workers[0], Worker))
        self.assertEqual(workers[0].db_id, worker_id)
        self.assertEqual(workers[0].worker_name, worker_name)

        # Check finding for specific workers
        workers = db.find_workers(worker_name=worker_name)
        self.assertEqual(len(workers), 1)
        self.assertTrue(isinstance(workers[0], Worker))
        self.assertEqual(workers[0].db_id, worker_id)
        self.assertEqual(workers[0].worker_name, worker_name)

        workers = db.find_workers(worker_name="fake_name")
        self.assertEqual(len(workers), 0)

    def test_worker_fails(self) -> None:
        """Ensure workers fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            worker = Worker.get(db, self.get_fake_id("Worker"))

        worker_name = "test_worker"
        provider_type = PROVIDER_TYPE
        worker_id = db.new_worker(worker_name, provider_type)

        # Can't create same worker again
        with self.assertRaises(EntryAlreadyExistsException):
            worker_id = db.new_worker(worker_name, provider_type)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            worker_id = db.new_worker("", provider_type)

        # Ensure no workers were created
        workers = db.find_workers()
        self.assertEqual(len(workers), 1)

    def test_task_run(self) -> None:
        """Test creation and querying of task_runs"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        task_name, task_id = get_test_task(db)
        requester_name, requester_id = get_test_requester(db)

        # Check creation and retrieval of a task_run
        init_params = json.dumps(OmegaConf.to_yaml(TaskRunArgs.get_mock_params()))
        task_run_id = db.new_task_run(
            task_id, requester_id, init_params, "mock", "mock"
        )
        self.assertIsNotNone(task_run_id)
        self.assertTrue(isinstance(task_run_id, str))
        task_run_row = db.get_task_run(task_run_id)
        self.assertEqual(task_run_row["init_params"], init_params)
        task_run = TaskRun.get(db, task_run_id)
        self.assertEqual(task_run.task_id, task_id)

        # Check finding for task_runs
        task_runs = db.find_task_runs()
        self.assertEqual(len(task_runs), 1)
        self.assertTrue(isinstance(task_runs[0], TaskRun))
        self.assertEqual(task_runs[0].db_id, task_run_id)
        self.assertEqual(task_runs[0].task_id, task_id)
        self.assertEqual(task_runs[0].requester_id, requester_id)

        # Check finding for specific task_runs
        task_runs = db.find_task_runs(task_id=task_id)
        self.assertEqual(len(task_runs), 1)
        self.assertTrue(isinstance(task_runs[0], TaskRun))
        self.assertEqual(task_runs[0].db_id, task_run_id)
        self.assertEqual(task_runs[0].task_id, task_id)
        self.assertEqual(task_runs[0].requester_id, requester_id)

        task_runs = db.find_task_runs(requester_id=requester_id)
        self.assertEqual(len(task_runs), 1)
        self.assertTrue(isinstance(task_runs[0], TaskRun))
        self.assertEqual(task_runs[0].db_id, task_run_id)
        self.assertEqual(task_runs[0].task_id, task_id)
        self.assertEqual(task_runs[0].requester_id, requester_id)

        task_runs = db.find_task_runs(task_id=self.get_fake_id("TaskRun"))
        self.assertEqual(len(task_runs), 0)

        task_runs = db.find_task_runs(is_completed=True)
        self.assertEqual(len(task_runs), 0)

        # Test updating the completion status, requery
        db.update_task_run(task_run_id, True)
        task_runs = db.find_task_runs(is_completed=True)
        self.assertEqual(len(task_runs), 1)
        self.assertTrue(isinstance(task_runs[0], TaskRun))
        self.assertEqual(task_runs[0].db_id, task_run_id)

    def test_task_run_fails(self) -> None:
        """Ensure task_runs fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        task_name, task_id = get_test_task(db)
        requester_name, requester_id = get_test_requester(db)
        init_params = json.dumps(OmegaConf.to_yaml(TaskRunArgs.get_mock_params()))

        # Can't create task run with invalid ids
        with self.assertRaises(EntryDoesNotExistException):
            task_run_id = db.new_task_run(
                self.get_fake_id("Task"), requester_id, init_params, "mock", "mock"
            )
        with self.assertRaises(EntryDoesNotExistException):
            task_run_id = db.new_task_run(
                task_id, self.get_fake_id("Requester"), init_params, "mock", "mock"
            )

        # Ensure no task_runs were created
        task_runs = db.find_task_runs()
        self.assertEqual(len(task_runs), 0)

    def test_assignment(self) -> None:
        """Test creation and querying of assignments"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        task_run_id = get_test_task_run(db)
        task_run = TaskRun.get(db, task_run_id)

        # Check creation and retrieval of an assignment
        assignment_id = db.new_assignment(
            task_run.task_id,
            task_run_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
            task_run.sandbox,
        )
        self.assertIsNotNone(assignment_id)
        self.assertTrue(isinstance(assignment_id, str))
        assignment_row = db.get_assignment(assignment_id)
        self.assertEqual(assignment_row["task_run_id"], task_run_id)
        assignment = Assignment.get(db, assignment_id)
        self.assertEqual(assignment.task_run_id, task_run_id)

        # Check finding for assignments
        assignments = db.find_assignments()
        self.assertEqual(len(assignments), 1)
        self.assertTrue(isinstance(assignments[0], Assignment))
        self.assertEqual(assignments[0].db_id, assignment_id)
        self.assertEqual(assignments[0].task_run_id, task_run_id)

        # Check finding for specific assignments
        assignments = db.find_assignments(task_run_id=task_run_id)
        self.assertEqual(len(assignments), 1)
        self.assertTrue(isinstance(assignments[0], Assignment))
        self.assertEqual(assignments[0].db_id, assignment_id)
        self.assertEqual(assignments[0].task_run_id, task_run_id)

        assignments = db.find_assignments(task_run_id=self.get_fake_id("Assignment"))
        self.assertEqual(len(assignments), 0)

    def test_assignment_fails(self) -> None:
        """Ensure assignments fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        task_run_id = get_test_task_run(db)
        task_run = TaskRun.get(db, task_run_id)
        # Can't create task run with invalid ids
        with self.assertRaises(EntryDoesNotExistException):
            assignment_id = db.new_assignment(
                task_run.task_id,
                self.get_fake_id("TaskRun"),
                task_run.requester_id,
                task_run.task_type,
                task_run.provider_type,
                task_run.sandbox,
            )

        # Ensure no assignments were created
        assignments = db.find_assignments()
        self.assertEqual(len(assignments), 0)

    def test_unit(self) -> None:
        """Test creation and querying of units"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Check creation and retrieval of a unit
        assignment_id = get_test_assignment(db)
        assignment = Assignment.get(db, assignment_id)
        unit_index = 0
        pay_amount = 15.0
        provider_type = PROVIDER_TYPE

        unit_id = db.new_unit(
            assignment.task_id,
            assignment.task_run_id,
            assignment.requester_id,
            assignment.db_id,
            unit_index,
            pay_amount,
            provider_type,
            assignment.sandbox,
        )
        self.assertIsNotNone(unit_id)
        self.assertTrue(isinstance(unit_id, str))
        unit_row = db.get_unit(unit_id)
        self.assertEqual(unit_row["assignment_id"], assignment_id)
        self.assertEqual(unit_row["pay_amount"], pay_amount)
        self.assertEqual(unit_row["status"], AssignmentState.CREATED)

        unit = Unit.get(db, unit_id)
        self.assertEqual(unit.assignment_id, assignment_id)

        # Check finding for units
        units = db.find_units()
        self.assertEqual(len(units), 1)
        self.assertTrue(isinstance(units[0], Unit))
        self.assertEqual(units[0].db_id, unit_id)
        self.assertEqual(units[0].assignment_id, assignment_id)
        self.assertEqual(units[0].pay_amount, pay_amount)

        # Check finding for specific units
        units = db.find_units(assignment_id=assignment_id)
        self.assertEqual(len(units), 1)
        self.assertTrue(isinstance(units[0], Unit))
        self.assertEqual(units[0].db_id, unit_id)
        self.assertEqual(units[0].assignment_id, assignment_id)
        self.assertEqual(units[0].pay_amount, pay_amount)

        units = db.find_units(assignment_id=self.get_fake_id("Assignment"))
        self.assertEqual(len(units), 0)

    def test_unit_fails(self) -> None:
        """Ensure units fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            unit = Unit.get(db, self.get_fake_id("Unit"))

        assignment_id = get_test_assignment(db)
        assignment = Assignment.get(db, assignment_id)
        unit_index = 0
        pay_amount = 15.0
        provider_type = PROVIDER_TYPE

        # Can't use invalid assignment_id name
        with self.assertRaises(EntryDoesNotExistException):
            unit_id = db.new_unit(
                assignment.task_id,
                assignment.task_run_id,
                assignment.requester_id,
                self.get_fake_id("Assignment"),
                unit_index,
                pay_amount,
                provider_type,
                assignment.sandbox,
            )

        unit_id = db.new_unit(
            assignment.task_id,
            assignment.task_run_id,
            assignment.requester_id,
            assignment.db_id,
            unit_index,
            pay_amount,
            provider_type,
            assignment.sandbox,
        )

        # Can't create same unit again
        with self.assertRaises(EntryAlreadyExistsException):
            unit_id = db.new_unit(
                assignment.task_id,
                assignment.task_run_id,
                assignment.requester_id,
                assignment.db_id,
                unit_index,
                pay_amount,
                provider_type,
                assignment.sandbox,
            )

        # Ensure no units were created
        units = db.find_units()
        self.assertEqual(len(units), 1)

    def test_unit_updates(self) -> None:
        """Test updating a unit's status"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        unit_id = get_test_unit(db)

        # Check finding for specific units
        units = db.find_units(status=AssignmentState.COMPLETED)
        self.assertEqual(len(units), 0)

        db.update_unit(unit_id, status=AssignmentState.COMPLETED)

        # Check finding for specific units
        units = db.find_units(status=AssignmentState.COMPLETED)
        self.assertEqual(len(units), 1)

        # Can't update with a status that doesn't exist
        with self.assertRaises(MephistoDBException):
            db.update_unit(unit_id, status="FAKE_STATUS")

    def test_agent(self) -> None:
        """Test creation and querying of agents"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Check creation and retrieval of a agent
        worker_name, worker_id = get_test_worker(db)
        unit_id = get_test_unit(db)
        unit = Unit.get(db, unit_id)

        agent_id = db.new_agent(
            worker_id,
            unit_id,
            unit.task_id,
            unit.task_run_id,
            unit.assignment_id,
            unit.task_type,
            unit.provider_type,
        )
        self.assertIsNotNone(agent_id)
        self.assertTrue(isinstance(agent_id, str))
        agent_row = db.get_agent(agent_id)
        self.assertEqual(agent_row["worker_id"], worker_id)
        self.assertEqual(agent_row["unit_id"], unit_id)
        self.assertEqual(agent_row["status"], AgentState.STATUS_NONE)

        # ensure the unit is assigned now
        units = db.find_units(status=AssignmentState.ASSIGNED)
        self.assertEqual(len(units), 1)

        agent = Agent.get(db, agent_id)
        self.assertEqual(agent.worker_id, worker_id)

        # Check finding for agents
        agents = db.find_agents()
        self.assertEqual(len(agents), 1)
        self.assertTrue(isinstance(agents[0], Agent))
        self.assertEqual(agents[0].db_id, agent_id)
        self.assertEqual(agents[0].worker_id, worker_id)

        # Check finding for specific agents
        agents = db.find_agents(worker_id=worker_id)
        self.assertEqual(len(agents), 1)
        self.assertTrue(isinstance(agents[0], Agent))
        self.assertEqual(agents[0].db_id, agent_id)
        self.assertEqual(agents[0].worker_id, worker_id)

        agents = db.find_agents(worker_id=self.get_fake_id("Worker"))
        self.assertEqual(len(agents), 0)

    def test_agent_fails(self) -> None:
        """Ensure agents fail to be created or loaded under failure conditions"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            agent = Agent.get(db, self.get_fake_id("Agent"))

        unit_id = get_test_unit(db)
        worker_name, worker_id = get_test_worker(db)
        unit = Unit.get(db, unit_id)

        # Can't use invalid worker id
        with self.assertRaises(EntryDoesNotExistException):
            agent_id = db.new_agent(
                self.get_fake_id("Worker"),
                unit_id,
                unit.task_id,
                unit.task_run_id,
                unit.assignment_id,
                unit.task_type,
                unit.provider_type,
            )

        # Can't use invalid unit id
        with self.assertRaises(EntryDoesNotExistException):
            agent_id = db.new_agent(
                worker_id,
                self.get_fake_id("Unit"),
                unit.task_id,
                unit.task_run_id,
                unit.assignment_id,
                unit.task_type,
                unit.provider_type,
            )

        # Ensure no agents were created
        agents = db.find_agents()
        self.assertEqual(len(agents), 0)

    def test_agent_updates(self) -> None:
        """Test updating an agent's status"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        agent_id = get_test_agent(db)

        # Check finding for specific agents
        agents = db.find_agents(status=AgentState.STATUS_NONE)
        self.assertEqual(len(agents), 1)

        agents = db.find_agents(status=AgentState.STATUS_ONBOARDING)
        self.assertEqual(len(agents), 0)

        db.update_agent(agent_id, status=AgentState.STATUS_ONBOARDING)

        # Check finding for specific agents
        agents = db.find_agents(status=AgentState.STATUS_ONBOARDING)
        self.assertEqual(len(agents), 1)

        agents = db.find_agents(status=AgentState.STATUS_NONE)
        self.assertEqual(len(agents), 0)

        # Can't update with a status that doesn't exist
        with self.assertRaises(MephistoDBException):
            db.update_agent(agent_id, status="FAKE_STATUS")

    def test_qualifications(self) -> None:
        """Test creating, assigning, revoking, and deleting qualifications"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        qualification_name = "TEST_QUALIFICATION_1"

        # Create qualification
        qual_id = db.make_qualification(qualification_name)

        # ensure qualification has been made
        qualifications = db.find_qualifications(qualification_name=qualification_name)

        self.assertEqual(len(qualifications), 1, "Single qualification not created")
        self.assertIsInstance(qualifications[0], Qualification)

        # Can't create same qualification again
        with self.assertRaises(EntryAlreadyExistsException):
            qual_id = db.make_qualification(qualification_name)

        qualifications = db.find_qualifications(qualification_name)
        self.assertEqual(len(qualifications), 1, "More than one qualification created")

        # Grant the qualification to a worker
        worker_name, worker_id = get_test_worker(db)

        db.grant_qualification(qual_id, worker_id)

        # Ensure it was granted
        granted_quals = db.check_granted_qualifications()
        self.assertEqual(len(granted_quals), 1, "Single qualification not granted")
        granted_qual = granted_quals[0]
        self.assertEqual(granted_qual.worker_id, worker_id)
        self.assertEqual(granted_qual.qualification_id, qual_id)
        self.assertEqual(granted_qual.value, 1)

        # Update the qualification
        db.grant_qualification(qual_id, worker_id, value=3)
        # Ensure it was updated
        granted_quals = db.check_granted_qualifications()
        self.assertEqual(len(granted_quals), 1, "Single qualification not granted")
        granted_qual = granted_quals[0]
        self.assertEqual(granted_qual.worker_id, worker_id)
        self.assertEqual(granted_qual.qualification_id, qual_id)
        self.assertEqual(granted_qual.value, 3)

        # Delete the qualification
        db.revoke_qualification(qual_id, worker_id)
        granted_quals = db.check_granted_qualifications()
        self.assertEqual(len(granted_quals), 0, "Single qualification not removed")

        # Re-grant the qualification
        db.grant_qualification(qual_id, worker_id)

        # Delete the qualification entirely
        db.delete_qualification(qualification_name)

        # Ensure deleted and cascaded
        qualifications = db.find_qualifications(qualification_name)
        self.assertEqual(len(qualifications), 0, "Qualification not remove")
        granted_quals = db.check_granted_qualifications()
        self.assertEqual(
            len(granted_quals), 0, "Cascade granted qualification not removed"
        )

        # cant retrieve the qualification directly anymore
        with self.assertRaises(EntryDoesNotExistException):
            qualification_row = db.get_granted_qualification(qual_id, worker_id)

    def test_onboarding_agents(self) -> None:
        """Ensure that the db can create and manipulate onboarding agents"""
        assert self.db is not None, "No db initialized"
        db: MephistoDB = self.db

        task_run_id = get_test_task_run(db)
        task_run = TaskRun.get(db, task_run_id)
        task = task_run.get_task()
        worker_name, worker_id = get_test_worker(db)

        onboarding_agent_id = db.new_onboarding_agent(
            worker_id, task.db_id, task_run_id, "mock"
        )
        self.assertIsNotNone(onboarding_agent_id)

        onboarding_agent = OnboardingAgent.get(db, onboarding_agent_id)
        self.assertIsInstance(onboarding_agent, OnboardingAgent)

        found_agents = db.find_onboarding_agents(worker_id=worker_id)
        self.assertEqual(len(found_agents), 1)
        self.assertIsInstance(found_agents[0], OnboardingAgent)
        found_agent = found_agents[0]
        self.assertEqual(found_agent.db_id, onboarding_agent_id)
        self.assertEqual(found_agent.get_status(), AgentState.STATUS_NONE)
