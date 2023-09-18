#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from dateutil.parser import parse
from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow
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


def _find_units(
    db, task_id: int, statuses: Optional[List[str]] = None, debug: bool = False,
) -> List[StringIDRow]:
    with db.table_access_condition:
        conn = db._get_connection()

        if debug:
            conn.set_trace_callback(print)

        params = []

        task_query = "task_id = ?" if task_id else ""
        if task_id:
            params.append(nonesafe_int(task_id))

        statuses_string = ",".join([f"'{s}'" for s in statuses])
        status_query = f"status IN ({statuses_string})" if statuses else ""

        joined_queries = ' AND '.join(list(filter(bool, [task_query, status_query])))

        where_query = f"WHERE {joined_queries}" if joined_queries else ""

        c = conn.cursor()
        c.execute(
            f"""
            SELECT * from units
            {where_query};
            """,
            params,
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
            db_units: List[StringIDRow] = _find_units(
                app.db, int(t["task_id"]), statuses=AssignmentState.completed(), debug=app.debug,
            )

            for u in db_units:
                print(f'{u["unit_id"]=}, {u["status"]=}')

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
