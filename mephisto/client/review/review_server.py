#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, Blueprint, send_file, jsonify, request
from datetime import datetime
import os
import atexit
import signal
import csv
import sys
import time
import threading


def run(
    build_dir,
    port,
    output,
    csv_headers,
    json=False,
    database_task_name=None,
    all_data=False,
    debug=False,
):
    global index_file, app
    global ready_for_next, current_data, finished, index_file
    global counter
    global all_data_list, datalist_update_time

    RESULTS_PER_PAGE_DEFAULT = 10
    TIMEOUT_IN_SECONDS = 300
    USE_TIMEOUT = True
    MODE = "ALL" if all_data else "OBO"
    RESULT_SUCCESS = "SUCCESS"
    RESULT_ERROR = "ERROR"

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

        def format_data_for_review(data):
            contents = data["data"]
            return f"{data}"

        units = mephisto_data_browser.get_units_for_task_name(database_task_name)
        for unit in units:
            yield format_data_for_review(mephisto_data_browser.get_data_from_unit(unit))

    def consume_data():
        """ For use in "one-by-one" or default mode. Runs on a seperate thread to consume mephisto review data line by line and update global variables to temporarily store this data """
        global ready_for_next, current_data, finished, counter

        if database_task_name is not None:
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

    def consume_all_data(page, results_per_page=RESULTS_PER_PAGE_DEFAULT, filters=None):
        """
        For use in "all" mode.
        Returns a filtered list of all data or a page of all data.
        Params:
            page: 1 indexed page number integer
            results_per_page: maximum number of results per page
            filters: keywords or sentences to filter data for. must be a list
        """
        global all_data_list, datalist_update_time
        paginated = type(page) is int
        if paginated:
            assert page > 0, "Page number should be a positive 1 indexed integer."
            assert (
                type(results_per_page) is int and results_per_page > 0
            ), "results_per_page should be a positive integer"

        first_index = (page - 1) * results_per_page if paginated else 0

        filtered_data_list = all_data_list
        if type(filters) is list:
            filtered_data_list = [
                item
                for item in all_data_list
                if all(word.lower() in str(item["data"]).lower() for word in filters)
            ]

        if database_task_name is not None:
            # If differnce in time since the last update to the data list is over 5 minutes, update list again
            # This can only be done for usage with mephistoDB as standard input is exhausted when originally creating the list
            now = datetime.now()
            if (
                USE_TIMEOUT
                and (now - datalist_update_time).total_seconds() > TIMEOUT_IN_SECONDS
            ):
                refresh_all_list_data()

        if paginated:
            list_len = len(filtered_data_list)
            if first_index > list_len - 1:
                return []
            results_per_page = (
                min(first_index + results_per_page, list_len) - first_index
            )
            if results_per_page < 0:
                return []
            return filtered_data_list[first_index : first_index + results_per_page]
        else:
            return filtered_data_list

    def refresh_all_list_data():
        """For use in "all" mode. Refreshes all data list when the data source is mephistoDB, allowing for new entries in the db to be included in the review"""
        global all_data_list, datalist_update_time
        data_source = mephistoDBReader()
        all_data_list = []
        count = 0
        for row in data_source:
            all_data_list.append({"data": row, "id": count})
            count += 1
        datalist_update_time = datetime.now()

    @app.route("/data_for_current_task")
    def data():
        """
        *** DEPRECATED ***
        For use in "one-by-one" or default mode.
        Based on global variables set by the consume_data method returns the piece of data currently being reviewed.
        If there is no more data being reviewed the app is shut down.
        """
        global current_data, finished
        if all_data:
            return jsonify(
                {
                    "error": 'mephisto review is in all mode, please get data by sending a GET request to "/data/:id"'
                }
            )
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
        """
        *** DEPRECATED ***
        For use in "one-by-one" or default mode.
        This route allows users to submit reviews for tasks.
        All review data must be contained within the body of the request.
        The review data is written directly to the output file specified in mephisto review.
        """
        global current_data, ready_for_next, finished, counter
        if all_data:
            return jsonify(
                {
                    "error": 'mephisto review is in all mode, please submit reviews by sending a POST request to "/data/:id"'
                }
            )
        result = (
            request.get_json(force=True)
            if request.method == "POST"
            else request.args.get("result")
        )

        if output == "":
            print("{}".format(result))
        else:
            with open(output, "a+") as f:
                f.write("{}\n".format(result))

        ready_for_next.set()
        time.sleep(0)
        return jsonify({"finished": finished, "counter": counter})

    @app.route("/data/<id>", methods=["GET", "POST"])
    def task_data_by_id(id):
        """
        This route takes a parameter of the id of an item being reviewed.
        This id represents the index (beginning at 0) of the item in the list of items being reviewed.
        If this route receives a GET request the data of the item at that position in the list of review items is returned.
        If this route receives a POST request a review is written for the item at the given index based on the body of JSON in the request.
        Accordingly for POST requests all review data must be in the JSON body of the request.
        The JSON for the review is written directly into the output file specified for mephisto review.
        """
        global finished, current_data, ready_for_next, counter, all_data_list
        id = int(id) if type(id) is int or (type(id) is str and id.isdigit()) else None
        if request.method == "GET":
            if all_data:
                list_len = len(all_data_list)
                if id is None or id < 0 or id >= list_len:
                    return jsonify(
                        {"error": f"Data with ID: {id} does not exist", "mode": MODE}
                    )
                return jsonify({"data": all_data_list[id], "mode": MODE})
            else:
                if id is None or id != counter - 1:
                    return jsonify(
                        {
                            "error": f"Please review the data point with ID: {counter - 1}",
                            "mode": MODE,
                        }
                    )
                data = {
                    "data": current_data if not finished else None,
                    "id": counter - 1,
                }
                if finished:
                    func = request.environ.get("werkzeug.server.shutdown")
                    if func is None:
                        raise RuntimeError("Not running with the Werkzeug Server")
                    func()
                return jsonify(
                    {
                        "finished": finished,
                        "data": data,
                        "mode": MODE,
                    }
                )
        else:
            review = request.get_json(force=True)
            if output == "":
                print("ID: {}, REVIEW: {}".format(id, review))
            else:
                with open(output, "a+") as f:
                    f.write("ID: {}, REVIEW: {}\n".format(id, review))
            if not all_data:
                ready_for_next.set()
                time.sleep(0)
            return jsonify(
                {"result": RESULT_SUCCESS, "finished": finished, "mode": MODE}
            )

    @app.route("/data")
    def all_task_data():
        """
        This route returns the list of all data being reviewed if the app is in "all" mode.
        Otherwise this route returns the id and data of the item currently being reviewed in "one-by-one" or standard mode.
        The id in the response refers to the index (beginning at 0) of the item being reviewed in the list of all items being reviewed.
        Params:
            page: 1 indexed page number for results
            results_per_page: number of results to show per page, must be positive integer
            filters: string representing keywords or senteces results must contain.
                Filters must be comma separated and spaced must be denoted by '%20'
        """
        global counter, current_data, all_data_list, finished
        if all_data:
            page = request.args.get("page", default=None, type=int)
            results_per_page = request.args.get(
                "results_per_page", default=RESULTS_PER_PAGE_DEFAULT, type=int
            )
            filters_str = request.args.get("filters", default=None, type=str)
            filters = None
            if type(filters_str) is str:
                filters_str = filters_str.replace("%20", " ")
                filters = filters_str.split(",")
                filters = [filt.strip() for filt in filters]
            try:
                data_point_list = consume_all_data(page, results_per_page, filters)
                total_pages = (
                    len(all_data_list) / results_per_page
                    if type(page) is int and page > 0
                    else 1
                )
                return jsonify(
                    {"data": data_point_list, "mode": MODE, "total_pages": total_pages}
                )
            except AssertionError as ae:
                print(f"Error: {ae.args[0]}")
                return jsonify({"error": ae.args[0], "mode": MODE})
        else:
            data = {"data": current_data if not finished else None, "id": counter - 1}
            return jsonify({"data": data, "mode": MODE, "finished": finished})

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

    if all_data:
        # if reading all data points, all data is loaded into memory before the app starts
        if database_task_name is not None:
            data_source = mephistoDBReader()
        elif json:
            data_source = json_reader(iter(sys.stdin.readline, ""))
        else:
            data_source = csv.reader(iter(sys.stdin.readline, ""))
            if csv_headers:
                next(data_source)

        all_data_list = []
        count = 0
        for row in data_source:
            all_data_list.append({"data": row, "id": count})
            count += 1
        datalist_update_time = datetime.now()
        finished = False
    else:
        thread = threading.Thread(target=consume_data)
        thread.start()
    if sys.stdout.isatty():
        print("Running on http://127.0.0.1:{}/ (Press CTRL+C to quit)".format(port))
    app.run(debug=False, port=port)
