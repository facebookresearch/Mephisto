#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.utils.testing import get_mock_requester
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestWorkerBlockView(BaseTestApiViewCase):
    def test_worker_block_no_review_note_passed_error(self, *args, **kwargs):
        _, worker_id = get_test_worker(self.db)

        with self.app_context:
            url = url_for("worker_block", worker_id=worker_id)
            response = self.client.post(url, json={})
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result["error"], "`review_note` parameter must be specified.")

    def test_worker_block_success(self, *args, **kwargs):
        # Requester
        requester = get_mock_requester(self.db)

        # Task Run
        get_test_task_run(self.db)

        # Worker
        _, worker_id = get_test_worker(self.db)
        worker: Worker = Worker.get(self.db, worker_id)
        blocked_before = worker.is_blocked(requester)

        # Unit
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        # Unit Review
        self.db.new_unit_review(unit_id, unit.task_id, worker_id, unit.db_status)

        with self.app_context:
            url = url_for("worker_block", worker_id=worker_id)
            response = self.client.post(url, json={"review_note": "Test", "unit_ids": [unit_id]})
            result = response.json

        worker: Worker = Worker.get(self.db, worker_id)
        blocked_after = worker.is_blocked(requester)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result, {})
        self.assertFalse(blocked_before)
        self.assertTrue(blocked_after)


if __name__ == "__main__":
    unittest.main()
