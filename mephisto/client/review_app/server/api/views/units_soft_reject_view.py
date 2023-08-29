#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.client.review_app.server import db_queries
from mephisto.data_model.unit import Unit


class UnitsSoftRejectView(MethodView):
    def post(self) -> dict:
        """ Soft-reject worker's result """

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        feedback = data and data.get("feedback")  # Optional

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Get units
        db_units: List[Unit] = app.db.find_units()

        # Soft Reject units
        for unit in db_units:
            if unit_ids and int(unit.db_id) not in unit_ids:
                continue

            agent = unit.get_assigned_agent()
            if not agent:
                raise BadRequest(f"Cound not reject softly Unit \"{unit.db_id}\".")

            agent.soft_reject_work()

            db_queries.create_unit_review(
                datastore=app.db,
                unit_id=int(unit.db_id),
                task_id=int(unit.task_id),
                worker_id=int(unit.worker_id),
                status=unit.db_status,
                feedback=feedback,
            )

        return {}
