#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils import http_status
from mephisto.utils.testing import get_mock_requester
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestWorkerQualificationsGrantView(BaseTestApiViewCase):
    def test_worker_qualifications_grant_no_units_ids_error(self, *args, **kwargs):
        _, worker_id = get_test_worker(self.db)

        with self.app_context:
            url = url_for("worker_qualifications_grant", worker_id=worker_id)
            response = self.client.post(url, json={})
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], 'Field "unit_ids" is required.')

    def test_worker_qualifications_grant_no_qualification_grants_error(self, *args, **kwargs):
        _, worker_id = get_test_worker(self.db)

        with self.app_context:
            url = url_for("worker_qualifications_grant", worker_id=worker_id)
            response = self.client.post(url, json={"unit_ids": [1, 2]})
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], 'Field "qualification_grants" is required.')

    def test_worker_qualifications_grant_success(self, *args, **kwargs):
        expected_value_1 = "9"
        expected_value_2 = "10"

        # Requester
        requester = get_mock_requester(self.db)

        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        # Qualification
        qualification_id_1 = get_test_qualification(self.db, name="Test 1")
        qualification_id_2 = get_test_qualification(self.db, name="Test 2")

        granted_aualification_1_before = self.db.check_granted_qualifications(
            qualification_id_1,
            worker_id,
        )
        granted_aualification_2_before = self.db.check_granted_qualifications(
            qualification_id_2,
            worker_id,
        )

        # Unit Review
        self.db.new_worker_review(
            unit_id=unit_id,
            task_id=unit.task_id,
            worker_id=worker_id,
            status=unit.db_status,
        )

        with self.app_context:
            url = url_for("worker_qualifications_grant", worker_id=worker_id)
            response = self.client.post(
                url,
                json={
                    "unit_ids": [unit_id],
                    "qualification_grants": [
                        {
                            "qualification_id": qualification_id_1,
                            "value": expected_value_1,
                        },
                        {
                            "qualification_id": qualification_id_2,
                            "value": expected_value_2,
                        },
                    ],
                },
            )
            result = response.json

        granted_aualification_1_after = self.db.check_granted_qualifications(
            qualification_id_1,
            worker_id,
            expected_value_1,
        )
        granted_aualification_2_after = self.db.check_granted_qualifications(
            qualification_id_2,
            worker_id,
            expected_value_2,
        )

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result, {})
        self.assertEqual(len(granted_aualification_1_before), 0)
        self.assertEqual(len(granted_aualification_2_before), 0)
        self.assertEqual(len(granted_aualification_1_after), 1)
        self.assertEqual(len(granted_aualification_2_after), 1)


if __name__ == "__main__":
    unittest.main()
