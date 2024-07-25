#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.utils import http_status
from mephisto.utils.testing import get_test_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestUnitHtmlView(BaseTestApiViewCase):
    def test_html_success(self, *args, **kwargs):
        unit_id = get_test_unit(self.db)

        with self.app_context:
            url = url_for("unit_review_html", unit_id=unit_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue(
            f'<script src="/units/{unit_id}/bundle.js"></script>' in response.data.decode()
        )


if __name__ == "__main__":
    unittest.main()
