#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.data_model.unit import Unit


class UnitsRejectView(MethodView):
    def post(self) -> dict:
        """Reject worker's result"""

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        review_note: Optional[str] = data.get("review_note") if data else None

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Reject units
        for unit_id in unit_ids:
            unit: Unit = Unit.get(app.db, str(unit_id))

            agent = unit.get_assigned_agent()
            if not agent:
                raise BadRequest(f'Cound not reject Unit "{unit_id}".')

            try:
                agent.reject_work(review_note=review_note)
            except Exception as e:
                raise BadRequest(f'Could not reject unit "{unit_id}". Reason: {e}')

            unit.get_status()  # Update status immediately for other EPs as this method affects DB

        return {}
