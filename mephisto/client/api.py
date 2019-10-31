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


@api.route("/requester/<string:type>/register", methods=["POST"])
def register(type):
    options = request.form.to_dict()
    crowd_provider = get_crowd_provider_from_type(type)
    RequesterClass = crowd_provider.RequesterClass
    db = LocalMephistoDB()

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
    db = LocalMephistoDB()
    requesters = db.find_requesters(requester_name=requester_name)

    if len(requesters) == 0:
        return jsonify({"success": False, 'msg': f'No requester available with name: {requester_name}'})

    requester = requesters[0]
    return jsonify({"balance": requester.get_available_budget()})
