#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.utils import http_status
from mephisto.utils.db import EntryDoesNotExistException
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_task_run
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestQualificationDetailsView(BaseTestApiViewCase):
    def test_get_qualification_success(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Qualifications
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification", qualification_id=qualification_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result["id"], str(qualification_id))
        self.assertIn("creation_date", result)
        self.assertIn("description", result)
        self.assertIn("id", result)
        self.assertIn("name", result)

    def test_get_qualification_no_qualification_error(self, *args, **kwargs):
        incorrect_qualification_id = 8888

        # Task Run
        get_test_task_run(self.db)

        # Qualifications
        get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification", qualification_id=incorrect_qualification_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_404_NOT_FOUND)

    def test_patch_qualification_success(self, *args, **kwargs):
        expected_name = "Test name"
        expected_description = "Test description"

        # Task Run
        get_test_task_run(self.db)

        # Qualifications
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification", qualification_id=qualification_id)
            response = self.client.patch(
                url,
                json={"name": expected_name, "description": expected_description},
            )
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertIn("creation_date", result)
        self.assertIn("description", result)
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertEqual(result["id"], str(qualification_id))
        self.assertEqual(result["name"], expected_name)
        self.assertEqual(result["description"], expected_description)

    def test_patch_qualification_no_field_name_error(self, *args, **kwargs):
        incorrect_name = ""
        expected_description = "Test description"

        # Task Run
        get_test_task_run(self.db)

        # Qualifications
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification", qualification_id=qualification_id)
            response = self.client.patch(
                url,
                json={"name": incorrect_name, "description": expected_description},
            )
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result, {"error": 'Field "name" is required.'})

    def test_delete_qualification_success(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Qualifications
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification", qualification_id=qualification_id)
            response = self.client.delete(url)

        with self.assertRaises(EntryDoesNotExistException) as cm:
            self.db.get_qualification(qualification_id)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            str(cm.exception),
            f"Table qualifications has no qualification_id {qualification_id}",
        )


if __name__ == "__main__":
    unittest.main()
