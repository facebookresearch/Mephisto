#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.task import Task
from mephisto.data_model.constants import NO_PROJECT_NAME

from typing import List


class Project:
    """
    High level project that many crowdsourcing tasks may be related to. Useful
    for budgeting and grouping tasks for a review perspective.

    Abstracts relevant queries behind usable functions.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        project_row = self.db.get_project(db_id)
        self.project_name: str = project_row["project_name"]

    def get_tasks(self) -> List[Task]:
        """
        Return the list of tasks that are run as part of this project
        """
        return self.db.find_tasks(project_id=self.db_id)

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent for this project
        across all tasks.
        """
        tasks = self.get_tasks()
        sum_total = 0
        for task in tasks:
            sum_total += task.get_total_spend()
        return sum_total

    @staticmethod
    def new(self, project_name: str, db: MephistoDB) -> Project:
        """
        Try to create a new project by this name, raise an exception if
        the name already exists.
        """
        assert project_name != NO_PROJECT_NAME, f'{project_name} is a reserved name that cannot be used as a project name.'
        db_id = db.new_project(project_name)
        return Project(db, db_id)
