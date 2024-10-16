#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.utils import http_status
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestQualificationDetailsView(BaseTestApiViewCase):
    def test_qualification_details_success(self, *args, **kwargs):
        granted_value = 999

        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id_1 = get_test_worker(self.db, "first")
        _, worker_id_2 = get_test_worker(self.db, "second")

        # Qualifications
        qualification_id = get_test_qualification(self.db)
        grant_test_qualification(self.db, qualification_id, worker_id_1, granted_value)
        grant_test_qualification(self.db, qualification_id, worker_id_2, granted_value)

        with self.app_context:
            url = url_for("qualification_details", qualification_id=qualification_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result["granted_qualifications_count"], 2)

    def test_qualification_details_success_no_results(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Qualifications
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification_details", qualification_id=qualification_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result["granted_qualifications_count"], 0)

    def test_qualification_details_no_qualification_error(self, *args, **kwargs):
        incorrect_qualification_id = 8888

        # Task Run
        get_test_task_run(self.db)

        with self.app_context:
            url = url_for("qualification_details", qualification_id=incorrect_qualification_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
