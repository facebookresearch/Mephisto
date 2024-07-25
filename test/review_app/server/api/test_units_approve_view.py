#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.utils import http_status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestUnitsApproveView(BaseTestApiViewCase):
    def test_units_approve_no_unit_ids_passed_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units_approve")
            response = self.client.post(url, json={})
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], "`unit_ids` parameter must be specified.")

    def test_units_approve_success(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("units_approve")
            response = self.client.post(url, json={"unit_ids": [unit_id]})
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result, {})
        self.assertEqual(unit.get_db_status(), AssignmentState.ACCEPTED)

    def test_units_approve_bonus_param_format_error(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        bonus = "wrong"

        with self.app_context:
            url = url_for("units_approve")
            with self.assertLogs(level="ERROR") as cm:
                response = self.client.post(url, json={"unit_ids": [unit_id], "bonus": bonus})

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertIn(f"Could not pay bonus. Passed value is invalid: {bonus}", cm.output[0])

    @patch("mephisto.abstractions.providers.mock.mock_worker.MockWorker.bonus_worker")
    def test_units_approve_paying_bonus_error(self, mock_bonus_worker, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        bonus = 1

        error_message = "Test error message"
        mock_bonus_worker.return_value = (False, error_message)

        with self.app_context:
            url = url_for("units_approve")
            with self.assertLogs(level="ERROR") as cm:
                response = self.client.post(url, json={"unit_ids": [unit_id], "bonus": bonus})

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertIn(f"Could not pay bonus. Reason: {error_message}", cm.output[0])

    @patch("mephisto.abstractions.providers.mock.mock_worker.MockWorker.bonus_worker")
    def test_units_approve_paying_bonus_exception_error(self, mock_bonus_worker, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        bonus = 1

        mock_bonus_worker.side_effect = Exception("Error")

        with self.app_context:
            url = url_for("units_approve")
            with self.assertLogs(level="ERROR") as cm:
                response = self.client.post(url, json={"unit_ids": [unit_id], "bonus": bonus})

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertIn("Could not pay bonus. Unexpected error", cm.output[0])


if __name__ == "__main__":
    unittest.main()
