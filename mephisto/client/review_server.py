#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, Blueprint, send_file, jsonify
from mephisto.client.config import Config
from mephisto.client.api import api
import os
import atexit
import signal
import csv
import sys
import time
import threading

# app = Flask(__name__, static_url_path="/static", static_folder="../webapp/build/static")
# app.config.from_object(Config)


def run(build_dir):
    global index_file, app
    global ready_for_next, current_data, finished, index_file
    app = Flask(
        __name__,
        root_path=os.getcwd(),
        static_url_path="/static",
        static_folder=build_dir + "/static",
    )

    def consume_data():
        global ready_for_next, current_data, finished
        data_source = csv.reader(iter(sys.stdin.readline, ""))

        finished = False
        for row in data_source:
            ready_for_next = threading.Event()
            current_data = row
            sys.stdout.write("{!r}\n".format(row))
            sys.stdout.flush()
            ready_for_next.wait()
        finished = True

    @app.route("/data")
    def data():
        global current_data, finished
        return jsonify(
            {"finished": finished, "data": current_data if not finished else None}
        )

    @app.route("/next")
    def next():
        global current_data, ready_for_next, finished
        ready_for_next.set()
        return jsonify(finished)

    @app.route("/")
    def index():
        global index_file
        return send_file(build_dir + "/index.html")

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
        term_handler(*args, **kwargs)

    atexit.register(cleanup_resources)
    signal.signal(signal.SIGINT, cleanup_resources)

    thread = threading.Thread(target=consume_data)
    thread.start()
    app.run(debug=False)
