#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker


class UpdateGrantedQualificationStatus:
    GRANT = "grant"
    REVOKE = "revoke"


def _find_units_ids(
    db: LocalMephistoDB,
    worker_id: int,
    qualification_id: int,
) -> List[str]:
    """Return the units for granted qualification"""

    with db.table_access_condition:
        conn = db.get_connection()
        c = conn.cursor()

        params = [
            nonesafe_int(qualification_id),
            nonesafe_int(worker_id),
        ]

        c.execute(
            f"""
            SELECT
                wr.unit_id as unit_id
            FROM worker_review AS wr
            WHERE (
                wr.worker_id = ?2 AND
                (wr.updated_qualification_id = ?1 OR wr.revoked_qualification_id = ?1)
            );
            """,
            params,
        )
        rows = c.fetchall()
        unit_ids = list(set([u["unit_id"] for u in rows]))
        return unit_ids


class QualifyWorkerView(MethodView):
    @staticmethod
    def grant_worker_qualification_with_unit(
        qualification: StringIDRow,
        unit: Unit,
        worker: Worker,
        value: int,
    ):
        worker.grant_qualification(qualification["qualification_name"], value)

        app.db.update_worker_review(
            unit_id=unit.db_id,
            qualification_id=qualification["qualification_id"],
            worker_id=worker.db_id,
            value=value,
            revoke=False,
        )

    @staticmethod
    def _revoke_worker_qualification_with_unit(
        qualification: StringIDRow,
        unit: Unit,
        worker: Worker,
        value: Optional[int] = None,
    ):
        worker.revoke_qualification(qualification["qualification_name"])

        app.db.update_worker_review(
            unit_id=unit.db_id,
            qualification_id=qualification["qualification_id"],
            worker_id=worker.db_id,
            value=value,
            revoke=True,
        )

    @staticmethod
    def _update_worker_qualification(
        qualification: StringIDRow,
        worker: Worker,
        value: int,
        explanation: Optional[str] = None,
    ):
        worker.grant_qualification(qualification["qualification_name"], value, skip_crowd=True)

        app.db.new_worker_review(
            worker_id=worker.db_id,
            qualification_id=qualification["qualification_id"],
            value=value,
            review_note=explanation,
            status=UpdateGrantedQualificationStatus.GRANT,
            revoke=False,
        )

    @staticmethod
    def _revoke_worker_qualification(
        qualification: StringIDRow,
        worker: Worker,
        explanation: Optional[str] = None,
    ):
        worker.revoke_qualification(qualification["qualification_name"], skip_crowd=True)

        app.db.new_worker_review(
            worker_id=worker.db_id,
            qualification_id=qualification["qualification_id"],
            review_note=explanation,
            status=UpdateGrantedQualificationStatus.REVOKE,
            revoke=True,
        )

    def post(self, qualification_id: int, worker_id: int, action: str) -> dict:
        """Grant/Revoke qualification to a worker with unit"""

        data: dict = request.json or {}
        unit_ids: Optional[List[str]] = data.get("unit_ids")
        value: Optional[int] = data.get("value")

        if not unit_ids:
            raise BadRequest('Field "unit_ids" is required.')

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)

        if not db_qualification:
            app.logger.debug(f"Could not found qualification with ID={qualification_id}")
            # Do not raise any error, just ignore it
            return {}

        worker: Worker = Worker.get(app.db, str(worker_id))

        for unit_id in unit_ids:
            unit: Unit = Unit.get(app.db, str(unit_id))

            try:
                if action == "grant":
                    self.grant_worker_qualification_with_unit(
                        qualification=db_qualification,
                        unit=unit,
                        worker=worker,
                        value=value or 1,
                    )
                elif action == "revoke":
                    self._revoke_worker_qualification_with_unit(
                        qualification=db_qualification,
                        unit=unit,
                        worker=worker,
                        value=value,
                    )
            except Exception as e:
                raise BadRequest(f"Could not {action} qualification. Reason: {e}")

        return {}

    def patch(self, qualification_id: int, worker_id: int, action: str) -> dict:
        """Update value of existing granted qualification or revoke qualification from a worker"""

        # TODO: Note that it will not affect `worker_review` table
        #  as we have required field `unit_id`,
        #  but in this case we update granted qualification directly

        data: dict = request.json or {}
        value: Optional[int] = data.get("value")
        explanation: Optional[str] = data.get("explanation")

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)

        if not db_qualification:
            app.logger.debug(f"Could not found qualification with ID={qualification_id}")
            # Do not raise any error, just ignore it
            return {}

        worker: Worker = Worker.get(app.db, str(worker_id))

        if action == "grant":
            if not value:
                raise BadRequest('Field "value" is required.')

            self._update_worker_qualification(
                qualification=db_qualification,
                worker=worker,
                value=value,
                explanation=explanation,
            )
        elif action == "revoke":
            self._revoke_worker_qualification(
                qualification=db_qualification,
                worker=worker,
                explanation=explanation,
            )

        return {}
