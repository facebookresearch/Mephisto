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

from mephisto.data_model.unit import Unit


class UnitsDetailsView(MethodView):
    def get(self) -> dict:
        """ Get full input for specified workers results (`unit_ids` is mandatory) """

        unit_ids: Optional[str] = request.args.get("unit_ids")

        app.logger.debug(f"Params: {unit_ids=}")

        # Parse `unit_ids`
        if unit_ids:
            try:
                unit_ids: List[int] = [int(i.strip()) for i in unit_ids.split(",")]
            except ValueError:
                raise BadRequest("`unit_ids` must be a comma-separated list of integers.")

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Get units
        db_units: List[Unit] = app.db.find_units()

        # Prepare response
        units = []
        for unit in db_units:
            if unit_ids and int(unit.db_id) not in unit_ids:
                continue

            try:
                unit_data = app.data_browser.get_data_from_unit(unit)
            except AssertionError:
                # In case if this is Expired Unit. It raises and axceptions
                unit_data = {}

            units.append(
                {
                    "id": int(unit.db_id),
                    "inputs": unit_data.get("data", {}).get("inputs"),  # instructions for worker
                    "outputs": unit_data.get("data", {}).get("outputs"),  # resposne from worker
                }
            )

        return {
            "units": units,
        }
