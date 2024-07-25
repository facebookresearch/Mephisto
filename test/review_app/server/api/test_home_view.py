#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.utils import http_status
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestHomeView(BaseTestApiViewCase):
    def test_redirect_success(self, *args, **kwargs):
        with self.app_context:
            url = url_for("client-home")
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_302_FOUND)

    @patch("os.path.join")
    def test_home_success(self, mock_join, *args, **kwargs):
        ui_html_file_data = "Test HTML"

        ui_html_file_path = f"{self.data_dir}/index.html"
        f = open(ui_html_file_path, "w")
        f.write(ui_html_file_data)
        f.close()

        mock_join.return_value = ui_html_file_path

        with self.app_context:
            url = url_for("client-tasks", path="tasks")
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(response.data, ui_html_file_data.encode())
        self.assertEqual(response.mimetype, "text/html")

    @patch("os.path.join")
    def test_home__no_html_file_error(self, mock_join, *args, **kwargs):
        mock_join.return_value = "/nonexistent/path"

        with self.app_context:
            url = url_for("client-tasks", path="tasks")
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            response.json["error"],
            "UI interface isn't ready to use. Build it or use separate address for dev UI server.",
        )


if __name__ == "__main__":
    unittest.main()
