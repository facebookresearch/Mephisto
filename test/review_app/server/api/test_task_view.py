#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.utils.testing import get_test_task
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTaskView(BaseTestApiViewCase):
    def test_no_task_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("task", task_id=999)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(result, {"error" : "Not found"})

    def test_one_task_success(self, *args, **kwargs):
        task_name, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("task", task_id=task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["id"], task_id)
        self.assertEqual(result["name"], task_name)
        self.assertTrue("created_at" in result)
        self.assertTrue("type" in result)


if __name__ == "__main__":
    unittest.main()
