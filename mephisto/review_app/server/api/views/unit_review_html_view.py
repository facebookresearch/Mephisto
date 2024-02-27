#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from pathlib import Path

from flask import current_app as app
from flask import Response
from flask.views import MethodView

from mephisto.data_model.unit import Unit


class UnitReviewHtmlView(MethodView):
    def get(self, unit_id: str = None) -> Response:
        """Return 'index.html' with review ReactJS bundle URL"""

        unit: Unit = Unit.get(app.db, str(unit_id))
        app.logger.debug(f"Found Unit in DB: {unit}")

        html_file_path = os.path.join(
            Path(__file__).resolve().parent.parent.parent,
            "static",
            "index.html",
        )
        with open(html_file_path) as f:
            html_template = f.read()
            html = html_template.format(f"/units/{unit_id}/bundle.js")

        return Response(html, mimetype="text/html")
