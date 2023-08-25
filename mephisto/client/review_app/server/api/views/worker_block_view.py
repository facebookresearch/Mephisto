#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.data_model.worker import Worker


class WorkerBlockView(MethodView):
    def post(self, worker_id: int) -> dict:
        """ Permanently block a worker """

        data: dict = request.json
        feedback = data and data.get("feedback")

        # Validate params
        if not feedback:
            raise BadRequest("`feedback` parameter must be specified.")

        # Block worker
        worker = Worker.get(app.db, str(worker_id))
        worker.block_worker(feedback)

        return {}
