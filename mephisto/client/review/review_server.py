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


def run(build_dir, port, output, csv_headers, json=False, database=None, debug=False):
    global index_file, app
    global ready_for_next, current_data, finished, index_file
    global counter
    global task_name

    if not debug or output == "":
        # disable noisy logging of flask, https://stackoverflow.com/a/18379764
        import logging

        flask_log = logging.getLogger("werkzeug")
        flask_log.disabled = True
        flask_cli = sys.modules["flask.cli"]
        flask_cli.show_server_banner = lambda *x: None

    app = Flask(
        __name__,
        root_path=os.getcwd(),
        static_url_path="/static",
        static_folder=build_dir + "/static",
    )

    def json_reader(f):
        import json

        for jsonline in f:
            yield json.loads(jsonline)

    def mephistoDBReader():
        from mephisto.abstractions.databases.local_database import LocalMephistoDB
        from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser

        db = LocalMephistoDB()
        mephisto_data_browser = MephistoDataBrowser(db=db)
        units = mephisto_data_browser.get_units_for_task_name(database)

        def format_data_for_review(data):
            contents = data["data"]

            inputs = contents["inputs"]
            inputs_string = f"Character: {inputs['character_name']}, Description: {inputs['character_description']}"
            return f"{inputs_string}"

        for unit in units:
            yield format_data_for_review(mephisto_data_browser.get_data_from_unit(unit))

    def consume_data():
        global ready_for_next, current_data, finished, counter

        if database is not None:
            data_source = mephistoDBReader()
        elif json:
            data_source = json_reader(iter(sys.stdin.readline, ""))
        else:
            data_source = csv.reader(iter(sys.stdin.readline, ""))
            if csv_headers:
                next(data_source)

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
    def next_task():
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
