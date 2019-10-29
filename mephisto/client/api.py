from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route("/get_balance")
def get_balance():
	return jsonify({'balance': 3})
