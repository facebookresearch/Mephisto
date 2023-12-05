#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker


def _write_grant_unit_review(
    db,
    unit_id: int,
    qualification_id: int,
    worker_id: int,
    value: Optional[int] = None,
):
    db.update_unit_review(unit_id, qualification_id, worker_id, value, revoke=False)


def _write_revoke_unit_review(
    db,
    unit_id: int,
    qualification_id: int,
    worker_id: int,
    value: Optional[int] = None,
):
    db.update_unit_review(unit_id, qualification_id, worker_id, value, revoke=True)


class QualifyWorkerView(MethodView):
    @staticmethod
    def _grant_worker_qualification(
        qualification: StringIDRow,
        unit: Unit,
        worker: Worker,
        value: int,
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
        """Grant/Revoke qualification to a worker"""

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        value = data and data.get("value")

        if not unit_ids:
            raise BadRequest('Field "unit_ids" is required.')

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)

        if not db_qualification:
            app.logger.debug(f"Could not found qualification with ID={qualification_id}")
            # Do not raise any error, just ignore it
            return {}

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
