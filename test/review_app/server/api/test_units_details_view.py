#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.utils.testing import get_test_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestUnitsDetailsView(BaseTestApiViewCase):
    def test_units_no_arguments_passed_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units_details")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], "`unit_ids` parameter must be specified.")

    def test_units_parsing_arguments_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units_details") + "?unit_ids=wrong"
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], "`unit_ids` must be a comma-separated list of integers.")

    def test_no_units_success(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units_details") + "?unit_ids=1"
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["units"]), 0)

    def test_one_unit_success(self, *args, **kwargs):
        unit_id = get_test_unit(self.db)

        with self.app_context:
            url = url_for("units_details") + f"?unit_ids={unit_id}"
            response = self.client.get(url)
            result = response.json

        first_unit = result["units"][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["units"]), 1)
        self.assertEqual(first_unit["id"], int(unit_id))

        unit_fields = [
            "has_task_source_review",
            "id",
            "inputs",
            "outputs",
            "prepared_inputs",
            "unit_data_folder",
        ]
        for unit_field in unit_fields:
            self.assertTrue(unit_field in first_unit)


if __name__ == "__main__":
    unittest.main()
