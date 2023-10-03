#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.data_model.unit import Unit


class UnitsApproveView(MethodView):
    def post(self) -> dict:
        """Approve worker's input"""

        data: dict = request.json
        unit_ids: Optional[str] = data and data.get("unit_ids")
        feedback = data and data.get("feedback")  # Optional
        tips = data and data.get("tips")  # Optional

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Approve units
        for unit_id in unit_ids:
            unit: Unit = Unit.get(app.db, str(unit_id))

            agent = unit.get_assigned_agent()
            if not agent:
                raise BadRequest(f'Cound not approve Unit "{unit_id}".')

            try:
                agent.approve_work(feedback=feedback, tips=tips)
            except Exception as e:
                raise BadRequest(f'Could not approve unit "{unit_id}". Reason: {e}')

            unit.get_status()  # Update status immediately for other EPs as this method affects DB

        return {}
