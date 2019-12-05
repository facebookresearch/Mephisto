from flask import Flask, send_file, jsonify
import os
from mephisto.client.config import Config
from mephisto.client.api import api

app = Flask(
    __name__, static_url_path="/static", static_folder="../webapp/build/static"
)
app.config.from_object(Config)


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def index(path):
    return send_file(os.path.join("..", "webapp", "build", "index.html"))


app.register_blueprint(api, url_prefix="/api/v1")
