from flask import Flask, send_file, jsonify
import os
from config import Config
from api import api

app = Flask(__name__, static_url_path="/static", static_folder="../webapp/build/static")
app.config.from_object(Config)


@app.route("/", defaults={'path': 'index.html'})
@app.route("/<path:path>")
def index(path):
	return send_file(os.path.join('..', 'webapp', 'build', path))


app.register_blueprint(api, url_prefix='/api/v1')
