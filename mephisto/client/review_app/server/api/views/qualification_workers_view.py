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


def _find_granted_qualifications(db: LocalMephistoDB, qualification_id: str) -> List[StringIDRow]:
    """Return the granted qualifications in the database by the given qualification id"""

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()
        c.execute(
            f"""
            SELECT * FROM granted_qualifications
            WHERE (qualification_id = ?1);
            """,
            (nonesafe_int(qualification_id),),
        )

        results = c.fetchall()
        return results


def _find_unit_reviews(
    db,
    qualification_id: str,
    worker_id: str,
    task_id: Optional[str] = None,
) -> List[StringIDRow]:
    """
    Return unit reviews in the db by the given Qualification ID, Worker ID and Task ID
    """

    params = [nonesafe_int(qualification_id), nonesafe_int(worker_id)]
    task_query = "AND (task_id = ?3)" if task_id else ""
    if task_id:
        params.append(nonesafe_int(task_id))

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()
        c.execute(
            f"""
            SELECT * FROM unit_review
            WHERE (updated_qualification_id = ?1) AND (worker_id = ?2) {task_query}
            ORDER BY created_at ASC;
            """,
            params,
        )

        results = c.fetchall()
        return results


class QualificationWorkersView(MethodView):
    def get(self, qualification_id) -> dict:
        """Get list of all bearers of a qualification."""

        task_id = request.args.get("task_id")

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        app.logger.debug(f"Found qualification in DB: {dict(db_qualification)}")

        db_granted_qualifications = _find_granted_qualifications(app.db, qualification_id)

        app.logger.debug(
            f"Found granted qualifications for this qualification in DB: "
            f"{db_granted_qualifications}"
        )

        workers = []

        for gq in db_granted_qualifications:
            unit_reviews = _find_unit_reviews(app.db, qualification_id, gq["worker_id"], task_id)

            if unit_reviews:
                latest_unit_review = unit_reviews[-1]
                unit_review_id = latest_unit_review["id"]
                granted_at = latest_unit_review["created_at"]
            else:
                continue

            workers.append(
                {
                    "worker_id": gq["worker_id"],
                    "value": gq["value"],
                    "unit_review_id": unit_review_id,  # latest grant of this qualification
                    "granted_at": granted_at,  # maps to `unit_review.created_at` column
                }
            )

        return {
            "workers": workers,
        }
