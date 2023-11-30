#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from flask import url_for

from mephisto.abstractions._subcomponents.agent_state import AgentState
from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestStatsView(BaseTestApiViewCase):
    def test_stats_success(self, *args, **kwargs):
        get_test_task_run(self.db)
        _, worker_id = get_test_worker(self.db)
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.ACCEPTED)
        qualification_id = get_test_qualification(self.db)
        self.db.new_unit_review(unit_id, unit.task_id, worker_id, AgentState.STATUS_APPROVED)
        self.db.update_unit_review(unit_id, qualification_id, worker_id)

        with self.app_context:
            url = url_for("stats") + f"?task_id={unit.task_id}"
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            result["stats"],
            {
                "approved_count": 1,
                "rejected_count": 0,
                "reviewed_count": 1,
                "soft_rejected_count": 0,
                "total_count": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
