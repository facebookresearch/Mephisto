#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask.views import MethodView

from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task import Task


class TasksView(MethodView):
    def get(self) -> dict:
        """ Get all available tasks (to select one for review) """

        db_tasks: List[Task] = app.db.find_tasks()
        app.logger.debug(f"Found tasks in DB: {db_tasks}")

        tasks = []
        for t in db_tasks:
            units = app.data_browser.get_units_for_task_name(t.task_name)

            app.logger.debug(f"All units: {units}")

            waiting_for_review_units = [
                u for u in units if u.get_status() == AssignmentState.COMPLETED
            ]

            app.logger.debug(f"Waiting for review units: {waiting_for_review_units}")

            unit_count = len(waiting_for_review_units)
            is_reviewed = unit_count == 0

            tasks.append(
                {
                    "id": t.db_id,
                    "name": t.task_name,
                    "is_reviewed": is_reviewed,
                    "unit_count": unit_count,
                    "created_at": t.creation_date.isoformat(),
                }
            )

        app.logger.debug(f"Tasks: {tasks}")

        return {
            'tasks': tasks,
        }
