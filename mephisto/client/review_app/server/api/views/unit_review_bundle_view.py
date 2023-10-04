#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import current_app as app
from flask import send_file
from flask.views import MethodView

from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit


class UnitReviewBundleView(MethodView):
    def get(self, unit_id: str = None) -> dict:
        """Return review ReactJS bundle depending on TaskRun args from config"""

        unit: Unit = Unit.get(app.db, str(unit_id))
        app.logger.debug(f"Found Unit in DB: {unit}")
        task_run: TaskRun = unit.get_task_run()
        react_reviewapp_bundle_js = task_run.args["blueprint"]["task_source_review"]
        return send_file(react_reviewapp_bundle_js, mimetype="text/javascript")
