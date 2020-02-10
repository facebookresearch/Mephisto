from flask import Blueprint, jsonify, request
from mephisto.core.utils import get_crowd_provider_from_type
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.database import EntryAlreadyExistsException
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.task import TaskRun
from mephisto.core.argparse_parser import get_extra_argument_dicts, parse_arg_dict
from mephisto.core.utils import (
    get_blueprint_from_type,
    get_crowd_provider_from_type,
    get_architect_from_type,
    get_valid_blueprint_types,
    get_valid_provider_types,
    get_valid_architect_types,
)
from mephisto.data_model.task_config import TaskConfig

api = Blueprint("api", __name__)
db = LocalMephistoDB()


@api.route("/requesters")
def get_available_requesters():
    requesters = db.find_requesters()
    dict_requesters = [r.to_dict() for r in requesters]
    return jsonify({"requesters": dict_requesters})


@api.route("/task_runs/running")
def get_running_task_runs():
    """Find running tasks by querying for all task runs that aren't completed"""
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


@api.route("/error", defaults={"status_code": "501"})
@api.route("/error/<string:status_code>")
def intentional_error(status_code):
    """
    A helper endpoint to test out cases in the UI where an error occurs.
    """
    raise InvalidUsage("An error occured", status_code=int(status_code))


@api.route("/task_runs/reviewable")
def get_reviewable_task_runs():
    """
    Find reviewable task runs by querying for all reviewable tasks
    and getting their runs
    """
    units = db.find_units(status=AssignmentState.COMPLETED)
    reviewable_count = len(units)
    task_run_ids = set([u.get_assignment().get_task_run().db_id for u in units])
    task_runs = [TaskRun(db, db_id) for db_id in task_run_ids]
    dict_tasks = [t.to_dict() for t in task_runs]
    # TODO maybe include warning for auto approve date once that's tracked
    return jsonify({"task_runs": dict_tasks, "total_reviewable": reviewable_count})


@api.route("/requester/<requester_type>/options")
def requester_details(requester_type):
    crowd_provider = get_crowd_provider_from_type(requester_type)
    RequesterClass = crowd_provider.RequesterClass
    params = get_extra_argument_dicts(RequesterClass)
    return jsonify(params)


@api.route("/requester/<string:requester_type>/register", methods=["POST"])
def register(requester_type):
    options = request.form.to_dict()
    crowd_provider = get_crowd_provider_from_type(requester_type)
    RequesterClass = crowd_provider.RequesterClass

    try:
        parsed_options = parse_arg_dict(RequesterClass, options)
    except Exception as e:
        return jsonify(
            {"success": False, "msg": f"error in parsing arguments: {str(e)}"}
        )

    if "name" not in parsed_options:
        return jsonify(
            {"success": False, "msg": "No name was specified for the requester."}
        )

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


@api.route("/<string:requester_name>/get_balance")
def get_balance(requester_name):
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
    BlueprintClass = get_blueprint_from_type(blueprint_type)
    params = get_extra_argument_dicts(BlueprintClass)
    return jsonify({"success": True, "options": params})


@api.route("/architects")
def get_available_architects():
    architect_types = get_valid_architect_types()
    return jsonify({"success": True, "architect_types": architect_types})


@api.route("/architect/<string:architect_type>/options")
def get_architect_arguments(architect_type):
    ArchitectClass = get_architect_from_type(architect_type)
    params = get_extra_argument_dicts(ArchitectClass)
    return jsonify({"success": True, "options": params})


@api.route("/task_run_options")
def get_basic_task_options():
    params = get_extra_argument_dicts(TaskConfig)
    return jsonify({"success": True, "options": params})


@api.route("/launch_task_run", methods=["POST"])
def launch_task_run(requester_type):
    # TODO parse out all of the details to be able to launch a task,
    try:
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})


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
