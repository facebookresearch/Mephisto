#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestUnitsView(BaseTestApiViewCase):
    def test_units_no_arguments_passed_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result["error"],
            "At least one of `task_id` or `unit_ids` parameters must be specified.",
        )

    def test_no_units_success(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units") + "?task_id=999"
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(result["error"], "Not found")

    def test_one_unit_with_task_id_success(self, *args, **kwargs):
        # Create 1 COMPLETED unit
        unit_id = get_test_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("units") + f"?task_id={unit.task_id}"
            response = self.client.get(url)
            result = response.json

        first_response_unit = result["units"][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["units"]), 1)

        self.assertEqual(first_response_unit["id"], int(unit_id))
        self.assertEqual(first_response_unit["worker_id"], unit.worker_id)
        self.assertEqual(first_response_unit["task_id"], int(unit.task_id))
        self.assertEqual(first_response_unit["status"], unit.db_status)

        self.assertTrue("pay_amount" in first_response_unit)
        self.assertTrue("creation_date" in first_response_unit)

        self.assertTrue("results" in first_response_unit)
        self.assertTrue("start" in first_response_unit["results"])
        self.assertTrue("end" in first_response_unit["results"])
        self.assertTrue("inputs_preview" in first_response_unit["results"])
        self.assertTrue("outputs_preview" in first_response_unit["results"])

        self.assertTrue("review" in first_response_unit)
        self.assertTrue("bonus" in first_response_unit["review"])
        self.assertTrue("review_note" in first_response_unit["review"])

    def test_one_unit_with_unit_ids_success(self, *args, **kwargs):
        # Create 2 COMPLETED units
        unit_1_id = get_test_unit(self.db)
        unit_1: Unit = Unit.get(self.db, unit_1_id)
        unit_2_id = self.db.new_unit(
            unit_1.task_id,
            unit_1.task_run_id,
            unit_1.requester_id,
            unit_1.db_id,
            2,
            1,
            unit_1.provider_type,
            unit_1.task_type,
        )
        unit_2: Unit = Unit.get(self.db, unit_2_id)
        unit_1.set_db_status(AssignmentState.COMPLETED)
        unit_2.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("units") + f"?unit_ids={','.join([unit_1_id])}"
            response = self.client.get(url)
            result = response.json

        first_response_unit = result["units"][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["units"]), 1)
        self.assertEqual(first_response_unit["id"], int(unit_1_id))

    def test_two_units_with_unit_ids_success(self, *args, **kwargs):
        # Create 2 COMPLETED units
        unit_1_id = get_test_unit(self.db)
        unit_1: Unit = Unit.get(self.db, unit_1_id)
        unit_2_id = self.db.new_unit(
            unit_1.task_id,
            unit_1.task_run_id,
            unit_1.requester_id,
            unit_1.db_id,
            2,
            1,
            unit_1.provider_type,
            unit_1.task_type,
        )

        unit_2: Unit = Unit.get(self.db, unit_2_id)
        unit_1.set_db_status(AssignmentState.COMPLETED)
        unit_2.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("units") + f"?unit_ids={','.join([unit_1_id, unit_2_id])}"
            response = self.client.get(url)
            result = response.json

        first_response_unit = result["units"][0]
        second_response_unit = result["units"][1]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["units"]), 2)
        self.assertEqual(first_response_unit["id"], int(unit_1_id))
        self.assertEqual(second_response_unit["id"], int(unit_2_id))


if __name__ == "__main__":
    unittest.main()
