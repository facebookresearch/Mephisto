#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from pathlib import Path
from typing import List

from flask import current_app as app
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from .tasks_view import find_completed_units


def get_results_dir() -> str:
    project_root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
    results_dir = os.path.join(project_root_dir, "tmp", "results")
    return results_dir


def get_result_file_path(results_dir: str, task_id: str, n_units: int) -> str:
    return os.path.join(results_dir, f"task_{task_id}__{n_units}_units__results.json")


class TaskExportResultsView(MethodView):
    def get(self, task_id: str = None) -> dict:
        """Assemble results for all Units related to the Task into a single file"""

        db_task: StringIDRow = app.db.get_task(task_id)
        app.logger.debug(f"Found Task in DB: {db_task}")

        db_units: List[StringIDRow] = find_completed_units(int(task_id))
        is_reviewed = all([u["status"] != AssignmentState.COMPLETED for u in db_units])

        if not is_reviewed:
            raise BadRequest(
                "This task has not been fully reviewed yet. "
                "Please review it completely before requesting the results."
            )

        task_units_data = {}
        for db_unit in db_units:
            unit_id = db_unit["unit_id"]
            unit: Unit = Unit.get(app.db, unit_id)

            try:
                unit_data = app.data_browser.get_data_from_unit(unit)
            except AssertionError:
                # In case if unit does not have agent somehow
                unit_data = {}

            task_units_data[unit_id] = unit_data

        # Save file with results, so it can be copied later from the repo if needed
        results_dir = get_results_dir()
        results_file_path = get_result_file_path(results_dir, task_id, len(db_units))

        # File is cached only if we did not add any new reviewed units to the task
        if not os.path.exists(results_file_path):
            os.makedirs(results_dir, exist_ok=True)
            with open(results_file_path, "w") as f:
                f.write(json.dumps(task_units_data, indent=4))

        return {"file_created": True}
