#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import find_unit_reviews
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestRevokeWorkersView(BaseTestApiViewCase):
    def test_grant_success(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        # Qualification
        qualification_id = get_test_qualification(self.db)

        # Unit Review
        self.db.new_unit_review(unit_id, unit.task_id, worker_id, unit.db_status)

        with self.app_context:
            url = url_for(
                "qualification_worker_revoke",
                qualification_id=qualification_id,
                worker_id=worker_id,
            )
            response = self.client.post(url, json={"unit_ids": [unit_id], "value": 10})
            result = response.json

        unit_reviews = find_unit_reviews(self.db, qualification_id, worker_id, unit.task_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result, {})
        self.assertEqual(len(unit_reviews), 1)
        self.assertEqual(unit_reviews[0]["revoked_qualification_id"], qualification_id)
        self.assertEqual(unit_reviews[0]["updated_qualification_id"], None)

    def test_grant_no_unit_ids_error(self, *args, **kwargs):
        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        # Qualification
        qualification_id = get_test_qualification(self.db)

        # Unit Review
        self.db.new_unit_review(unit_id, unit.task_id, worker_id, unit.db_status)

        with self.app_context:
            url = url_for(
                "qualification_worker_revoke",
                qualification_id=qualification_id,
                worker_id=worker_id,
            )
            response = self.client.post(url, json={})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], 'Field "unit_ids" is required.')


if __name__ == "__main__":
    unittest.main()
