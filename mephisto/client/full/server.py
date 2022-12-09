#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, send_file, jsonify  # type: ignore
from mephisto.client.config import Config
from mephisto.client.api import api
from mephisto.operations.operator import Operator
from mephisto.abstractions.databases.local_database import LocalMephistoDB

import os
import atexit
import signal


def get_app():
    app = Flask(
        __name__, static_url_path="/static", static_folder="webapp/build/static"
    )
    app.config.from_object(Config)

    app.register_blueprint(api, url_prefix="/api/v1")

    # Register extensions
    db = LocalMephistoDB()
    operator = Operator(db)
    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["db"] = db
    app.extensions["operator"] = operator

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def index(path):
        return send_file(os.path.join("webapp", "build", "index.html"))

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        response.headers.add("Cache-Control", "no-store")
        return response

    term_handler = signal.getsignal(signal.SIGINT)

    def cleanup_resources(*args, **kwargs):
        operator.shutdown()
        db.shutdown()
        term_handler(*args, **kwargs)

    atexit.register(cleanup_resources)
    signal.signal(signal.SIGINT, cleanup_resources)
    return app
