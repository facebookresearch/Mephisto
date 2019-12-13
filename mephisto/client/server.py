from flask import Flask, send_file, jsonify
import os
from mephisto.client.config import Config
from mephisto.client.api import api

app = Flask(__name__, static_url_path="/static", static_folder="../webapp/build/static")
app.config.from_object(Config)

app.register_blueprint(api, url_prefix="/api/v1")


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def index(path):
    return send_file(os.path.join("..", "webapp", "build", "index.html"))


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Cache-Control", "no-store")
    return response
