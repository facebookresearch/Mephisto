#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os.path
from typing import Union

from flask import current_app as app
from flask import Response
from flask import send_file
from flask.views import MethodView
from omegaconf.errors import ConfigKeyError

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit


class UnitReviewBundleView(MethodView):
    def get(self, unit_id: str = None) -> Union[dict, Response]:
        """Return review ReactJS bundle depending on TaskRun args from config"""

        unit: Unit = Unit.get(app.db, str(unit_id))
        app.logger.debug(f"Found Unit in DB: {unit}")
        task_run: TaskRun = unit.get_task_run()

        try:
            react_reviewapp_bundle_js = task_run.args["blueprint"]["task_source_review"]

            if not os.path.exists(react_reviewapp_bundle_js):
                raise FileNotFoundError

        except (ConfigKeyError, FileNotFoundError) as e:
            return Response(
                json.dumps(
                    {
                        "error": (
                            "`blueprint.task_source_review` was not found or not specified "
                            "or database is corrupted or just old. "
                            "You need this settings to make review app work."
                        ),
                    }
                ),
                status=status.HTTP_404_NOT_FOUND,
                mimetype="application/json",
            )

        return send_file(react_reviewapp_bundle_js, mimetype="text/javascript")
