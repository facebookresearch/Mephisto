#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import StringIDRow
from mephisto.data_model.qualification import Qualification


class QualificationsView(MethodView):
    def get(self) -> dict:
        """ Get all available qualifications (to select "approve" and "reject" qualifications) """

        db_qualifications: List[Qualification] = app.db.find_qualifications()
        app.logger.debug(f"Found qualifications in DB: {db_qualifications}")

        qualifications = [
            {
                "id": q.db_id,
                "name": q.qualification_name,
            }
            for q in db_qualifications
        ]

        app.logger.debug(f"Qualifications: {qualifications}")

        return {
            "qualifications": qualifications,
        }

    def post(self) -> dict:
        """ Create a new qualification """

        data: dict = request.json
        qualification_name = data and data.get("name")

        if not qualification_name:
            raise BadRequest("Field \"name\" is required.")

        db_qualifications: List[Qualification] = app.db.find_qualifications(qualification_name)

        if db_qualifications:
            raise BadRequest(f"Qualifications with name \"{qualification_name}\" already exists.")

        db_qualification_id: str = app.db.make_qualification(qualification_name)
        db_qualification: StringIDRow = app.db.get_qualification(db_qualification_id)

        return {
            "id": db_qualification["qualification_id"],
            "name": db_qualification["qualification_name"],
        }
