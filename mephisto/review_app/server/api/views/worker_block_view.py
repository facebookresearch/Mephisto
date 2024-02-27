#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.database import EntryDoesNotExistException
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker


def _update_blocked_worker_in_unit_review(
    db,
    unit_id: int,
    worker_id: int,
    block: bool = False,
) -> None:
    """Update unit review in the db with blocking Worker value"""

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
                blocked_worker = ?
            WHERE id = ?;
            """,
            (
                block,
                latest_unit_review_id,
            ),
        )
        conn.commit()


class WorkerBlockView(MethodView):
    def post(self, worker_id: int) -> dict:
        """Permanently block a worker"""

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        review_note = data and data.get("review_note")

        # Validate params
        if not review_note:
            raise BadRequest("`review_note` parameter must be specified.")

        # Block worker
        worker = Worker.get(app.db, str(worker_id))

        worker.block_worker(review_note)

        if unit_ids:
            for unit_id in unit_ids:
                unit: Unit = Unit.get(app.db, str(unit_id))
                _update_blocked_worker_in_unit_review(app.db, int(unit.db_id), worker_id, True)

        return {}
