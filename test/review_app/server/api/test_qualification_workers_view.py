#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.utils import http_status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_unit
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import grant_test_qualification
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestQualificationWorkersView(BaseTestApiViewCase):
    def test_qualification_list_no_workers_success(self, *args, **kwargs):
        qualification_id = get_test_qualification(self.db)

        with self.app_context:
            url = url_for("qualification_workers", qualification_id=qualification_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(result["workers"]), 0)

    def test_qualification_list_one_worker_success(self, *args, **kwargs):
        # Unit
        unit_id = get_test_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.ACCEPTED)

        # Qualification
        qualification_id = get_test_qualification(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit Review
        self.db.new_worker_review(
            unit_id=unit_id,
            task_id=unit.task_id,
            worker_id=worker_id,
            status=unit.db_status,
        )
        self.db.update_worker_review(
            unit_id=unit_id,
            qualification_id=qualification_id,
            worker_id=worker_id,
        )

        # Granted Qualification
        qualification_value = 10
        grant_test_qualification(self.db, qualification_id, worker_id, qualification_value)

        with self.app_context:
            url = url_for("qualification_workers", qualification_id=qualification_id)
            response = self.client.get(url)
            result = response.json

        first_worker = result["workers"][0]
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(result["workers"]), 1)
        self.assertEqual(first_worker["worker_id"], worker_id)
        self.assertEqual(first_worker["value"], qualification_value)
        self.assertTrue("worker_review_id" in first_worker)
        self.assertTrue("granted_at" in first_worker)


if __name__ == "__main__":
    unittest.main()
