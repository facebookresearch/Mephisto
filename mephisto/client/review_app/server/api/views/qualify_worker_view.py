#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from mephisto.abstractions.database import EntryDoesNotExistException
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker


def _update_quailification_in_unit_review(
    db,
    unit_id: int,
    qualification_id: int,
    worker_id: int,
    value: Optional[int] = None,
    revoke: bool = False,
) -> None:
    """
    Update unit review in the db with the given Qualification ID, Worker ID and Value
    """

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()

        c.execute(
            """
            SELECT * FROM unit_review
            WHERE (unit_id = ?) AND (worker_id = ?)
            ORDER BY created_at ASC;
            """,
            (unit_id, worker_id),
        )
        results = c.fetchall()
        if not results:
            raise EntryDoesNotExistException(
                f"`unit_review` was not created for this `unit_id={unit_id}`"
            )

        latest_unit_review_id = results[-1]["id"]

        c.execute(
            """
            UPDATE unit_review
            SET
                updated_qualification_id = ?,
                updated_qualification_value = ?,
                revoked_qualification_id = ?
            WHERE id = ?;
            """,
            (
                qualification_id if not revoke else None,
                value,
                qualification_id if revoke else None,
                latest_unit_review_id,
            ),
        )
        conn.commit()


def _write_grant_unit_review(
    db, unit_id: int, qualification_id: int, worker_id: int, value: Optional[int] = None,
):
    _update_quailification_in_unit_review(db, unit_id, qualification_id, worker_id, value)


def _write_revoke_unit_review(
    db, unit_id: int, qualification_id: int, worker_id: int, value: Optional[int] = None,
):
    _update_quailification_in_unit_review(db, unit_id, qualification_id, worker_id, value, revoke=True)


class QualifyWorkerView(MethodView):
    @staticmethod
    def _grant_worker_qualification(
        qualification: StringIDRow, unit: Unit, worker: Worker, value: int,
    ):
        worker.grant_qualification(qualification["qualification_name"], value)

        _write_grant_unit_review(
            app.db,
            int(unit.db_id),
            qualification["qualification_id"],
            int(worker.db_id),
            value,
        )

    @staticmethod
    def _revoke_worker_qualification(qualification: StringIDRow, unit: Unit, worker: Worker):
        worker.revoke_qualification(qualification["qualification_name"])

        _write_revoke_unit_review(
            app.db,
            int(unit.db_id),
            qualification["qualification_id"],
            int(worker.db_id),
        )

    def post(self, qualification_id: int, worker_id: int, action: str) -> dict:
        """ Grant/Revoke qualification to a worker """

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        value = data and data.get("value")

        if not unit_ids:
            raise BadRequest("Field \"unit_ids\" is required.")

        if not qualification_id:
            # Front-end could send us an enpty value - don't raise exception, just ignore
            return {}

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        if not db_qualification:
            raise NotFound()

        for unit_id in unit_ids:
            unit: Unit = Unit.get(app.db, str(unit_id))
            worker: Worker = Worker.get(app.db, str(worker_id))

            try:
                if action == "grant":
                    self._grant_worker_qualification(db_qualification, unit, worker, value or 1)
                elif action == "revoke":
                    self._revoke_worker_qualification(db_qualification, unit, worker)
            except Exception as e:
                raise BadRequest(f"Could not {action} qualification. Reason: {e}")

        return {}
