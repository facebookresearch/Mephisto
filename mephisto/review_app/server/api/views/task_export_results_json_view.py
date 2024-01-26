#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from flask import send_file
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from .task_export_results_view import get_result_file_path
from .task_export_results_view import get_results_dir


class TaskExportResultsJsonView(MethodView):
    def get(self, task_id: str = None, n_units: int = None) -> dict:
        """Get result data file in JSON format"""
        results_dir = get_results_dir()
        results_file_path = get_result_file_path(results_dir, task_id, n_units)

        if not os.path.exists(results_file_path):
            raise NotFound("File not found")

        return send_file(
            results_file_path,
            as_attachment=True,
            attachment_filename=f"task-{task_id}-results.json",
        )
