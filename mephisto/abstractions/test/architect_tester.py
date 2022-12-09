#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import Optional, Type
import tempfile
import os
import shutil
import requests
from mephisto.abstractions.architect import Architect
from mephisto.data_model.task_run import TaskRun
from mephisto.utils.testing import get_test_task_run
from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockSharedState
from mephisto.abstractions.blueprints.mock.mock_task_builder import MockTaskBuilder
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.operations.hydra_config import MephistoConfig
from omegaconf import OmegaConf

EMPTY_STATE = MockSharedState()


class ArchitectTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable for a crowd
    """

    ArchitectClass: Type[Architect]
    db: MephistoDB
    data_dir: str
    build_dir: str
    curr_architect: Optional[Architect] = None

    warned_about_setup = False

    # Implementations of this test suite should implement the following methods.
    # See the mock architect for examples

    def server_is_prepared(self, build_dir: str) -> bool:
        """Ensure that the server is ready to be deployed from the given directory"""
        raise NotImplementedError()

    def server_is_cleaned(self, build_dir: str) -> bool:
        """Validate that server files are cleaned up following a deploy"""
        raise NotImplementedError()

    def server_is_shutdown(self) -> bool:
        """Validate that server is no longer running, ie shutdown successfully called"""
        raise NotImplementedError()

    def server_is_up(self, url: str) -> bool:
        """Ping the url to see if anything is running"""
        if url.endswith("/"):
            url = url[:-1]
        alive_url = url + "/is_alive"
        try:
            response = requests.get(alive_url)
        except requests.ConnectionError:
            return False
        return response.status_code == 200

    @classmethod
    def setUpClass(cls):
        """
        Only run tests on subclasses of this class, as this class is just defining the
        testing interface and the tests to run on an architect that adheres to the interface
        """
        if cls is ArchitectTests:
            raise unittest.SkipTest("Skip ArchitectTests tests, it's a base class")
        super(ArchitectTests, cls).setUpClass()

    def setUp(self) -> None:
        """
        Setup should put together any requirements for starting the database for a test.
        """
        try:
            _ = self.ArchitectClass
        except:
            raise unittest.SkipTest("Skipping test as no ArchitectClass set")
        if not self.warned_about_setup:
            print(
                "Architect tests may require using an account with the server provider "
                "in order to function properly. Make sure these are configured before testing."
            )
            self.warned_about_setup = True
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.build_dir = tempfile.mkdtemp()
        self.task_run = TaskRun.get(self.db, get_test_task_run(self.db))
        builder = MockTaskBuilder(self.task_run, OmegaConf.create({}))
        builder.build_in_dir(self.build_dir)

    def tearDown(self) -> None:
        """
        tearDown should clear up anything that was set up or
        used in any of the tests in this class.

        Generally this means cleaning up the database that was
        set up.
        """
        self.db.shutdown()
        shutil.rmtree(self.data_dir)
        shutil.rmtree(self.build_dir)

    def test_init_architect(self) -> None:
        """Simple test to ensure that an architect can be initialized with default
        arguments, and that it is the correct class
        """
        self.assertTrue(
            issubclass(self.ArchitectClass, Architect),
            "Implemented ArchitectClass does not extend Architect",
        )
        self.assertNotEqual(
            self.ArchitectClass, Architect, "Can not use base Architect"
        )
        arch_args = self.ArchitectClass.ArgsClass()
        args = OmegaConf.structured(MephistoConfig(architect=arch_args))
        architect = self.ArchitectClass(
            self.db, args, EMPTY_STATE, self.task_run, self.build_dir
        )

    def get_architect(self) -> Architect:
        """
        Return an initialized architect to use in testing. Can be overridden if
        special parameters need to be set to run tests properly.
        """
        arch_args = self.ArchitectClass.ArgsClass()
        args = OmegaConf.structured(MephistoConfig(architect=arch_args))
        self.curr_architect = self.ArchitectClass(
            self.db, args, EMPTY_STATE, self.task_run, self.build_dir
        )
        return self.curr_architect

    def test_prepare_cleanup(self) -> None:
        """Test preparation and cleanup for server"""
        architect = self.get_architect()
        built_dir = architect.prepare()
        self.assertTrue(os.path.exists(built_dir))
        self.assertTrue(self.server_is_prepared(self.build_dir))
        architect.cleanup()
        self.assertTrue(self.server_is_cleaned(self.build_dir))

    def test_deploy_shutdown(self) -> None:
        """Test deploying the server, and shutting it down"""
        architect = self.get_architect()
        architect.prepare()
        self.assertTrue(self.server_is_prepared(self.build_dir))
        server_url = architect.deploy()
        self.assertTrue(self.server_is_up(server_url))
        architect.cleanup()
        self.assertTrue(self.server_is_cleaned(self.build_dir))
        architect.shutdown()
        self.assertFalse(self.server_is_up(server_url))
        self.assertTrue(self.server_is_shutdown())
