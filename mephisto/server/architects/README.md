# Architects
## Overview
Architects exist to automate the process of deploying the required task build for a task to a server.
They don't intend to cover all of the possible deployment processes and use cases, but the most common
ones for quick jobs, piloting, and testing with our interface.

As of now, these architects require the mephisto client to be directly communicating with the deployed
task server in order to complete a task and properly track worker progress and such.

## Implementations
### HerokuArchitect
Deploys the built task onto a heroku server, and then sets up communication with that server. The
heroku server can serve the relevant task content, and communicate with the mephisto client for
worker management, task flow control, and data saving.
### LocalArchitect
Deploys the built task on a server set up on localhost, for use deploying either for testing a task
in progress, or for deploying a task publicly from a machine that already has public web access enabled.
### HumanArchitect
Requires a human (you) to verify that you've set up your own server with the task files as expected
somewhere, and requests that you provide mephisto with the URL to register to it and communicate through.

## Future work
Future work is to develop a mephisto-remote that can set up a local client on a deployed server, and
make periodic requests to that server for updates, allowing the server to run on its own through task
completion, but keeping local information up-to-date and results in one place.
