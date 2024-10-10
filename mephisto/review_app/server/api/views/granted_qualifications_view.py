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

        c.execute(
            f"""
            SELECT
                gq.qualification_id AS qualification_id,
                q.qualification_name AS qualification_name,
                gq.worker_id AS worker_id,
                w.worker_name AS worker_name,
                gq.value AS current_value,
                gq.update_date AS granted_at,
                ur.blocked_worker AS blocked_worker
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
                FROM unit_review
                WHERE blocked_worker = 1
            ) AS ur ON (
                ur.worker_id = gq.worker_id AND (
                    (
                        ur.updated_qualification_id = gq.qualification_id AND
                        ur.revoked_qualification_id IS NULL
                    )
                    OR
                    (
                        ur.revoked_qualification_id = gq.qualification_id AND
                        ur.updated_qualification_id IS NULL
                    )
                )
            )
            {where_query};
            """,
            params,
        )
        rows = c.fetchall()
        return rows


def _find_units(
    db: LocalMephistoDB,
    worker_id: str,
    qualification_id: str,
    statuses: Optional[List[str]] = None,
    units_limit: Optional[int] = None,
) -> List[StringIDRow]:
    """Return the units for granted qualification"""

    with db.table_access_condition:
        conn = db.get_connection()
        c = conn.cursor()

        params = [
            nonesafe_int(worker_id),
            nonesafe_int(qualification_id),
        ]

        worker_query = "ur.worker_id = ?1"

        qualification_query = "ur.updated_qualification_id = ?2"

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

        units_limit_query = "LIMIT ?3" if units_limit else ""
        if units_limit:
            params.append(nonesafe_int(units_limit))

        c.execute(
            f"""
            SELECT
                ur.task_id as task_id,
                t.task_name as task_name,
                ur.unit_id as unit_id,
                ur.updated_qualification_value
            FROM unit_review AS ur
            LEFT JOIN (
                SELECT
                    task_id,
                    task_name
                FROM tasks
            ) AS t ON t.task_id = ur.task_id
            LEFT JOIN (
                SELECT
                    unit_id,
                    status
                FROM units
                WHERE {status_query}
                ORDER BY creation_date DESC {units_limit_query}
            ) AS u ON u.unit_id = ur.unit_id
            {where_query}
            ORDER BY creation_date DESC;
            """,
            params,
        )
        rows = c.fetchall()
        return rows


class GrantedQualificationsView(MethodView):
    def get(self) -> dict:
        """Get list of all granted queslifications."""

        qualification_id = request.args.get("qualification_id")

        db_granted_qualifications = _find_granted_qualifications(
            db=app.db,
            qualification_id=qualification_id,
        )

        app.logger.debug(f"Found granted qualifications in DB: {list(db_granted_qualifications)}")

        granted_qualifications = []
        for gq in db_granted_qualifications:
            units = [
                {
                    "task_id": u["task_id"],
                    "task_name": u["task_name"],
                    "unit_id": u["unit_id"],
                    "value": u["updated_qualification_value"],
                }
                for u in _find_units(
                    db=app.db,
                    worker_id=gq["worker_id"],
                    qualification_id=gq["qualification_id"],
                    statuses=STATUSES_UNITS_FOR_QUALIFICATION,
                    units_limit=LIMIT_UNITS_FOR_QUALIFICATION,
                )
            ]
            granted_qualifications.append(
                {
                    "granted_at": gq["granted_at"],
                    "qualification_id": gq["qualification_id"],
                    "qualification_name": gq["qualification_name"],
                    "units": units,
                    "value_current": gq["current_value"],
                    "worker_id": gq["worker_id"],
                    "worker_name": gq["worker_name"],
                },
            )

        return {
            "granted_qualifications": granted_qualifications,
        }
