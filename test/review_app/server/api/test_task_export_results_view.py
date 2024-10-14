#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.utils import http_status
from mephisto.review_app.server.api.views.task_export_results_view import get_result_file_path
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit
from mephisto.utils.testing import get_test_qualification
from mephisto.utils.testing import get_test_unit
from mephisto.utils.testing import get_test_worker
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTaskExportResultsView(BaseTestApiViewCase):
    @patch("mephisto.review_app.server.api.views.task_export_results_view.get_results_dir")
    def test_task_export_result_success(self, mock_get_results_dir, *args, **kwargs):
        mock_get_results_dir.return_value = self.data_dir

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

        results_file_data = "Test JS"

        results_file_path = get_result_file_path(self.data_dir, unit.task_id, 1)
        f = open(results_file_path, "w")
        f.write(results_file_data)
        f.close()

        with self.app_context:
            url = url_for("task_export_results", task_id=unit.task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(result, {"file_created": True})
        self.assertEqual(response.mimetype, "application/json")

    def test_task_export_result_not_found_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("task_export_results", task_id=999)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_404_NOT_FOUND)

    @patch(
        (
            "mephisto.review_app.server.api.views.task_export_results_view."
            "ENABLE_INCOMPLETE_TASK_RESULTS_EXPORT"
        ),
        False,
    )
    @patch("mephisto.review_app.server.api.views.task_export_results_view.check_if_task_reviewed")
    def test_task_export_result_not_reviews_error(
        self,
        mock_check_if_task_reviewed,
        *args,
        **kwargs,
    ):
        mock_check_if_task_reviewed.return_value = False

        unit_id = get_test_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        unit.set_db_status(AssignmentState.COMPLETED)

        with self.app_context:
            url = url_for("task_export_results", task_id=unit.task_id)
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result["error"],
            (
                "This task has not been fully reviewed yet. "
                "Please review it completely before requesting the results."
            ),
        )


if __name__ == "__main__":
    unittest.main()
