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

from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit
from mephisto.generators.form_composer.config_validation.task_data_config import (
    prepare_task_config_for_review_app,
)


class UnitsDetailsView(MethodView):
    def get(self) -> dict:
        """Get full input for specified workers results (`unit_ids` is mandatory)"""

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

            task_run: TaskRun = unit.get_task_run()
            has_task_source_review = bool(task_run.args.get("blueprint").get("task_source_review"))

            inputs = unit_data.get("data", {}).get("inputs", {})
            outputs = unit_data.get("data", {}).get("outputs", {})

            # In case if there is outdated code that returns `final_submission`
            # under `inputs` and `outputs` keys, we should use the value in side `final_submission`
            if "final_submission" in inputs:
                inputs = inputs["final_submission"]
            if "final_submission" in outputs:
                outputs = outputs["final_submission"]

            # Perform any dynamic action on task config for current unit
            # to make it the same as it looked like for a worker
            prepared_inputs = inputs
            if "form" in inputs:
                prepared_inputs = prepare_task_config_for_review_app(inputs)

            agent = unit.get_assigned_agent()
            unit_data_folder = agent.get_data_dir() if agent else None

            units.append(
                {
                    "has_task_source_review": has_task_source_review,
                    "id": int(unit.db_id),
                    "inputs": inputs,  # instructions for worker
                    "outputs": outputs,  # response from worker
                    "prepared_inputs": prepared_inputs,  # prepared instructions from worker
                    "unit_data_folder": unit_data_folder,  # path to data dir in file system
                }
            )

        return {
            "units": units,
        }
