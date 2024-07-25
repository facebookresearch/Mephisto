#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask.views import MethodView

from mephisto.data_model.task import Task
from mephisto.data_model.unit import Unit


class TaskWorkerOpinionsView(MethodView):
    def get(self, task_id: str = None) -> dict:
        """Returns all Worker Opinions related to a Task"""

        task: Task = Task.get(db=app.db, db_id=task_id)
        app.logger.debug(f"Found Task in DB: {task}")

        units: List[Unit] = task.db.find_units(task_id=task_id)
        app.logger.debug(f"Found Units in DB: {units}")

        worker_opinions = []
        for unit in units:
            try:
                unit_data = app.data_browser.get_data_from_unit(unit)
            except AssertionError:
                # In case if this is Expired Unit. It raises and axceptions
                unit_data = {}

            metadata = unit_data.get("metadata", {})

            if worker_opinion := metadata.get("worker_opinion"):
                agent = unit.get_assigned_agent()
                unit_data_folder = agent.get_data_dir() if agent else None

                worker_opinions.append(
                    {
                        "worker_id": unit.worker_id,
                        "unit_data_folder": unit_data_folder,
                        "unit_id": unit.db_id,
                        "data": {
                            "attachments": worker_opinion["attachments"],
                            "questions": worker_opinion["questions"],
                        },
                    }
                )

        return {
            "task_name": task.task_name,
            "worker_opinions": worker_opinions,
        }
