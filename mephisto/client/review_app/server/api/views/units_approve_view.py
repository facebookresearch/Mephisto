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

from mephisto.abstractions.blueprint import AgentState
from mephisto.client.review_app.server import db_queries
from mephisto.data_model.unit import Unit


class UnitsApproveView(MethodView):
    def post(self) -> dict:
        """ Approve worker's input """

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        feedback = data and data.get("feedback")  # Optional
        tips = data and data.get("tips")  # Optional

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Get units
        db_units: List[Unit] = app.db.find_units()

        # Approve units
        for unit in db_units:
            if unit_ids and str(unit.db_id) not in unit_ids:
                continue

            agent = unit.get_assigned_agent()
            if not agent:
                raise BadRequest(f"Cound not approve Unit \"{unit.db_id}\".")

            agent.approve_work()

            db_queries.create_unit_review(
                db=app.db,
                unit_id=int(unit.db_id),
                task_id=int(unit.task_id),
                worker_id=int(unit.worker_id),
                status=AgentState.STATUS_APPROVED,
                feedback=feedback,
                tips=tips,
            )

        return {}
