#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Tuple

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import StringIDRow


class QualificationView(MethodView):
    def get(self, qualification_id: str = None) -> dict:
        """Get qualification"""

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        app.logger.debug(f"Found Qualification in DB: {db_qualification}")

        return {
            "creation_date": db_qualification["creation_date"],
            "description": db_qualification["description"],
            "id": db_qualification["qualification_id"],
            "name": db_qualification["qualification_name"],
        }

    def patch(self, qualification_id: str = None) -> dict:
        """Update qualification"""

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        app.logger.debug(f"Found Qualification in DB: {db_qualification}")

        data: dict = request.json
        name: str = data and data.get("name")
        description: str = data and data.get("description")

        if not name:
            raise BadRequest('Field "name" is required.')

        name = name.strip()
        description = description.strip() if description else None

        app.db.update_qualification(
            qualification_id=qualification_id,
            name=name,
            description=description,
        )

        updated_qualification: StringIDRow = app.db.get_qualification(qualification_id)

        return {
            "creation_date": updated_qualification["creation_date"],
            "description": updated_qualification["description"],
            "id": updated_qualification["qualification_id"],
            "name": updated_qualification["qualification_name"],
        }

    def delete(self, qualification_id: str = None) -> Tuple[dict, int]:
        """Delete qualification"""

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        app.logger.debug(f"Found Qualification in DB: {db_qualification}")

        app.db.delete_qualification(qualification_name=db_qualification["qualification_name"])

        return {}
