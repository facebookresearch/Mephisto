from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)


@api.route("/requester/<type>")
def requester_details(type):
    if type == "mturk":
        return jsonify(
            {
                "type": "mturk",
                "fields": [
                    {"name": "Access ID", "required": True},
                    {"name": "Secret Key", "required": True},
                    {"name": "Default Region", "required": False},
                ],
            }
        )
    else:
        return jsonify({})


@api.route("/requester/<string:type>/register", methods=["GET"])
def register(type):
    options = request.args.to_dict()
    return jsonify(options)

    # get the provider from the user
    # use utils to get provider for that type
    # get the required arguments that provider needs to setup
    # show those to the user
    # user enters in
    # pass back in


@api.route("/get_balance")
def get_balance():
    # connect to the sqlitedb if exists
    # get the requester ID
    # use the requester API to get the current balance
    return jsonify({"balance": 3})
