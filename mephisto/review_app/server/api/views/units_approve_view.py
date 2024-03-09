#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional
from typing import Union

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker


class UnitsApproveView(MethodView):
    def post(self) -> dict:
        """Approve worker's input"""

        data: dict = request.json or {}
        unit_ids: Optional[str] = data.get("unit_ids")
        review_note: Optional[str] = data.get("review_note")
        bonus: Optional[Union[int, float]] = data.get("bonus")
        send_to_worker: Optional[bool] = data.get("send_to_worker", False)

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Approve units
        for unit_id in unit_ids:
            unit: Unit = Unit.get(app.db, str(unit_id))
            worker: Worker = Worker.get(app.db, str(unit.worker_id))

            agent = unit.get_assigned_agent()
            if not agent:
                raise BadRequest(f'Cound not approve Unit "{unit_id}".')

            try:
                agent.approve_work(review_note=review_note, bonus=bonus)
            except Exception as e:
                raise BadRequest(f'Could not approve unit "{unit_id}". Reason: {e}')

            unit.get_status()  # Update status immediately for other EPs as this method affects DB

            if bonus:
                # NOTE: We do not break response, we just log error messages with details

                # Validate bonus value
                try:
                    bonus = float(bonus)
                except Exception:
                    app.logger.exception(f"Could not pay bonus. Passed value is invalid: {bonus}")
                    return {}

                # Pay bonus
                try:
                    bonus_successfully_paid, message = worker.bonus_worker(bonus, review_note, unit)
                    if not bonus_successfully_paid:
                        app.logger.error(f"Could not pay bonus. Reason: {message}")
                except Exception:
                    app.logger.exception("Could not pay bonus. Unexpected error")
                    return {}

            if review_note and send_to_worker:
                worker.send_feedback_message(text=review_note, unit=unit)

        return {}
