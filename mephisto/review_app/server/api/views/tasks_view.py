#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from dateutil.parser import parse
from flask import current_app as app
from flask.views import MethodView
from omegaconf import DictConfig

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.review_app.server.db_queries import find_units


def _find_tasks(db, debug: bool = False) -> List[StringIDRow]:
    with db.table_access_condition:
        conn = db.get_connection()

        c = conn.cursor()
        c.execute(
            """
            SELECT * from tasks
            """
        )
        rows = c.fetchall()

        return rows


def find_all_units(task_id: int) -> List[StringIDRow]:
    return find_units(app.db, task_id, debug=app.debug)


def find_completed_units(task_id: int) -> List[StringIDRow]:
    return find_units(
        app.db,
        task_id,
        statuses=AssignmentState.completed(),
        debug=app.debug,
    )


def check_if_task_reviewed(task_id: int) -> bool:
    # As we can review only completed Units,
    # Task can be considered reviewed, if we count only these Units
    db_units: List[StringIDRow] = find_completed_units(task_id)
    unit_count = len(db_units)
    is_reviewed = unit_count > 0 and all(
        [u["status"] != AssignmentState.COMPLETED for u in db_units]
    )
    return is_reviewed


def _check_task_has_stats(task_id: str) -> bool:
    task: Task = Task.get(db=app.db, db_id=task_id)
    task_runs: List[TaskRun] = task.get_runs()

    if not task_runs:
        return False

    last_task_run: TaskRun = task_runs[-1]
    last_task_run_config: DictConfig = last_task_run.get_task_args()

    if "form-composer" in last_task_run_config.task_tags:
        from mephisto.generators.form_composer.stats import check_task_has_fields_for_stats

        return check_task_has_fields_for_stats(task)

    return False


class TasksView(MethodView):
    def get(self) -> dict:
        """Get all available tasks (to select one for review)"""

        db_tasks: List[StringIDRow] = _find_tasks(app.db, debug=app.debug)
        app.logger.debug(f"Found tasks in DB: {[t['task_id'] for t in db_tasks]}")

        tasks = []
        for t in db_tasks:
            db_units: List[StringIDRow] = find_all_units(int(t["task_id"]))
            app.logger.debug(f"All found units: {[u['unit_id'] for u in db_units]}")

            unit_all_count = len(db_units)
            unit_completed_count = len(find_completed_units(int(t["task_id"])))
            unit_finished_count = len(
                [u["status"] in AssignmentState.final_agent() for u in db_units]
            )
            is_reviewed = check_if_task_reviewed(task_id=t["task_id"])
            has_stats = _check_task_has_stats(task_id=t["task_id"])

            tasks.append(
                {
                    "created_at": parse(t["creation_date"]).isoformat(),
                    "has_stats": has_stats,
                    "id": t["task_id"],
                    "is_reviewed": is_reviewed,
                    "name": t["task_name"],
                    # To show how many Units Task has
                    "unit_all_count": unit_all_count,
                    # To download results file (we use it in URL)
                    "unit_completed_count": unit_completed_count,
                    # To show how many Units were finished among all
                    "unit_finished_count": unit_finished_count,
                }
            )

        app.logger.debug(f"Tasks: {tasks}")

        return {
            "tasks": tasks,
        }
