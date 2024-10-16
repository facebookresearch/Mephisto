#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.review_app.server.api.views import QualifyWorkerView


class WorkerQualificationsGrantView(MethodView):
    def post(self, worker_id: int) -> dict:
        """Grant multiple qualifications to a worker with units"""

        data: dict = request.json or {}
        unit_ids: List[str] = data.get("unit_ids")
        qualification_grants: List[dict] = data.get("qualification_grants", [])

        if not unit_ids:
            raise BadRequest('Field "unit_ids" is required.')

        if not qualification_grants:
            raise BadRequest('Field "qualification_grants" is required.')

        for qualification_grant in qualification_grants:
            qualification_id = qualification_grant.get("qualification_id")
            qualification_value = qualification_grant.get("value", 1)

            db_qualification: StringIDRow = app.db.get_qualification(qualification_id)

            if not db_qualification:
                app.logger.debug(f"Could not found qualification with ID={qualification_id}")
                # Do not raise any error, just ignore it
                continue

            worker: Worker = Worker.get(app.db, str(worker_id))

            for unit_id in unit_ids:
                unit: Unit = Unit.get(app.db, str(unit_id))

                QualifyWorkerView.grant_worker_qualification_with_unit(
                    qualification=db_qualification,
                    unit=unit,
                    worker=worker,
                    value=qualification_value,
                )

        return {}
