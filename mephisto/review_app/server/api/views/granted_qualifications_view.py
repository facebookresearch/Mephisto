#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.constants.assignment_state import AssignmentState

LIMIT_UNITS_FOR_QUALIFICATION = 3
STATUSES_UNITS_FOR_QUALIFICATION = AssignmentState.completed()


def _find_granted_qualifications(
    db: LocalMephistoDB,
    qualification_id: Optional[str] = None,
    sort_param: Optional[str] = None,
) -> List[StringIDRow]:
    """Return the granted qualifications in the database"""

    with db.table_access_condition:
        conn = db.get_connection()
        c = conn.cursor()

        params = []

        # Exclude granted qualifications for blocked workers
        blocked_worker_query = "blocked_worker IS NULL"

        qualification_query = "gq.qualification_id = ?1" if qualification_id else ""
        if qualification_id is not None:
            params.append(nonesafe_int(qualification_id))

        joined_queries = " AND ".join(
            list(
                filter(
                    bool,
                    [
                        blocked_worker_query,
                        qualification_query,
                    ],
                )
            )
        )

        where_query = f"WHERE {joined_queries}" if joined_queries else ""

        order_by_query = ""
        if sort_param:
            order_direction = "DESC" if sort_param.startswith("-") else "ASC"
            order_column = sort_param[1:] if sort_param.startswith("-") else sort_param
            order_by_query = f"ORDER BY {order_column} {order_direction}"

        c.execute(
            f"""
            SELECT
                gq.qualification_id AS qualification_id,
                q.qualification_name AS qualification_name,
                gq.worker_id AS worker_id,
                w.worker_name AS worker_name,
                gq.value AS value_current,
                gq.update_date AS granted_at,
                wr.blocked_worker AS blocked_worker
            FROM granted_qualifications AS gq
            LEFT JOIN (
                SELECT
                    worker_id,
                    worker_name,
                    creation_date
                FROM workers
            ) AS w ON w.worker_id = gq.worker_id
            LEFT JOIN (
                SELECT
                    qualification_id,
                    qualification_name,
                    creation_date
                FROM qualifications
            ) AS q ON q.qualification_id = gq.qualification_id
            LEFT JOIN (
                SELECT
                    id,
                    blocked_worker,
                    updated_qualification_id,
                    revoked_qualification_id,
                    worker_id,
                    creation_date
                FROM worker_review
                WHERE blocked_worker = 1
            ) AS wr ON (
                wr.worker_id = gq.worker_id AND (
                    (
                        wr.updated_qualification_id = gq.qualification_id AND
                        wr.revoked_qualification_id IS NULL
                    )
                    OR
                    (
                        wr.revoked_qualification_id = gq.qualification_id AND
                        wr.updated_qualification_id IS NULL
                    )
                )
            )
            {where_query}
            {order_by_query};
            """,
            params,
        )
        rows = c.fetchall()
        return rows


def _find_grants(
    db: LocalMephistoDB,
    worker_id: str,
    qualification_id: str,
    statuses: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[StringIDRow]:
    """Return the units for granted qualification"""

    with db.table_access_condition:
        conn = db.get_connection()
        c = conn.cursor()

        params = [
            nonesafe_int(worker_id),
            nonesafe_int(qualification_id),
        ]

        worker_query = "wr.worker_id = ?1"

        qualification_query = "wr.updated_qualification_id = ?2"

        units_statuses_string = ",".join([f"'{s}'" for s in statuses])
        status_query = f"status IN ({units_statuses_string})" if statuses else ""

        joined_queries = " AND ".join(
            list(
                filter(
                    bool,
                    [
                        worker_query,
                        qualification_query,
                    ],
                )
            )
        )

        where_query = f"WHERE {joined_queries}" if joined_queries else ""

        limit_query = "LIMIT ?3" if limit else ""
        if limit:
            params.append(nonesafe_int(limit))

        c.execute(
            f"""
            SELECT
                wr.task_id as task_id,
                t.task_name as task_name,
                wr.unit_id as unit_id,
                wr.updated_qualification_value as updated_qualification_value,
                wr.creation_date as creation_date
            FROM worker_review AS wr
            LEFT JOIN (
                SELECT
                    task_id,
                    task_name
                FROM tasks
            ) AS t ON t.task_id = wr.task_id
            LEFT JOIN (
                SELECT
                    unit_id,
                    status
                FROM units
                WHERE {status_query}
                ORDER BY creation_date DESC
            ) AS u ON u.unit_id = wr.unit_id
            {where_query}
            ORDER BY creation_date DESC
            {limit_query};
            """,
            params,
        )
        rows = c.fetchall()
        return rows


class GrantedQualificationsView(MethodView):
    def get(self) -> dict:
        """Get list of all granted queslifications."""

        qualification_id_param = request.args.get("qualification_id")
        sort_param = request.args.get("sort")

        db_granted_qualifications = _find_granted_qualifications(
            db=app.db,
            qualification_id=qualification_id_param,
            sort_param=sort_param,
        )

        app.logger.debug(f"Found granted qualifications in DB: {list(db_granted_qualifications)}")

        granted_qualifications = []
        for gq in db_granted_qualifications:
            units = [
                {
                    "creation_date": u["creation_date"],
                    "task_id": u["task_id"],
                    "task_name": u["task_name"],
                    "unit_id": u["unit_id"],
                    "value": u["updated_qualification_value"],
                }
                for u in _find_grants(
                    db=app.db,
                    worker_id=gq["worker_id"],
                    qualification_id=gq["qualification_id"],
                    statuses=STATUSES_UNITS_FOR_QUALIFICATION,
                    limit=LIMIT_UNITS_FOR_QUALIFICATION,
                )
            ]
            granted_qualifications.append(
                {
                    "granted_at": gq["granted_at"],
                    "qualification_id": gq["qualification_id"],
                    "qualification_name": gq["qualification_name"],
                    "units": units,
                    "value_current": gq["value_current"],
                    "worker_id": gq["worker_id"],
                    "worker_name": gq["worker_name"],
                },
            )

        return {
            "granted_qualifications": granted_qualifications,
        }
