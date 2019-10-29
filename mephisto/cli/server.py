from flask import Flask, send_file
import os
from config import Config

app = Flask(__name__, static_url_path="/static", static_folder="../webapp/build/static")
app.config.from_object(Config)

@app.route("/")
def main():
    index_path = os.path.join('..', 'webapp', 'build', 'index.html')
    return send_file(index_path)

@app.route("/<path:path>")
def index(path):
	# print(path)
	# print(os.path.join('..', 'webapp', 'build', path))
	# print(os.path.isfile(os.path.join('..', 'webapp', 'build', path)))
	# root_dir = os.path.dirname(os.getcwd())
	return send_file(os.path.join('..', 'webapp', 'build', path))

