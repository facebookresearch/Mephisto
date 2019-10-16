#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.task import TaskRun

from typing import List


class Requester:
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database
        self.crowd_provider_type: str = None
        self.requester_name: str = None

    def get_task_runs(self) -> List[TaskRun]:
        """
        Return the list of task runs that are run by this requester
        """
        # TODO query the database for tasks that are registered under this,
        # and return them.
        pass

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent by this requester
        across all tasks.
        """
        # TODO get all the tasks with get_tasks, and then return the
        # sum spend of each of them.
        pass

    @staticmethod
    def new(self, requester_name: str, crowd_provider: str, db: MephistoDB) -> Project:
        """
        Try to create a new requester by this name, raise an exception if
        the name already exists.
        """
        # TODO create an entry in the MephistoDB, then return the object
        # > db_id = MephistoDB.new_project()
        # > return Project(db_id)
        # TODO update to take in a crowdprovider type
        pass
