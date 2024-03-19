#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.worker import Worker


def _find_granted_qualifications(db: LocalMephistoDB, worker_id: str) -> List[StringIDRow]:
    """Return the granted qualifications in the database by the given worker id"""

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()
        c.execute(
            """
            SELECT
                gq.value,
                gq.worker_id,
                gq.qualification_id,
                gq.granted_qualification_id,
                ur.created_at AS granted_at
            FROM granted_qualifications AS gq
            LEFT JOIN (
                SELECT
                    updated_qualification_id,
                    created_at
                FROM unit_review
                ORDER BY created_at DESC
                /*
                We’re retrieving unit_review data only
                for the latest update of the worker-qualification pair.
                */
                LIMIT 1
            ) AS ur ON ur.updated_qualification_id = gq.qualification_id
            WHERE gq.worker_id = ?1
            """,
            (worker_id,),
        )
        rows = c.fetchall()
        return rows


class WorkerGrantedQualificationsView(MethodView):
    def get(self, worker_id: int) -> dict:
        """Get list of all granted queslifications for a worker."""

        worker: Worker = Worker.get(app.db, str(worker_id))
        app.logger.debug(f"Found Worker in DB: {worker}")

        db_granted_qualifications = _find_granted_qualifications(app.db, worker.db_id)

        app.logger.debug(
            f"Found granted qualifications for worker {worker_id} in DB: "
            f"{list(db_granted_qualifications)}"
        )

        granted_qualifications = []
        for gq in db_granted_qualifications:
            granted_qualifications.append(
                {
                    "worker_id": gq["worker_id"],
                    "qualification_id": gq["qualification_id"],
                    "value": int(gq["value"]),
                    "granted_at": gq["worker_id"],  # maps to `unit_review.created_at` column
                },
            )

        return {
            "granted_qualifications": granted_qualifications,
        }
