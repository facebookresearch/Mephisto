#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
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

from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.constants.assignment_state import AssignmentState


def _find_unit_reviews(
    db,
    worker_id: Optional[str] = None,
    task_id: Optional[str] = None,
    status: Optional[str] = None,
    since: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[StringIDRow]:
    params = []

    worker_query = "worker_id = ?" if worker_id else ""
    if worker_id:
        params.append(nonesafe_int(worker_id))

    task_query = "task_id = ?" if task_id else ""
    if task_id:
        params.append(nonesafe_int(task_id))

    status_query = "status = ?" if status else ""
    if status:
        params.append(status)

    since_query = "created_at >= ?" if since else ""
    if since:
        params.append(since)

    joined_queries = " AND ".join(
        list(
            filter(
                bool,
                [
                    worker_query,
                    task_query,
                    status_query,
                    since_query,
                ],
            )
        )
    )

    where_query = f"WHERE {joined_queries}" if joined_queries else ""

    limit_query = "LIMIT ?" if limit else ""
    if limit:
        params.append(nonesafe_int(limit))

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()
        c.execute(
            f"""
            SELECT * FROM unit_review
            {where_query}
            ORDER BY created_at ASC {limit_query};
            """,
            params,
        )

        results = c.fetchall()
        return results


def _find_units_for_worker(
    db,
    worker_id: Optional[str] = None,
    task_id: Optional[str] = None,
    statuses: Optional[List[str]] = None,
    since: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[StringIDRow]:
    params = []

    worker_query = "worker_id = ?" if worker_id else ""
    if worker_id:
        params.append(nonesafe_int(worker_id))

    task_query = "task_id = ?" if task_id else ""
    if task_id:
        params.append(nonesafe_int(task_id))

    statuses_string = ",".join([f"'{s}'" for s in statuses])
    status_query = f"status IN ({statuses_string})" if statuses else ""

    since_query = "creation_date >= ?" if since else ""
    if since:
        params.append(since)

    joined_queries = " AND ".join(
        list(
            filter(
                bool,
                [
                    worker_query,
                    task_query,
                    status_query,
                    since_query,
                ],
            )
        )
    )

    where_query = f"WHERE {joined_queries}" if joined_queries else ""

    limit_query = "LIMIT ?" if limit else ""
    if limit:
        params.append(nonesafe_int(limit))

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()
        c.execute(
            f"""
            SELECT * FROM units
            {where_query}
            ORDER BY creation_date ASC {limit_query};
            """,
            params,
        )

        results = c.fetchall()
        return results


class StatsView(MethodView):
    def get(self) -> dict:
        """Get stats of recent approvals for the worker or task"""

        worker_id = request.args.get("worker_id")
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
            worker_id=worker_id,
            task_id=task_id,
            status=AgentState.STATUS_APPROVED,
            since=since,
            limit=limit,
        )
        rejected_unit_reviews = _find_unit_reviews(
            db=app.db,
            worker_id=worker_id,
            task_id=task_id,
            status=AgentState.STATUS_REJECTED,
            since=since,
            limit=limit,
        )
        soft_rejected_unit_reviews = _find_unit_reviews(
            db=app.db,
            worker_id=worker_id,
            task_id=task_id,
            status=AgentState.STATUS_SOFT_REJECTED,
            since=since,
            limit=limit,
        )
        all_units_for_worker = _find_units_for_worker(
            db=app.db,
            worker_id=worker_id,
            task_id=task_id,
            statuses=AssignmentState.completed(),
            since=since,
            limit=limit,
        )

        reviewed_reviews = (
            approved_unit_reviews + rejected_unit_reviews + soft_rejected_unit_reviews
        )

        return {
            "stats": {
                "total_count": len(all_units_for_worker),  # within the scope of the filters
                "reviewed_count": len(reviewed_reviews),
                "approved_count": len(approved_unit_reviews),
                "rejected_count": len(rejected_unit_reviews),
                "soft_rejected_count": len(soft_rejected_unit_reviews),
            },
        }
