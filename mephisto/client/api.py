from flask import Blueprint, jsonify, request
from mephisto.core.utils import get_crowd_provider_from_type
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.database import EntryAlreadyExistsException
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.task import TaskRun

api = Blueprint("api", __name__)
db = LocalMephistoDB()

@api.route("/requesters")
def get_available_requesters():
    requesters = db.find_requesters()
    dict_requesters = [r.to_dict() for r in requesters]
    return jsonify({'requesters': dict_requesters})


@api.route("/task_runs/running")
def get_running_task_runs():
    """Find running tasks by querying for all task runs that aren't completed"""
    task_runs = db.find_task_runs(is_completed=False)
    dict_tasks = [t.to_dict() for t in task_runs if not t.get_is_completed()]
    live_task_count = len([t for t in dict_tasks if not t['sandbox']])
    return jsonify({
        'task_runs': dict_tasks,
        'task_count': len(dict_tasks),
        'live_task_count': live_task_count,
    })

@api.route("/error")
def intentional_error():
    raise InvalidUsage("An error occured", status_code=501)

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
    return jsonify({
        'task_runs': dict_tasks,
        'total_reviewable': reviewable_count,
    })


@api.route("/requester/<type>")
def requester_details(type):
    crowd_provider = get_crowd_provider_from_type(type)
    RequesterClass = crowd_provider.RequesterClass
    params = RequesterClass.get_register_args()
    return jsonify(params)


@api.route("/requester/<string:type>/register", methods=["POST"])
def register(type):
    options = request.form.to_dict()
    crowd_provider = get_crowd_provider_from_type(type)
    RequesterClass = crowd_provider.RequesterClass

    if 'name' not in options:
        return jsonify({'success': False, 'msg': 'No name was specified for the requester.'})

    requesters = db.find_requesters(requester_name=options['name'])
    if len(requesters) == 0:
        requester = RequesterClass.new(db, options['name'])  # TODO: unhardcode
    else:
        requester = requesters[0]
    # except EntryAlreadyExistsException as e:
    #     return jsonify({'success': False, 'msg': 'Noah1027 already exists.'})
    try:
        print(options)
        requester.register(options)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})


@api.route("/<string:requester_name>/get_balance")
def get_balance(requester_name):
    requesters = db.find_requesters(requester_name=requester_name)

    if len(requesters) == 0:
        return jsonify({"success": False, 'msg': f'No requester available with name: {requester_name}'})

    requester = requesters[0]
    return jsonify({"balance": requester.get_available_budget()})


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
        rv['message'] = self.message
        return rv


@api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
