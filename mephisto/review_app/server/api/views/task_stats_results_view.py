#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask.views import MethodView
from omegaconf import DictConfig
from werkzeug.exceptions import BadRequest

from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    FORM_COMPOSER_TASK_TAG,
)


class TaskStatsResultsView(MethodView):
    def get(self, task_id: str = None) -> dict:
        """Assemble stats with results for Task"""

        task: Task = Task.get(db=app.db, db_id=task_id)
        app.logger.debug(f"Found Task in DB: {task}")

        task_runs: List[TaskRun] = task.get_runs()

        if not task_runs:
            raise BadRequest("This task has never been launched before.")

        last_task_run: TaskRun = task_runs[-1]
        last_task_run_config: DictConfig = last_task_run.get_task_args()

        collect_task_stats_func = None
        if FORM_COMPOSER_TASK_TAG in last_task_run_config.task_tags:
            from mephisto.generators.form_composer.stats import collect_task_stats

            collect_task_stats_func = collect_task_stats
        else:
            raise BadRequest("Statistics for tasks of this type are not yet supported.")

        stats = collect_task_stats_func(task)

        return stats
