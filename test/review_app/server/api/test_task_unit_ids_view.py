#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTaskUnitIdsView(BaseTestApiViewCase):
    def test_no_units_success(self, *args, **kwargs):
        task_name, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("worker_units_ids", task_id=task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["worker_units_ids"]), 0)

    def test_one_unit_success(self, *args, **kwargs):
        get_test_task_run(self.db)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("worker_units_ids", task_id=unit.task_id)
            response = self.client.get(url)
            result = response.json

        first_worker_unit_ids = result["worker_units_ids"][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["worker_units_ids"]), 1)
        self.assertEqual(first_worker_unit_ids["worker_id"], worker_id)
        self.assertEqual(first_worker_unit_ids["unit_id"], unit_id)


if __name__ == "__main__":
    unittest.main()
