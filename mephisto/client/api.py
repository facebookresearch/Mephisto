from flask import Blueprint, jsonify, request
from mephisto.core.utils import get_crowd_provider_from_type
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.database import EntryAlreadyExistsException

api = Blueprint("api", __name__)


@api.route("/requester/<type>")
def requester_details(type):
    crowd_provider = get_crowd_provider_from_type(type)
    RequesterClass = crowd_provider.RequesterClass
    params = RequesterClass.get_register_args()
    return jsonify(params)


@api.route("/requester/<string:type>/register", methods=["GET"])
def register(type):
    options = request.args.to_dict()
    crowd_provider = get_crowd_provider_from_type(type)
    RequesterClass = crowd_provider.RequesterClass
    db = LocalMephistoDB()

    requesters = db.find_requesters(requester_name="Noah1027")
    if len(requesters) == 0:
        requester = RequesterClass.new(db, "Noah1027")  # TODO: unhardcode
    else:
        requester = requesters[0]
    # except EntryAlreadyExistsException as e:
    #     return jsonify({'success': False, 'msg': 'Noah1027 already exists.'})
    try:
        requester.register(options)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})


@api.route("/<string:requester_name>/get_balance")
def get_balance(requester_name):
    db = LocalMephistoDB()
    requester = db.find_requesters(requester_name=requester_name)
    requester = requester[0]
    return jsonify({"balance": requester.get_available_budget()})
