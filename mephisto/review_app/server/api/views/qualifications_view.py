#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.qualification import GrantedQualification
from mephisto.data_model.qualification import Qualification


def _find_qualifications_by_ids(
    db,
    qualification_ids: List[str],
    debug: bool = False,
) -> List[Qualification]:
    with db.table_access_condition:
        conn = db._get_connection()

        c = conn.cursor()

        qualifications_string = ",".join([f"{s}" for s in qualification_ids])
        qualification_query = (
            f"qualification_id IN ({qualifications_string})" if qualification_ids else ""
        )

        where_query = f"WHERE {qualification_query}" if qualification_query else ""

        c.execute(
            f"""
            SELECT * from qualifications
            {where_query}
            """
        )
        rows = c.fetchall()

        return [
            Qualification(db, str(r["qualification_id"]), row=r, _used_new_call=True) for r in rows
        ]


class QualificationsView(MethodView):
    def get(self) -> dict:
        """Get all available qualifications (to select "approve" and "reject" qualifications)"""

        worker_id = request.args.get("worker_id")

        if worker_id:
            db_granted_qualifications: List[
                GrantedQualification
            ] = app.db.find_granted_qualifications(worker_id)

            db_qualifications: List[Qualification] = []
            if db_granted_qualifications:
                db_qualifications: List[Qualification] = _find_qualifications_by_ids(
                    app.db,
                    qualification_ids=[gq.qualification_id for gq in db_granted_qualifications],
                    debug=True,
                )

        else:
            db_qualifications: List[Qualification] = app.db.find_qualifications()
            app.logger.debug(f"Found qualifications in DB: {db_qualifications}")

        qualifications = [
            {
                "id": q.db_id,
                "name": q.qualification_name,
            }
            for q in db_qualifications
        ]

        app.logger.debug(f"Qualifications: {qualifications}")

        return {
            "qualifications": qualifications,
        }

    def post(self) -> dict:
        """Create a new qualification"""

        data: dict = request.json
        qualification_name = data and data.get("name")

        if not qualification_name:
            raise BadRequest('Field "name" is required.')

        db_qualifications: List[Qualification] = app.db.find_qualifications(qualification_name)

        if db_qualifications:
            raise BadRequest(f'Qualification with name "{qualification_name}" already exists.')

        db_qualification_id: str = app.db.make_qualification(qualification_name)
        db_qualification: StringIDRow = app.db.get_qualification(db_qualification_id)

        return {
            "id": db_qualification["qualification_id"],
            "name": db_qualification["qualification_name"],
        }
