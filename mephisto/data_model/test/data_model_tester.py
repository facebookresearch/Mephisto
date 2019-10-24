#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import Optional
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


class BaseDataModelTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable by any database that intends to be an implementation
    of the MephistoDB class.
    """

    db: Optional[MephistoDB] = None

    @classmethod
    def setUpClass(cls):
        if cls is BaseDataModelTests:
            raise unittest.SkipTest("Skip BaseDataModelTests tests, it's a base class")
        super(BaseDataModelTests, cls).setUpClass()

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


    def test_all_types_init_empty(self) -> None:
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

    def get_test_project(self) -> None:
        assert self.db is not None, 'No db initialized'
        db: MephistoDB = self.db
        project_name = 'test_project'
        project_id = db.new_project(project_name)
        return project_name, project_id

    def test_task(self) -> None:
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
        with self.assertRaises(EntryAlreadyExistsException):
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
