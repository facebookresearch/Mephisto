#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from dateutil.parser import parse
from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.client.review_app.server.db_queries import find_units
from mephisto.data_model.constants.assignment_state import AssignmentState


def _find_tasks(db, debug: bool = False) -> List[StringIDRow]:
    with db.table_access_condition:
        conn = db._get_connection()

        if debug:
            conn.set_trace_callback(print)

        c = conn.cursor()
        c.execute(
            """
            SELECT * from tasks
            """
        )
        rows = c.fetchall()

        if debug:
            conn.set_trace_callback(None)

        return rows


class TasksView(MethodView):
    def get(self) -> dict:
        """ Get all available tasks (to select one for review) """

        db_tasks: List[StringIDRow] = _find_tasks(app.db, debug=app.debug)
        app.logger.debug(f"Found tasks in DB: {[t['task_id'] for t in db_tasks]}")

        tasks = []
        for t in db_tasks:
            db_units: List[StringIDRow] = find_units(
                app.db, int(t["task_id"]), statuses=AssignmentState.completed(), debug=app.debug,
            )

            app.logger.debug(f"All finished units: {[u['unit_id'] for u in db_units]}")

            unit_count = len(db_units)
            is_reviewed = all([u["status"] != AssignmentState.COMPLETED for u in db_units])

            tasks.append(
                {
                    "id": t["task_id"],
                    "name": t["task_name"],
                    "is_reviewed": is_reviewed,
                    "unit_count": unit_count,
                    "created_at": parse(t["creation_date"]).isoformat(),
                }
            )

        app.logger.debug(f"Tasks: {tasks}")

        return {
            "tasks": tasks,
        }
