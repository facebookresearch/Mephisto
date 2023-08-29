#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from dateutil.parser import parse
from dateutil.parser import ParserError
from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.worker import Worker


def _find_unit_reviews(
    db,
    worker_id: str,
    task_id: Optional[str] = None,
    status: Optional[str] = None,
    since: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[StringIDRow]:
    params = [nonesafe_int(worker_id)]

    task_query = "AND (task_id = ?)" if task_id else ""
    if task_id:
        params.append(nonesafe_int(task_id))

    status_query = "AND (status = ?)" if status else ""
    if status:
        params.append(status)

    since_query = "AND (created_at >= ?)" if since else ""
    if since:
        params.append(since)

    limit_query = "LIMIT ?" if limit else ""
    if limit:
        params.append(nonesafe_int(limit))

    with db.table_access_condition:
        conn = db._get_connection()
        conn.set_trace_callback(print)
        c = conn.cursor()
        c.execute(
            f"""
            SELECT * FROM unit_review
            WHERE (worker_id = ?) {task_query} {status_query} {since_query}
            ORDER BY created_at ASC {limit_query};
            """,
            params,
        )

        results = c.fetchall()
        return results


class WorkerStatsView(MethodView):
    def get(self, worker_id: int) -> dict:
        """ Get stats of recent approvals for the worker """

        # Check if exists. Raises exceptions in case if not
        worker: Worker = Worker.get(app.db, str(worker_id))

        task_id = request.args.get("task_id")
        limit = request.args.get("limit")
        since = request.args.get("since")

        # Validate `since` and change format
        if since:
            try:
                since = parse(since).strftime("%Y-%m-%d %H:%M:%S")
            except ParserError:
                raise BadRequest("Wrong date format.")

        approved_unit_reviews = _find_unit_reviews(
            db=app.db,
            worker_id=worker.db_id,
            task_id=task_id,
            status=AssignmentState.ACCEPTED,
            since=since,
            limit=limit,
        )
        rejected_unit_reviews = _find_unit_reviews(
            db=app.db,
            worker_id=worker.db_id,
            task_id=task_id,
            status=AssignmentState.REJECTED,
            since=since,
            limit=limit,
        )
        soft_rejected_unit_reviews = _find_unit_reviews(
            db=app.db,
            worker_id=worker.db_id,
            task_id=task_id,
            status=AssignmentState.SOFT_REJECTED,
            since=since,
            limit=limit,
        )
        all_unit_reviews = _find_unit_reviews(db=app.db, worker_id=worker.db_id)

        return {
            "worker_id": worker.db_id,
            "stats": {
                "total_count": len(all_unit_reviews),  # within the scope of the filters
                "approved_count": len(approved_unit_reviews),
                "rejected_count": len(rejected_unit_reviews),
                "soft_rejected_count": len(soft_rejected_unit_reviews),
            },
        }
