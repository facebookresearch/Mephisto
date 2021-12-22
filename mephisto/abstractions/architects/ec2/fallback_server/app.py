#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import json
import time
from flask import Flask, request, render_template  # type: ignore
from urllib.parse import urlparse
from gevent.pywsgi import WSGIServer  # type: ignore

app = Flask(__name__)

MY_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_BASE = os.path.join(MY_DIR, "access_logs")
PASSWORD_FILE = os.path.join(MY_DIR, "access_key.txt")
with open(PASSWORD_FILE, "r") as password_file:
    PASSWORD = password_file.read().strip()


@app.route("/view_logs")
def get_details():
    args = request.args
    if args.get("access_key") != PASSWORD:
        return main_route("view_logs")

    timestamp = args.get("timestamp", 0)
    found_logs = []
    for log_path in os.listdir(LOG_BASE):
        if not log_path.endswith(".json"):
            continue
        with open(os.path.join(LOG_BASE, log_path), "r") as log_file:
            data = json.load(log_file)
        if data["timestamp"] > timestamp:
            found_logs.append(data)

    return {"logs": found_logs}


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def main_route(path):
    args = dict(request.args)
    o = urlparse(request.base_url)
    host = o.hostname
    curr_time = time.time()
    if not host.startswith("10."):
        filename = f"{host}-{curr_time}-access.json"
        access_log = {
            "timestamp": curr_time,
            "args": args,
            "host": host,
        }
        with open(os.path.join(LOG_BASE, filename), "w+") as log_file:
            json.dump(access_log, log_file)

    return render_template("landing.html")


http_server = WSGIServer(("", 5000), app)
print("Launching server!", http_server)
http_server.serve_forever()
