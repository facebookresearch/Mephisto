#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.task import Task

from typing import List


class Project:
    """
    High level project that many crowdsourcing tasks may be related to. Useful
    for budgeting and grouping tasks for a review perspective.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        # TODO pull info for this from the database
        self.project_name: str = None

    def get_tasks(self) -> List[Task]:
        """
        Return the list of tasks that are run as part of this project
        """
        # TODO query the database for tasks that are registered under this,
        # and return them.
        pass

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent for this project
        across all tasks.
        """
        # TODO get all the tasks with get_tasks, and then return the
        # sum spend of each of them.
        pass

    @staticmethod
    def new(self, project_name: str, db: MephistoDB) -> Project:
        """
        Try to create a new project by this name, raise an exception if
        the name already exists.
        """
        # TODO create an entry in the MephistoDB, then return the object
        # > db_id = MephistoDB.new_project()
        # > return Project(db_id)
        pass
