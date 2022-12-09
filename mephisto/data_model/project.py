#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)

from typing import List, Mapping, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task import Task


class Project(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    """
    High level project that many crowdsourcing tasks may be related to. Useful
    for budgeting and grouping tasks for a review perspective.

    Abstracts relevant queries behind usable functions.
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct Project and data model access via Project(db, id) is "
                "now deprecated in favor of calling Project.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = self.db.get_project(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["project_id"]
        self.project_name: str = row["project_name"]

    def get_tasks(self) -> List["Task"]:
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
        sum_total = 0.0
        for task in tasks:
            sum_total += task.get_total_spend()
        return sum_total

    @staticmethod
    def new(self, db: "MephistoDB", project_name: str) -> "Project":
        """
        Try to create a new project by this name, raise an exception if
        the name already exists.
        """
        assert (
            project_name != NO_PROJECT_NAME
        ), f"{project_name} is a reserved name that cannot be used as a project name."
        db_id = db.new_project(project_name)
        return Project.get(db, db_id)
