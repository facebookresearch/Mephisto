#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.unit import Unit


class TasksWorkerUnitsView(MethodView):
    def get(self, task_id) -> dict:
        """
        Get full, unpaginated list of unit IDs within a task
        (for subsequent client-side grouping by worker_id and GET /task-units pagination)
        """

        db_task: StringIDRow = app.db.get_task(task_id)
        app.logger.debug(f"Found task in DB: {dict(db_task)}")

        units: List[Unit] = app.data_browser.get_units_for_task_name(db_task["task_name"])

        worker_units_ids = []
        for u in units:
            app.logger.debug(f"All units: {units}")

            worker_units_ids.append(
                {
                    "worker_id": u.worker_id,
                    "unit_id": u.db_id,
                }
            )

        app.logger.debug(f"Worker Units IDs: {worker_units_ids}")

        return {
            "worker_units_ids": worker_units_ids,
        }
