#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.utils.testing import get_test_qualification
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestQualificationsView(BaseTestApiViewCase):
    def test_qualification_list_one_qualification_success(self, *args, **kwargs):
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualifications")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["qualifications"]), 1)
        self.assertEqual(result["qualifications"][0]["id"], qualification_id)

    def test_qualification_list_empty_success(self, *args, **kwargs):
        with self.app_context:
            url = url_for("qualifications")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["qualifications"]), 0)

    def test_qualification_create_success(self, *args, **kwargs):
        qualification_name = "Test name"

        with self.app_context:
            url = url_for("qualifications")
            response = self.client.post(url, json={"name": qualification_name})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["name"], qualification_name)
        self.assertTrue("id" in result)

    def test_qualification_create_no_passed_name_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("qualifications")
            response = self.client.post(url, json={})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], 'Field "name" is required.')

    def test_qualification_create_already_exists_error(self, *args, **kwargs):
        qualification_name = "Test name"
        get_test_qualification(self.db, name=qualification_name)

        with self.app_context:
            url = url_for("qualifications")
            response = self.client.post(url, json={"name": qualification_name})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result["error"],
            f'Qualification with name "{qualification_name}" already exists.',
        )


if __name__ == "__main__":
    unittest.main()
