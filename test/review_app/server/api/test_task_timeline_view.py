#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for
from requests import HTTPError
from requests import Response

from mephisto.utils import http_status
from mephisto.utils.metrics import GRAFANA_PORT
from mephisto.utils.testing import get_test_task
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTaskTimelineView(BaseTestApiViewCase):
    def test_task_timeline_not_found_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("task_timeline", task_id=999)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_404_NOT_FOUND)

    @patch("requests.get")
    def test_task_timeline_server_down(self, mock_requests_get, *args, **kwargs):
        def mock_raise_for_status(*args, **kwargs):
            raise HTTPError("Test")

        mock_response = Response()
        mock_response.raise_for_status = mock_raise_for_status
        mock_response.status_code = http_status.HTTP_400_BAD_REQUEST
        mock_response._content = ""

        mock_requests_get.return_value = mock_response

        _, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("task_timeline", task_id=task_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            response.json,
            {"dashboard_url": None, "server_is_available": False, "task_name": "test_task"},
        )

    @patch("mephisto.utils.metrics.get_default_dashboard_url")
    @patch("requests.get")
    def test_task_timeline_success(
        self,
        mock_requests_get,
        mock_get_default_dashboard_url,
        *args,
        **kwargs,
    ):
        expected_dashboard_url = f"localhost:{GRAFANA_PORT}/test"

        def mock_raise_for_status(*args, **kwargs):
            return

        mock_response = Response()
        mock_response.raise_for_status = mock_raise_for_status
        mock_response.status_code = http_status.HTTP_200_OK
        mock_response._content = ""

        mock_requests_get.return_value = mock_response
        mock_get_default_dashboard_url.return_value = expected_dashboard_url

        _, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("task_timeline", task_id=task_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            response.json,
            {
                "dashboard_url": f"http://{expected_dashboard_url}",
                "server_is_available": True,
                "task_name": "test_task",
            },
        )


if __name__ == "__main__":
    unittest.main()
