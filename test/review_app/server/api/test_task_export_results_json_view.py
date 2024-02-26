#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.review_app.server.api.views.task_export_results_view import get_result_file_path
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTaskExportResultsJsonView(BaseTestApiViewCase):
    @patch("mephisto.review_app.server.api.views.task_export_results_json_view.get_results_dir")
    def test_task_export_result_json_success(self, mock_get_results_dir, *args, **kwargs):
        mock_get_results_dir.return_value = self.data_dir
        task_id = 1
        n_units = 1

        results_file_data = "Test JS"

        results_file_path = get_result_file_path(self.data_dir, task_id, n_units)
        f = open(results_file_path, "w")
        f.write(results_file_data)
        f.close()

        with self.app_context:
            url = url_for("task_export_results_json", task_id=task_id, n_units=n_units)
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, results_file_data.encode())
        self.assertEqual(response.mimetype, "application/json")

    def test_task_export_result_json_not_found_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("task_export_results_json", task_id=999, n_units=1)
            response1 = self.client.get(url)

        with self.app_context:
            url = url_for("task_export_results_json", task_id=1, n_units=99)
            response2 = self.client.get(url)

        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
