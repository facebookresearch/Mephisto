#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import StringIDRow


class TaskView(MethodView):
    def get(self, task_id: str = None) -> dict:
        """Get all available tasks (to select one for review)"""

        db_task: StringIDRow = app.db.get_task(task_id)
        app.logger.debug(f"Found Task in DB: {db_task}")

        return {
            "created_at": db_task["creation_date"],
            "id": db_task["task_id"],
            "name": db_task["task_name"],
            "type": db_task["task_type"],
        }
