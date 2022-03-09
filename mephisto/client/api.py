#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Blueprint, jsonify, request  # type: ignore
from flask import current_app as app  # type: ignore
from mephisto.abstractions.database import EntryAlreadyExistsException
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit
from mephisto.data_model.assignment import Assignment
from mephisto.operations.hydra_config import parse_arg_dict, get_extra_argument_dicts
from mephisto.operations.registry import (
    get_blueprint_from_type,
    get_crowd_provider_from_type,
    get_architect_from_type,
    get_valid_blueprint_types,
    get_valid_provider_types,
    get_valid_architect_types,
)
import sys
import traceback
import os

api = Blueprint("api", __name__)


@api.route("/requesters")
def get_available_requesters():
    db = app.extensions["db"]
    requesters = db.find_requesters()
    dict_requesters = [r.to_dict() for r in requesters]
    return jsonify({"requesters": dict_requesters})


@api.route("/task_runs/running")
def get_running_task_runs():
    """Find running tasks by querying for all task runs that aren't completed"""
    db = app.extensions["db"]
    task_runs = db.find_task_runs(is_completed=False)
    dict_tasks = [t.to_dict() for t in task_runs if not t.get_is_completed()]
    live_task_count = len([t for t in dict_tasks if not t["sandbox"]])
    return jsonify(
        {
            "task_runs": dict_tasks,
            "task_count": len(dict_tasks),
            "live_task_count": live_task_count,
        }
    )


@api.route("/task_runs/reviewable")
def get_reviewable_task_runs():
    """
    Find reviewable task runs by querying for all reviewable tasks
    and getting their runs
    """
    db = app.extensions["db"]
    units = db.find_units(status=AssignmentState.COMPLETED)
    reviewable_count = len(units)
    task_run_ids = set([u.get_assignment().get_task_run().db_id for u in units])
    task_runs = [TaskRun.get(db, db_id) for db_id in task_run_ids]
    dict_tasks = [t.to_dict() for t in task_runs]
    # TODO(OWN) maybe include warning for auto approve date once that's tracked
    return jsonify({"task_runs": dict_tasks, "total_reviewable": reviewable_count})


@api.route("/launch/options")
def launch_options():
    blueprint_types = get_valid_blueprint_types()
    architect_types = get_valid_architect_types()
    provider_types = get_valid_provider_types()
    return jsonify(
        {
            "success": True,
            "architect_types": architect_types,
            "provider_types": provider_types,
            "blueprint_types": [
                {"name": bp, "rank": idx + 1}
                for (idx, bp) in enumerate(blueprint_types)
            ],
        }
    )


@api.route("/task_runs/launch", methods=["POST"])
def start_task_run():
    # Blueprint, CrowdProvider, Architect (Local/Heroku), Dict of arguments

    info = request.get_json(force=True)
    input_arg_list = []
    for arg_content in info.values():
        input_arg_list.append(arg_content["option_string"])
        input_arg_list.append(arg_content["value"])
    try:
        operator = app.extensions["operator"]
        operator.parse_and_launch_run(input_arg_list)
        # MOCK? What data would we want to return?
        # perhaps a link to the task? Will look into soon!
        return jsonify({"status": "success", "data": info})
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({"success": False, "msg": f"error in launching job: {str(e)}"})


@api.route("/task_runs/<int:task_id>/units")
def view_unit(task_id):
    # TODO

    # MOCK
    return jsonify(
        {"id": task_id, "view_path": "https://google.com", "data": {"name": "me"}}
    )


@api.route("/task_runs/options")
def get_basic_task_options():
    params = get_extra_argument_dicts(TaskRun)
    return jsonify({"success": True, "options": params})


@api.route("/requester/<string:requester_type>/options")
def requester_details(requester_type):
    crowd_provider = get_crowd_provider_from_type(requester_type)
    RequesterClass = crowd_provider.RequesterClass
    params = get_extra_argument_dicts(RequesterClass)
    return jsonify(params)


@api.route("/requester/<string:requester_type>/register", methods=["POST"])
def requester_register(requester_type):
    options = request.get_json()
    crowd_provider = get_crowd_provider_from_type(requester_type)
    RequesterClass = crowd_provider.RequesterClass

    try:
        parsed_options = parse_arg_dict(RequesterClass, options)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify(
            {"success": False, "msg": f"error in parsing arguments: {str(e)}"}
        )
    if "name" not in parsed_options:
        return jsonify(
            {"success": False, "msg": "No name was specified for the requester."}
        )

    db = app.extensions["db"]
    requesters = db.find_requesters(requester_name=parsed_options["name"])
    if len(requesters) == 0:
        requester = RequesterClass.new(db, parsed_options["name"])
    else:
        requester = requesters[0]
    try:
        print(parsed_options)
        requester.register(parsed_options)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})


@api.route("/data/submitted_data")
def get_submitted_data():
    try:
        task_run_ids = request.args.getlist("task_run_id")
        task_names = request.args.getlist("task_name")
        assignment_ids = request.args.getlist("assignment_id")
        unit_ids = request.args.getlist("unit_ids")
        statuses = request.args.getlist("status")

        db = app.extensions["db"]
        units = []
        assignments = []
        assert len(task_names) == 0, "Searching via task names not yet supported"

        task_runs = [TaskRun.get(db, task_run_id) for task_run_id in task_run_ids]
        for task_run in task_runs:
            assignments += task_run.get_assignments()

        assignments += [
            Assignment.get(db, assignment_id) for assignment_id in assignment_ids
        ]

        if len(statuses) == 0:
            statuses = [
                AssignmentState.COMPLETED,
                AssignmentState.ACCEPTED,
                AssignmentState.REJECTED,
            ]

        filtered_assignments = [a for a in assignments if a.get_status() in statuses]

        for assignment in assignments:
            units += assignment.get_units()

        units += [Unit.get(db, unit_id) for unit_id in unit_ids]

        all_unit_data = []
        for unit in units:
            unit_data = {
                "assignment_id": unit.assignment_id,
                "task_run_id": unit.task_run_id,
                "status": unit.db_status,
                "unit_id": unit.db_id,
                "worker_id": unit.worker_id,
                "data": None,
            }
            agent = unit.get_assigned_agent()
            if agent is not None:
                unit_data["data"] = agent.state.get_data()
                unit_data["worker_id"] = agent.worker_id
            all_unit_data.append(unit_data)

        print(all_unit_data)
        return jsonify({"success": True, "units": all_unit_data})
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "msg": str(e)})


@api.route("/<string:requester_name>/get_balance")
def get_balance(requester_name):
    db = app.extensions["db"]
    requesters = db.find_requesters(requester_name=requester_name)

    if len(requesters) == 0:
        return jsonify(
            {
                "success": False,
                "msg": f"No requester available with name: {requester_name}",
            }
        )

    requester = requesters[0]
    return jsonify({"balance": requester.get_available_budget()})


@api.route("/requester/<string:requester_name>/launch_options")
def requester_launch_options(requester_type):
    db = app.extensions["db"]
    requesters = db.find_requesters(requester_name=requester_name)

    if len(requesters) == 0:
        return jsonify(
            {
                "success": False,
                "msg": f"No requester available with name: {requester_name}",
            }
        )
    provider_type = requesters[0].provider_type
    CrowdProviderClass = get_crowd_provider_from_type(requester_type)
    params = get_extra_argument_dicts(CrowdProviderClass)
    return jsonify({"success": True, "options": params})


@api.route("/blueprints")
def get_available_blueprints():
    blueprint_types = get_valid_blueprint_types()
    return jsonify({"success": True, "blueprint_types": blueprint_types})


@api.route("/blueprint/<string:blueprint_type>/options")
def get_blueprint_arguments(blueprint_type):
    if blueprint_type == "none":
        return jsonify({"success": True, "options": {}})
    BlueprintClass = get_blueprint_from_type(blueprint_type)
    params = get_extra_argument_dicts(BlueprintClass)
    return jsonify({"success": True, "options": params})


@api.route("/architects")
def get_available_architects():
    architect_types = get_valid_architect_types()
    return jsonify({"success": True, "architect_types": architect_types})


@api.route("/architect/<string:architect_type>/options")
def get_architect_arguments(architect_type):
    if architect_type == "none":
        return jsonify({"success": True, "options": {}})
    ArchitectClass = get_architect_from_type(architect_type)
    params = get_extra_argument_dicts(ArchitectClass)
    return jsonify({"success": True, "options": params})


@api.route("/unit/<string:unit_id>/accept", methods=["POST"])
def accept_unit(unit_id):
    return jsonify({"success": True})
    pass


@api.route("/unit/<string:unit_id>/reject", methods=["POST"])
def reject_unit(unit_id):
    return jsonify({"success": True})
    pass


@api.route("/unit/<string:unit_id>/softBlock", methods=["POST"])
def soft_block_unit(unit_id):
    return jsonify({"success": True})
    pass


@api.route("/unit/<string:unit_id>/hardBlock", methods=["POST"])
def hard_block_unit(unit_id):
    return jsonify({"success": True})
    pass


@api.route("/error", defaults={"status_code": "501"})
@api.route("/error/<string:status_code>")
def intentional_error(status_code):
    """
    A helper endpoint to test out cases in the UI where an error occurs.
    """
    raise InvalidUsage("An error occured", status_code=int(status_code))


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
