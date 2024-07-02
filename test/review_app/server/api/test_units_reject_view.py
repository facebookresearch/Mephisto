#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestUnitsRejectView(BaseTestApiViewCase):
    def test_units_reject_no_unit_ids_passed_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("units_reject")
            response = self.client.post(url, json={})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], "`unit_ids` parameter must be specified.")

    def test_units_reject_success(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("units_reject")
            response = self.client.post(url, json={"unit_ids": [unit_id]})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result, {})
        self.assertEqual(unit.get_db_status(), AssignmentState.REJECTED)


if __name__ == "__main__":
    unittest.main()
