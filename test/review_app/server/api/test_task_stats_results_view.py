#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for
from omegaconf import OmegaConf

from mephisto.utils import http_status
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRunArgs
from mephisto.data_model.unit import Unit
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from mephisto.utils.testing import MOCK_ARCHITECT_ARGS
from mephisto.utils.testing import MOCK_BLUEPRINT_ARGS
from mephisto.utils.testing import MOCK_PROVIDER_ARGS
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase

MOCK_TASK_ARGS = TaskRunArgs(
    task_title="title",
    task_description="This is a description",
    task_reward=0.3,
    task_tags="1,2,3,form-composer",
)

MOCK_CONFIG = MephistoConfig(
    provider=MOCK_PROVIDER_ARGS,
    blueprint=MOCK_BLUEPRINT_ARGS,
    architect=MOCK_ARCHITECT_ARGS,
    task=MOCK_TASK_ARGS,
)


class TestTaskStatsResultsView(BaseTestApiViewCase):
    def test_task_stats_result_not_found_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("task_stats_results", task_id=999)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_404_NOT_FOUND)

    def test_task_stats_result_not_reviews_error(self, *args, **kwargs):
        _, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("task_stats_results", task_id=task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result["error"],
            "This task has never been launched before.",
        )

    def test_task_stats_result_not_form_composer(self, *args, **kwargs):
        _, worker_id = get_test_worker(self.db)
        get_test_task_run(self.db)
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)

        with self.app_context:
            url = url_for("task_stats_results", task_id=unit.task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result["error"],
            "Statistics for tasks of this type are not yet supported.",
        )

    @patch("mephisto.generators.form_composer.stats.collect_task_stats")
    def test_task_stats_result_success(self, mock_collect_task_stats, *args, **kwargs):
        _, worker_id = get_test_worker(self.db)
        init_params = OmegaConf.to_yaml(OmegaConf.structured(MOCK_CONFIG))
        get_test_task_run(self.db, init_params=init_params)
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        task: Task = Task.get(self.db, unit.task_id)

        expected_value = {
            "stats": {},
            "task_id": task.db_id,
            "task_name": task.task_name,
            "workers_count": 1,
        }

        mock_collect_task_stats.return_value = expected_value

        with self.app_context:
            url = url_for("task_stats_results", task_id=unit.task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result, expected_value)


if __name__ == "__main__":
    unittest.main()
