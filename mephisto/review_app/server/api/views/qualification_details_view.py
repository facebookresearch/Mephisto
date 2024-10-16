#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import current_app as app
from flask.views import MethodView

from mephisto.abstractions.databases.local_database import StringIDRow


class QualificationDetailsView(MethodView):
    def get(self, qualification_id: str = None) -> dict:
        """Get qualification details"""

        db_qualification: StringIDRow = app.db.get_qualification(qualification_id)
        app.logger.debug(f"Found Qualification in DB: {db_qualification}")

        db_granted_qualifications: StringIDRow = app.db.find_granted_qualifications(
            qualification_id=qualification_id
        )

        return {
            "granted_qualifications_count": len(db_granted_qualifications),
        }
