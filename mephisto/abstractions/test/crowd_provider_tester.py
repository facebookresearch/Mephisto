#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from typing import Optional, Tuple, Type
import tempfile
import mephisto
import os
import shutil
from mephisto.data_model.requester import Requester
from mephisto.data_model.worker import Worker
from mephisto.abstractions.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.crowd_provider import CrowdProvider


class CrowdProviderTests(unittest.TestCase):
    """
    This class contains the basic data model tests that should
    be passable for a crowd
    """

    CrowdProviderClass: Type[CrowdProvider]
    db: MephistoDB
    data_dir: str

    warned_about_setup = False

    @classmethod
    def setUpClass(cls):
        """
        Only run tests on subclasses of this class, as this class is just defining the
        testing interface and the tests to run on a DB that adheres to that interface
        """
        if cls is CrowdProviderTests:
            raise unittest.SkipTest("Skip CrowdProviderTests tests, it's a base class")
        super(CrowdProviderTests, cls).setUpClass()

    def get_test_worker_name(self) -> str:
        """Return a worker name that is usable for testing with this crowdprovider"""
        raise NotImplementedError()

    def get_test_requester_name(self) -> str:
        """Return a requester name that is usable for testing with this crowdprovider"""
        raise NotImplementedError()

    def get_test_requester_balance(self, requester_name: str) -> float:
        """Get the amount that test accounts are expected to have"""
        raise NotImplementedError()

    def setUp(self) -> None:
        """
        Setup should put together any requirements for starting the database for a test.
        """
        if not self.warned_about_setup:
            print(
                "Provider tests require using a test account for that crowd provider, "
                "you may need to set this up on your own."
            )
            self.warned_about_setup = True
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)

    def tearDown(self) -> None:
        """
        tearDown should clear up anything that was set up or
        used in any of the tests in this class.

        Generally this means cleaning up the database that was
        set up.
        """
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    def get_test_requester(self) -> Requester:
        """Create a requester to use in tests and register it"""
        db: MephistoDB = self.db
        RequesterClass = self.CrowdProviderClass.RequesterClass
        return RequesterClass.new(db, self.get_test_requester_name())

    def test_init_registers_datastore(self) -> None:
        """Ensure that initializing the crowd provider registers
        a datastore with the database, as this is required functionality
        for all crowd providers.
        """
        ProviderClass = self.CrowdProviderClass
        self.assertFalse(
            self.db.has_datastore_for_provider(ProviderClass.PROVIDER_TYPE)
        )
        # Initialize the provider
        provider = ProviderClass(self.db)
        self.assertTrue(self.db.has_datastore_for_provider(ProviderClass.PROVIDER_TYPE))

    def test_init_object_registers_datastore(self) -> None:
        """Ensure that initializing the crowd provider registers
        a datastore with the database, as this is required functionality
        for all crowd providers.
        """
        ProviderClass = self.CrowdProviderClass
        self.assertFalse(
            self.db.has_datastore_for_provider(ProviderClass.PROVIDER_TYPE)
        )
        # Initialize the requester
        RequesterClass = ProviderClass.RequesterClass
        requester = RequesterClass.new(self.db, self.get_test_requester_name())
        self.assertTrue(self.db.has_datastore_for_provider(ProviderClass.PROVIDER_TYPE))

    def test_requester(self) -> None:
        """Ensure we can create and use a requester"""
        db: MephistoDB = self.db
        RequesterClass = self.CrowdProviderClass.RequesterClass
        test_requester = RequesterClass.new(db, self.get_test_requester_name())
        test_requester_2 = Requester.get(db, test_requester.db_id)
        self.assertEqual(
            test_requester.requester_name,
            test_requester_2.requester_name,
            "Requester gotten from db not same as first init",
        )

        # Ensure credential registration works
        # TODO(#97) ensure registration fails when we programatically login to an account
        # in the future
        # self.assertFalse(test_requester.is_registered())
        test_requester.register()
        self.assertTrue(test_requester.is_registered())

        # Ensure requester methods work
        avail_budget = test_requester.get_available_budget()
        test_budget = self.get_test_requester_balance(test_requester.requester_name)
        self.assertEqual(
            avail_budget,
            test_budget,
            "Queried budget from `get_available_budget` not equal to `test_budget`",
        )

    def test_worker(self) -> None:
        """Ensure we can query and use a worker"""
        db: MephistoDB = self.db
        requester = self.get_test_requester()
        WorkerClass = self.CrowdProviderClass.WorkerClass
        test_worker = WorkerClass.new(db, self.get_test_worker_name())
        test_worker_2 = Worker.get(db, test_worker.db_id)
        self.assertEqual(
            test_worker.worker_name,
            test_worker_2.worker_name,
            "Worker gotten from db not same as first init",
        )

        # Ensure blocking is doable
        test_worker.block_worker("Test reason", requester=requester)
        self.assertTrue(test_worker.is_blocked(requester))
        test_worker.unblock_worker("Test reason", requester=requester)
        self.assertFalse(test_worker.is_blocked(requester))

        # TODO(#97) is it possible to test worker bonuses?
        # TODO(#97) is it possible to test eligibility?

    # TODO(#97) implmeent the following after test tasks are possible
    # def test_unit(self) -> None:
    # def test_agent(self) -> None:
