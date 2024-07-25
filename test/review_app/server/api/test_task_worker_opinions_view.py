#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.data_model.task import Task
from mephisto.data_model.unit import Unit
from mephisto.utils import http_status
from mephisto.utils.testing import get_test_task
from mephisto.utils.testing import get_test_task_run
from mephisto.utils.testing import get_test_worker
from mephisto.utils.testing import make_completed_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestTaskWorkerOpinionsView(BaseTestApiViewCase):
    def test_task_worker_opinions_not_found_error(self, *args, **kwargs):
        with self.app_context:
            url = url_for("task_worker_opinions", task_id=999)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_404_NOT_FOUND)

    def test_task_worker_opinions_no_units(self, *args, **kwargs):
        task_name, task_id = get_test_task(self.db)

        with self.app_context:
            url = url_for("task_worker_opinions", task_id=task_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            response.json,
            {
                "task_name": task_name,
                "worker_opinions": [],
            },
        )

    def test_task_worker_opinions_success_with_units_without_opinions(self, *args, **kwargs):
        _, worker_id = get_test_worker(self.db)
        get_test_task_run(self.db)
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        task: Task = Task.get(self.db, unit.task_id)

        with self.app_context:
            url = url_for("task_worker_opinions", task_id=task.db_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            response.json,
            {
                "task_name": task.task_name,
                "worker_opinions": [],
            },
        )

    @patch("mephisto.tools.data_browser.DataBrowser.get_data_from_unit")
    def test_task_worker_opinions_success_with_units_with_opinions(
        self,
        mock_get_data_from_unit,
        *args,
        **kwargs,
    ):
        expected_attachment_1 = {
            "destination": "/tmp/",
            "encoding": "7bit",
            "fieldname": "attachments",
            "filename": "1-2-files-file-1.png",
            "mimetype": "image/png",
            "originalname": "file-1.png",
            "path": "/tmp/1-2-files-file-1.png",
            "size": 11111,
        }
        expected_attachment_2 = {
            "destination": "/tmp/",
            "encoding": "7bit",
            "fieldname": "attachments",
            "filename": "1-2-files-file-2.png",
            "mimetype": "image/png",
            "originalname": "file-2.png",
            "path": "/tmp/1-2-files-file-2.png",
            "size": 22222,
        }
        expected_question_1 = {
            "answer": "yes",
            "id": "7f352128-848d-4638-b465-3ff93142c01d",
            "question": "Was this task hard?",
            "reviewed": False,
            "toxicity": None,
        }
        expected_question_2 = {
            "answer": "great",
            "id": "0ef341a8-b93a-4d65-8487-588f0c8fe0e5",
            "question": "Is this a good example?",
            "reviewed": False,
            "toxicity": None,
        }

        _, worker_id = get_test_worker(self.db)
        get_test_task_run(self.db)
        unit_id = make_completed_unit(self.db)
        unit: Unit = Unit.get(self.db, unit_id)
        task: Task = Task.get(self.db, unit.task_id)

        agent = unit.get_assigned_agent()
        mock_get_data_from_unit.return_value = {
            "assignment_id": unit.assignment_id,
            "data": {},
            "metadata": {
                "worker_opinion": {
                    "attachments": [
                        expected_attachment_1,
                        expected_attachment_2,
                    ],
                    "attachments_by_fields": {
                        "attachments": [
                            expected_attachment_1,
                            expected_attachment_2,
                        ],
                    },
                    "questions": [
                        expected_question_1,
                        expected_question_2,
                    ],
                },
            },
            "status": agent.db_status,
            "task_end": agent.state.get_task_end(),
            "task_start": agent.state.get_task_start(),
            "unit_id": unit.db_id,
            "worker_id": agent.worker_id,
            "tips": agent.state.get_tips(),
            "feedback": agent.state.get_feedback(),
        }

        with self.app_context:
            url = url_for("task_worker_opinions", task_id=task.db_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(
            response.json,
            {
                "task_name": task.task_name,
                "worker_opinions": [
                    {
                        "data": {
                            "attachments": [
                                expected_attachment_1,
                                expected_attachment_2,
                            ],
                            "questions": [
                                expected_question_1,
                                expected_question_2,
                            ],
                        },
                        "unit_data_folder": agent.get_data_dir(),
                        "unit_id": unit.db_id,
                        "worker_id": unit.worker_id,
                    },
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
