#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.database import MephistoDB
from mephisto.data_model.task import TaskRun
from mephisto.core.utils import get_crowd_provider_from_type

from typing import List


class Requester(ABC):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        row = db.get_requester(db_id)
        self.provider_type: str = row["provider_type"]
        self.requester_name: str = row["requester_name"]

    def __new__(cls, db: MephistoDB, db_id: str) -> Unit:
        """
        The new method is overridden to be able to automatically generate
        the expected Requester class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Requester
        as you will instead be returned the correct Requester class according to
        the crowdprovider associated with this Requester.
        """
        if cls == Requester:
            # We are trying to construct a Requester, find what type to use and
            # create that instead
            row = db.get_requester(db_id)
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).RequesterClass
            return super().__new__(correct_class, db, db_id)
        else:
            # We are constructing another instance directly
            return super().__new__(cls, db, db_id)

    def get_task_runs(self) -> List[TaskRun]:
        """
        Return the list of task runs that are run by this requester
        """
        return self.db.find_task_runs(requester_id=self.db_id)

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent by this requester
        across all tasks.
        """
        task_runs = self.db.find_task_runs(requester_id=self.db_id)
        total_spend = 0
        for run in task_runs:
            total_spend += run.get_total_spend()
        return total_spend

    @staticmethod
    def _register_requester(
        db: MephistoDB, requester_id: str, provider_type: str
    ) -> Requester:
        """
        Create an entry for this requester in the database
        """
        db_id = db.new_requester(requester_id, provider_type)
        return Requester(db, db_id)

    @abstractstaticmethod
    def new(self, db: MephistoDB, requester_name: str) -> Project:
        """
        Try to create a new requester by this name, raise an exception if
        the name already exists.

        Implementation should call _register_requester(db, requester_id) when sure the requester
        can be successfully created to have it put into the db and return the result.
        """
        raise NotImplementedError()
