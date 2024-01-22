#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from pathlib import Path
from typing import Optional
from typing import Union

from flask import redirect
from flask import request
from flask import Response
from flask import send_file
from flask import url_for
from flask.views import MethodView
from flask_cors import cross_origin


class HomeView(MethodView):
    @cross_origin()
    def get(self, path: Optional[str] = None, *args, **kwargs) -> Union[Response, dict]:
        """Return client 'index.html'"""
        if request.path == "/":
            return redirect(url_for("client-tasks", path="tasks"), code=302)

        ui_html_file_path = os.path.join(
            Path(__file__).resolve().parent.parent.parent.parent,
            "client",
            "build",
            "index.html",
        )

        if not os.path.exists(ui_html_file_path):
            return {
                "error": (
                    "UI interface isn't ready to use. "
                    "Build it or use separate address for dev UI server."
                )
            }

        return send_file(ui_html_file_path, mimetype="text/html")
