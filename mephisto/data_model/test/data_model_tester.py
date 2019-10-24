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
from mephisto.data_model.database import MephistoDB


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

