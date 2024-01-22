#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.review_app.server.db_queries import find_units


class TaskUnitIdsView(MethodView):
    def get(self, task_id) -> dict:
        """
        Get full, unpaginated list of unit IDs within a task
        (for subsequent client-side grouping by worker_id and GET /task-units pagination)
        """

        db_task: StringIDRow = app.db.get_task(task_id)
        app.logger.debug(f"Found task in DB: {dict(db_task)}")

        db_units: List[StringIDRow] = find_units(
            app.db,
            int(db_task["task_id"]),
            statuses=AssignmentState.completed(),
            debug=app.debug,
        )

        app.logger.debug(f"All units: {[u['unit_id'] for u in db_units]}")

        worker_units_ids = []
        for db_unit in db_units:
            if db_unit["status"] != AssignmentState.COMPLETED:
                continue

            worker_units_ids.append(
                {
                    "worker_id": db_unit["worker_id"],
                    "unit_id": db_unit["unit_id"],
                }
            )

        app.logger.debug(f"Worker Units IDs: {worker_units_ids}")

        return {
            "worker_units_ids": worker_units_ids,
        }
