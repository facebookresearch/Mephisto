#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.utils.testing import get_test_task
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTasksView(BaseTestApiViewCase):
    def test_no_tasks_success(self, *args, **kwargs):
        with self.app_context:
            url = url_for("tasks")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["tasks"], [])

    def test_one_task_success(self, *args, **kwargs):
        task_name, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("tasks")
            response = self.client.get(url)
            result = response.json

        first_response_task = result["tasks"][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(first_response_task["id"], task_id)
        self.assertEqual(first_response_task["name"], task_name)
        self.assertTrue("created_at" in first_response_task)
        self.assertTrue("is_reviewed" in first_response_task)
        self.assertTrue("unit_count" in first_response_task)
        self.assertTrue("has_stats" in first_response_task)


if __name__ == "__main__":
    unittest.main()
