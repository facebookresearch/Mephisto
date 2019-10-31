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
from mephisto.data_model.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.crowd_provider import CrowdProvider


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
        return "ALNAP8V96IIO0"
        raise NotImplementedError()

    def get_test_requester_name(self) -> str:
        """Return a requester name that is usable for testing with this crowdprovider"""
        return "UNIT_TEST_REQUESTER"
        raise NotImplementedError()

    def get_test_requester_balance(self, requester_name: str) -> float:
        """Get the amount that test accounts are expected to have"""
        raise NotImplementedError

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
        self.provider = self.CrowdProviderClass(self.db)

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
        assert self.provider is not None, "No db initialized"
        db: MephistoDB = self.db
        provider: CrowdProvider = self.provider
        RequesterClass = provider.RequesterClass
        return RequesterClass.new(db, self.get_test_requester_name())

    def test_requester(self) -> None:
        """Ensure we can create and use a requester"""
        assert self.provider is not None, "No db initialized"
        db: MephistoDB = self.db
        provider: CrowdProvider = self.provider
        RequesterClass = provider.RequesterClass
        test_requester = RequesterClass.new(db, self.get_test_requester_name())
        test_requester_2 = Requester(db, test_requester.db_id)
        self.assertEqual(test_requester.requester_name, test_requester_2.requester_name, "Requester gotten from db not same as first init")
        # Ensure credential registration works
        test_requester.register_credentials()

        # Ensure requester methods work
        avail_budget = test_requester.get_available_budget()
        test_budget = self.get_test_requester_balance(test_requester.requester_name)
        self.assertEqual(avail_budget, test_budget, "Queried budget from `get_available_budget` not equal to `test_budget`")

    def test_worker(self) -> None:
        """Ensure we can query and use a worker"""
        assert self.provider is not None, "No db initialized"
        db: MephistoDB = self.db
        provider: CrowdProvider = self.provider
        requester = self.get_test_requester()
        WorkerClass = provider.WorkerClass
        test_worker = WorkerClass.new(db, self.get_test_worker_name())
        test_worker_2 = Worker(db, test_worker.db_id)
        self.assertEqual(test_worker.worker_name, test_worker_2.worker_name, "Worker gotten from db not same as first init")

        # Ensure blocking is doable
        test_worker.block_worker('Test reason', requester=requester)
        self.assertTrue(test_worker.is_blocked(requester))
        test_worker.unblock_worker('Test reason', requester=requester)
        self.assertFalse(test_worker.is_blocked(requester))

        # TODO is it possible to test worker bonuses?
        # TODO is it possible to test eligibility?

    # TODO implmeent the following after test tasks are possible
    # def test_unit(self) -> None:
    # def test_agent(self) -> None:
