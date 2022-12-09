# router
This directory contains all of the Mephisto code regarding setting up and deploying and endpoint that can handle interfacing with the `mephisto-task` package. As of now there are two implementations, a node server in `deploy` and a Flask server in `flask`. Each of these can be extended upon such that you can deploy your own server (with whatever logic you may need) but still have mephisto routing functionality.

## `build_router.py`
This file contains code to be able to initialize the required build files for a server, assuming that they're set up properly. With the routers available in this directory, they should work out-of-the-box, but more configuration. If you want to specify your own build, you should start from the given servers, then provide the `architect.server_source_root` and `architect.server_type` arguments as appropriate with your server directory and the kind of server you're running.

# Router Types
## node
This folder contains a node-based server that meets the specification for being a Mephisto Router. Additional files are served via `/static/` and uploaded files from the user are temporarily available from `/tmp/`. 

## flask
This folder contains a Flask Blueprint (not to be confused with a Mephisto Blueprint) in `mephisto_flask_blueprint.py`. It also has example usage of this within the `app.py` file. The `app.py` file is what we actually deploy by default, and the contents demonstrate some important usage requirements for deploying a Mephisto router within an arbitrary Flask app. 

Key notes: you'll need to import the blueprint and the websocket server, and register the app alongside the websocket server. You'll also need to use `monkey.patch_all()` to ensure that the threading of the websockets and the main Flask server are able to interleave.

# Routing implementation, functionality, and gotchas

In short, the Mephisto protocol for routing requests from clients down to the Mephisto main server is somewhat complicated. There are a number of endpoints that need to retain the behavior that's captured in the comments of the Flask implementation's `mephisto_flask_blueprint.py` file. These should be enumerated further here.

**TODO** Document the requirements for a Mephisto Router to be running properly, including keeping track of local agent states, converting HTTP POST requests to websocket messages, and the heartbeat protocols.