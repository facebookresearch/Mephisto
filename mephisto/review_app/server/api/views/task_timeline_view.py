#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import requests
from flask import current_app as app
from flask.views import MethodView

from mephisto.data_model.task import Task
from mephisto.utils import metrics


class TaskTimelineView(MethodView):
    def get(self, task_id: str = None) -> dict:
        """Check if Grafana server is available and redirect or return error"""

        task: Task = Task.get(db=app.db, db_id=task_id)
        app.logger.debug(f"Found Task in DB: {task}")

        try:
            grafana_url = metrics.get_grafana_url()
            r = requests.get(grafana_url)
            grafana_server_is_ok = r.ok
        except requests.exceptions.ConnectionError as e:
            grafana_server_is_ok = False

        data = {
            "dashboard_url": None,
            "server_is_available": False,
            "task_name": task.task_name,
        }

        if grafana_server_is_ok:
            data.update(
                {
                    "dashboard_url": "http://" + metrics.get_default_dashboard_url(),
                    "server_is_available": True,
                }
            )

        return data
