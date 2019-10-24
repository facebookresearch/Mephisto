#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import Optional, Tuple
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.data_model.agent import Agent
from mephisto.data_model.agent_state import AgentState
from mephisto.data_model.assignment import Assignment, Unit
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task, TaskRun
from mephisto.data_model.worker import Worker
from mephisto.data_model.database import MephistoDB, MephistoDBException, EntryAlreadyExistsException, EntryDoesNotExistException


class BaseDatabaseTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable by any database that intends to be an implementation
    of the MephistoDB class.
    """

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
        return '999'

    def get_test_project(self) -> Tuple[str, str]:
        """Helper to create a project for tests"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db
        project_name = 'test_project'
        project_id = db.new_project(project_name)
        return project_name, project_id

    def get_test_worker(self) -> Tuple[str, str]:
        """Helper to create a worker for tests"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db
        worker_name = 'test_worker'
        provider_type = 'mock'
        worker_id = db.new_worker(worker_name, provider_type)
        return worker_name, worker_id

    def get_test_requester(self) -> Tuple[str, str]:
        """Helper to create a requester for tests"""
        db: MephistoDB = self.db
        requester_name = 'test_requester'
        provider_type = 'mock'
        requester_id = db.new_requester(requester_name, provider_type)
        return requester_name, requester_id

    def get_test_task(self) -> Tuple[str, str]:
        """Helper to create a task for tests"""
        db: MephistoDB = self.db
        task_name = 'test_task'
        task_type = 'mock'
        task_id = db.new_task(task_name, task_type)
        return task_name, task_id

    def test_all_types_init_empty(self) -> None:
        """Ensure all of the tables on an empty database are empty"""
        assert self.db is not None, 'No db initialized'
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
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Check creation and retrieval of a project
        project_name = 'test_project'
        project_id = db.new_project(project_name)
        self.assertIsNotNone(project_id)
        self.assertTrue(isinstance(project_id, str))
        project_row = db.get_project(project_id)
        self.assertEqual(project_row['project_name'], project_name)
        project = Project(db, project_id)
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

        projects = db.find_projects(project_name='fake_name')
        self.assertEqual(len(projects), 0)

    def test_project_fails(self) -> None:
        """Ensure projects fail to be created or loaded under failure conditions"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            project = Project(db, self.get_fake_id('Project'))

        project_name = 'test_project'
        project_id = db.new_project(project_name)

        # Can't create same project again
        with self.assertRaises(EntryAlreadyExistsException):
            project_id = db.new_project(project_name)

        # Can't use reserved name
        with self.assertRaises(MephistoDBException):
            project_id = db.new_project(NO_PROJECT_NAME)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            project_id = db.new_project('')

        # Ensure no projects were created
        projects = db.find_projects()
        self.assertEqual(len(projects), 1)

    def test_task(self) -> None:
        """Ensure tasks can be created and queried as expected"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        project_name, project_id = self.get_test_project()

        # Check creation and retrieval of a task
        task_name_1 = 'test_task'
        task_type = 'test'
        task_id_1 = db.new_task(task_name_1, task_type, project_id=project_id)
        self.assertIsNotNone(task_id_1)
        self.assertTrue(isinstance(task_id_1, str))
        task_row = db.get_task(task_id_1)
        self.assertEqual(task_row['task_name'], task_name_1)
        self.assertEqual(task_row['task_type'], task_type)
        self.assertEqual(task_row['project_id'], project_id)
        self.assertIsNone(task_row['parent_task_id'])
        task = Task(db, task_id_1)
        self.assertEqual(task.task_name, task_name_1)

        # Check creation of a task with a parent task, but no project
        task_name_2 = 'test_task_2'
        task_id_2 = db.new_task(task_name_2, task_type, parent_task_id=task_id_1)
        self.assertIsNotNone(task_id_2)
        self.assertTrue(isinstance(task_id_2, str))
        task_row = db.get_task(task_id_2)
        self.assertEqual(task_row['task_name'], task_name_2)
        self.assertEqual(task_row['task_type'], task_type)
        self.assertEqual(task_row['parent_task_id'], task_id_1)
        self.assertIsNone(task_row['project_id'])
        task = Task(db, task_id_2)
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

        tasks = db.find_tasks(parent_task_id=task_id_1)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(isinstance(tasks[0], Task))
        self.assertEqual(tasks[0].db_id, task_id_2)
        self.assertEqual(tasks[0].task_name, task_name_2)

        tasks = db.find_tasks(task_name='fake_name')
        self.assertEqual(len(tasks), 0)

    def test_task_fails(self) -> None:
        """Ensure task creation fails under specific cases"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            task = Task(db, self.get_fake_id('Task'))

        task_name = 'test_task'
        task_type = 'test'
        task_id = db.new_task(task_name, task_type)

        # Can't create same task again
        with self.assertRaises(EntryAlreadyExistsException):
            task_id = db.new_task(task_name, task_type)

        # Can't create task with invalid project
        with self.assertRaises(EntryDoesNotExistException):
            fake_id = self.get_fake_id('Project')
            task_id = db.new_task(task_name, task_type, project_id=fake_id)

        # Can't create task with invalid parent task
        with self.assertRaises(EntryAlreadyExistsException):
            fake_id = self.get_fake_id('Task')
            task_id = db.new_task(task_name, task_type, parent_task_id=fake_id)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            task_id = db.new_task('', task_type)

        # Ensure no tasks were created
        tasks = db.find_tasks()
        self.assertEqual(len(tasks), 1)

    def test_update_task(self) -> None:
        """Ensure tasks can be updated (when not run yet)"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        project_name, project_id = self.get_test_project()

        # Check creation and retrieval of a task
        task_name_1 = 'test_task'
        task_name_2 = 'test_task_2'
        task_type = 'test'
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
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        task_name = 'test_task'
        task_type = 'test'
        task_id = db.new_task(task_name, task_type)

        task_name_2 = 'test_task_2'
        task_id_2 = db.new_task(task_name_2, task_type)

        task_name_3 = 'test_task_3'

        # Can't update a task to existing name
        with self.assertRaises(EntryAlreadyExistsException):
            task_id = db.update_task(task_id_2, task_name=task_name)

        # Can't update to an invalid name
        with self.assertRaises(MephistoDBException):
            task_id = db.update_task(task_id_2, task_name='')

        # Can't update to a nonexistent project id
        with self.assertRaises(EntryDoesNotExistException):
            fake_id = self.get_fake_id('Project')
            task_id = db.update_task(task_id_2, project_id=fake_id)

        # can update a task though
        db.update_task(task_id_2, task_name=task_name_3)

        # But not after we've created a task run
        requester_name, requester_id = self.get_test_requester()
        init_params = "--test --params"
        task_run_id = db.new_task_run(task_id_2, requester_id, init_params)
        with self.assertRaises(MephistoDBException):
            task_id = db.update_task(task_id_2, task_name=task_name_2)

    def test_requester(self) -> None:
        """Test creation and querying of requesters"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Check creation and retrieval of a requester
        requester_name = 'test_requester'
        provider_type = 'mock'
        requester_id = db.new_requester(requester_name, provider_type)
        self.assertIsNotNone(requester_id)
        self.assertTrue(isinstance(requester_id, str))
        requester_row = db.get_requester(requester_id)
        self.assertEqual(requester_row['requester_name'], requester_name)

        # TODO Uncomment once Requester mock object exists
        # requester = Requester(db, requester_id)
        # self.assertEqual(requester.requester_name, requester_name)

        # # Check finding for requesters
        # requesters = db.find_requesters()
        # self.assertEqual(len(requesters), 1)
        # self.assertTrue(isinstance(requesters[0], Requester))
        # self.assertEqual(requesters[0].db_id, requester_id)
        # self.assertEqual(requesters[0].requester_name, requester_name)

        # # Check finding for specific requesters
        # requesters = db.find_requesters(requester_name=requester_name)
        # self.assertEqual(len(requesters), 1)
        # self.assertTrue(isinstance(requesters[0], Requester))
        # self.assertEqual(requesters[0].db_id, requester_id)
        # self.assertEqual(requesters[0].requester_name, requester_name)

        # requesters = db.find_requesters(requester_name='fake_name')
        # self.assertEqual(len(requesters), 0)

    def test_requester_fails(self) -> None:
        """Ensure requesters fail to be created or loaded under failure conditions"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            requester = Requester(db, self.get_fake_id('Requester'))

        requester_name = 'test_requester'
        provider_type = 'mock'
        requester_id = db.new_requester(requester_name, provider_type)

        # Can't create same requester again
        with self.assertRaises(EntryAlreadyExistsException):
            requester_id = db.new_requester(requester_name, provider_type)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            requester_id = db.new_requester('', provider_type)

        # TODO uncomment once Requester mock is created
        # # Ensure no requesters were created
        # requesters = db.find_requesters()
        # self.assertEqual(len(requesters), 1)

    def test_worker(self) -> None:
        """Test creation and querying of workers"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Check creation and retrieval of a worker
        worker_name = 'test_worker'
        provider_type = 'mock'
        worker_id = db.new_worker(worker_name, provider_type)
        self.assertIsNotNone(worker_id)
        self.assertTrue(isinstance(worker_id, str))
        worker_row = db.get_worker(worker_id)
        self.assertEqual(worker_row['worker_name'], worker_name)

        # TODO Uncomment once Worker mock object exists
        # worker = Worker(db, worker_id)
        # self.assertEqual(worker.worker_name, worker_name)

        # # Check finding for workers
        # workers = db.find_workers()
        # self.assertEqual(len(workers), 1)
        # self.assertTrue(isinstance(workers[0], Worker))
        # self.assertEqual(workers[0].db_id, worker_id)
        # self.assertEqual(workers[0].worker_name, worker_name)

        # # Check finding for specific workers
        # workers = db.find_workers(worker_name=worker_name)
        # self.assertEqual(len(workers), 1)
        # self.assertTrue(isinstance(workers[0], Worker))
        # self.assertEqual(workers[0].db_id, worker_id)
        # self.assertEqual(workers[0].worker_name, worker_name)

        # workers = db.find_workers(worker_name='fake_name')
        # self.assertEqual(len(workers), 0)

    def test_worker_fails(self) -> None:
        """Ensure workers fail to be created or loaded under failure conditions"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        # Cant get non-existent entry
        with self.assertRaises(EntryDoesNotExistException):
            worker = Worker(db, self.get_fake_id('Worker'))

        worker_name = 'test_worker'
        provider_type = 'mock'
        worker_id = db.new_worker(worker_name, provider_type)

        # Can't create same worker again
        with self.assertRaises(EntryAlreadyExistsException):
            worker_id = db.new_worker(worker_name, provider_type)

        # Can't use no name
        with self.assertRaises(MephistoDBException):
            worker_id = db.new_worker('', provider_type)

        # TODO uncomment once Worker mock is created
        # # Ensure no workers were created
        # workers = db.find_workers()
        # self.assertEqual(len(workers), 1)

    def test_task_run(self) -> None:
        """Test creation and querying of task_runs"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        task_name, task_id = self.get_test_task()
        requester_name, requester_id = self.get_test_requester()

        # Check creation and retrieval of a task_run
        # TODO pull initial params from the task type?
        init_params = "--test --params"
        task_run_id = db.new_task_run(task_id, requester_id, init_params)
        self.assertIsNotNone(task_run_id)
        self.assertTrue(isinstance(task_run_id, str))
        task_run_row = db.get_task_run(task_run_id)
        self.assertEqual(task_run_row['init_params'], init_params)
        task_run = TaskRun(db, task_run_id)
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

        task_runs = db.find_task_runs(task_id=self.get_fake_id('Task'))
        self.assertEqual(len(task_runs), 0)

    def test_task_run_fails(self) -> None:
        """Ensure task_runs fail to be created or loaded under failure conditions"""
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db

        task_name, task_id = self.get_test_task()
        requester_name, requester_id = self.get_test_requester()
        init_params = "--test --params"

        # Can't create task run with invalid ids
        with self.assertRaises(EntryDoesNotExistException):
            task_run_id = db.new_task_run(self.get_fake_id('Task'), requester_id, init_params)
        with self.assertRaises(EntryDoesNotExistException):
            task_run_id = db.new_task_run(task_id, self.get_fake_id('Requester'), init_params)


        # Ensure no task_runs were created
        task_runs = db.find_task_runs()
        self.assertEqual(len(task_runs), 0)
