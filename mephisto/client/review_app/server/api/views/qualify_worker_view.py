#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.worker import Worker


def _create_unit_review(
    datastore,
    qualification_id: int,
    worker_id: int,
    value: Optional[int] = None,
    revoke: bool = False,
) -> None:
    """
    Create unit review in the datastore by the given Qualification ID, Worker ID and Value
    """

    with datastore.table_access_condition:
        conn = datastore._get_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO unit_review (
                unit_id,
                worker_id,
                task_id,
                updated_qualification_id,
                updated_qualification_value,
                revoked_qualification_id
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                None,
                worker_id,
                None,
                qualification_id if not revoke else None,
                value,
                qualification_id if revoke else None,
            ),
        )
        conn.commit()


def _create_grant_unit_review(
    datastore, qualification_id: int, worker_id: int, value: Optional[int] = None,
):
    _create_unit_review(datastore, qualification_id, worker_id, value)


def _create_revoke_unit_review(
    datastore, qualification_id: int, worker_id: int, value: Optional[int] = None,
):
    _create_unit_review(datastore, qualification_id, worker_id, value, revoke=True)


class QualifyWorkerView(MethodView):
    @staticmethod
    def _grant_worker_qualification(qualification: StringIDRow, worker: Worker, value: int):
        worker.grant_qualification(qualification["qualification_name"], value)

        # TODO [Review APP]: `unit_id` and `task_id` are mandatory fields, need to find them here
        # _create_grant_unit_review(
        #     app.datastore, qualification["qualification_id"], int(worker.db_id), value,
        # )

    @staticmethod
    def _revoke_worker_qualification(qualification: StringIDRow, worker: Worker):
        worker.revoke_qualification(qualification["qualification_name"])

        # TODO [Review APP]: `unit_id` and `task_id` are mandatory fields, need to find them here
        # _create_revoke_unit_review(
        #     app.datastore, qualification["qualification_id"], int(worker.db_id),
        # )

    def post(self, qualification_id: int, worker_id: int, action: str) -> dict:
        """ Grant/Revoke qualification to a worker """

        data: dict = request.json
        value = data and data.get("value")

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        worker: Worker = Worker.get(app.db, str(worker_id))

        if action == "grant":
            self._grant_worker_qualification(db_qualification, worker, value or 1)
            return {}
        elif action == "revoke":
            self._revoke_worker_qualification(db_qualification, worker)
            return {}
        else:
            raise NotFound()
