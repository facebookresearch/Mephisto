# router
This directory contains all of the Mephisto code regarding setting up and deploying and endpoint that can handle interfacing with the `mephisto-task` package. As of now there are two implementations, a node server in `deploy` and a Flask server in `flask`. Each of these can be extended upon such that you can deploy your own server (with whatever logic you may need) but still have mephisto routing functionality.

## `build_router.py`
This file contains code to be able to initialize the required build files for a server, assuming that they're set up properly. With the routers available in this directory, they should work out-of-the-box, but more configuration 

**TODO** Actually need to implement specifying a folder outside of those in the `router` directory as a target for `build_router.py`.

# Router Types
## deploy
This folder contains a node-based server that meets the specification for being a Mephisto Router. Additional files are served via `/static/` and uploaded files from the user are temporarily available from `/tmp/`. Currently retains the `deploy` name as it was our first server, but it is somewhat unwieldy.

## flask
This folder contains a Flask Blueprint (not to be confused with a Mephisto Blueprint) in `mephisto_flask_blueprint.py`. It also has example usage of this within the `app.py` file. The `app.py` file is what we actually deploy by default, and the contents demonstrate some important usage requirements for deploying a Mephisto router within an arbitrary Flask app. 

Key notes: you'll need to import the blueprint and the websocket server, and register the app alongside the websocket server. You'll also need to use `monkey.patch_all()` to ensure that the threading of the websockets and the main Flask server are able to interleave.

**TODO** right now this is hard coded to operate on port 3000, this needs to be updated to work via a configuration argument for usage in `LocalArchitect` and via environment variables for working via the `HerokuArchitect`.

# Routing implementation, functionality, and gotchas

**TODO** Document the requirements for a Mephisto Router to be running properly, including keeping track of local agent states, converting HTTP POST requests to websocket messages, and the heartbeat protocols.