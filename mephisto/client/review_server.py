#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, Blueprint, send_file, jsonify, request
import os
import atexit
import signal
import csv
import sys
import time
import threading


def run(build_dir, port, output, debug=False):
    global index_file, app
    global ready_for_next, current_data, finished, index_file
    global counter

    if not debug or output == "":
        # disable noisy logging of flask
        import logging

        log = logging.getLogger("werkzeug")
        log.disabled = True
        cli = sys.modules["flask.cli"]
        cli.show_server_banner = lambda *x: None

    app = Flask(
        __name__,
        root_path=os.getcwd(),
        static_url_path="/static",
        static_folder=build_dir + "/static",
    )

    def consume_data():
        global ready_for_next, current_data, finished, counter
        data_source = csv.reader(iter(sys.stdin.readline, ""))

        finished = False
        counter = 0
        for row in data_source:
            ready_for_next = threading.Event()
            current_data = row
            counter += 1
            ready_for_next.wait()
        finished = True

    @app.route("/data_for_current_task")
    def data():
        global current_data, finished

        if finished:
            func = request.environ.get("werkzeug.server.shutdown")
            if func is None:
                raise RuntimeError("Not running with the Werkzeug Server")
            func()

        return jsonify(
            {"finished": finished, "data": current_data if not finished else None}
        )

    @app.route("/submit_current_task", methods=["GET", "POST"])
    def next():
        global current_data, ready_for_next, finished, counter

        result = (
            request.get_json(force=True)
            if request.method == "POST"
            else request.ags.get("result")
        )

        if output == "":
            sys.stdout.write("{}\n".format(result))
            sys.stdout.flush()
        else:
            with open(output, "a+") as f:
                f.write("{}\n".format(result))

        ready_for_next.set()
        time.sleep(0)
        return jsonify({"finished": finished, "counter": counter})

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

    thread = threading.Thread(target=consume_data)
    thread.start()
    if sys.stdout.isatty():
        print("Running on http://127.0.0.1:{}/ (Press CTRL+C to quit)".format(port))
    app.run(debug=False, port=port)
