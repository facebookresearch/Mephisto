#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils import http_status
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestGrantedQualificationsView(BaseTestApiViewCase):
    def test_granted_qualifications_list_one_qualification_success(self, *args, **kwargs):
        granted_value = 999

        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        # Qualifications
        qualification_id = get_test_qualification(self.db)
        grant_test_qualification(self.db, qualification_id, worker_id, granted_value)

        # Unit Review
        self.db.new_unit_review(unit_id, unit.task_id, worker_id, unit.db_status)
        self.db.update_unit_review(unit_id, qualification_id, worker_id)

        with self.app_context:
            url = url_for("granted_qualifications")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(result["granted_qualifications"]), 1)
        self.assertIn("granted_at", result["granted_qualifications"][0])
        self.assertIn("qualification_id", result["granted_qualifications"][0])
        self.assertIn("qualification_name", result["granted_qualifications"][0])
        self.assertIn("units", result["granted_qualifications"][0])
        self.assertIn("value_current", result["granted_qualifications"][0])
        self.assertIn("worker_id", result["granted_qualifications"][0])
        self.assertIn("worker_name", result["granted_qualifications"][0])
        self.assertEqual(result["granted_qualifications"][0]["qualification_id"], qualification_id)
        self.assertEqual(result["granted_qualifications"][0]["value_current"], granted_value)
        self.assertEqual(result["granted_qualifications"][0]["worker_id"], worker_id)
        self.assertIn("task_id", result["granted_qualifications"][0]["units"][0])
        self.assertIn("task_name", result["granted_qualifications"][0]["units"][0])
        self.assertIn("unit_id", result["granted_qualifications"][0]["units"][0])
        self.assertIn("value", result["granted_qualifications"][0]["units"][0])
        self.assertEqual(result["granted_qualifications"][0]["units"][0]["unit_id"], unit_id)


if __name__ == "__main__":
    unittest.main()
