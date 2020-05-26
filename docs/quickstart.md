# 10 minute Quick Start

### Pre-req: Installation

First, clone this repo to your local system.

### Option A (via pip install)
Run the following in the root directory:

```bash
$ pip install -e .

# Verify that mephisto is installed correctly:
$ mephisto check
Mephisto seems to be set up correctly.
```

### Option B (via poetry)
Alteratively, you can install [poetry](https://github.com/python-poetry/poetry) to help with easy install, dependency management, and automatic virtual environment isolation:

```bash
# install poetry
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# install the project, in the root dir do:
$ poetry install

# Verify that mephisto is installed correctly:
$ mephisto check
Mephisto seems to be set up correctly.

```

## Step 1. Run your first task (locally)

```bash
$ cd examples/simple_static_task
$ python static_test_script.py

# This should launch a local server with the task hosted.
# You can then navigate to the task in your browser and complete the task.

# TIP:
# By default, tasks are run using a "mock" requester, and a "local" architect.
# The "local" architect is reponsible for running a server on your local machine
# to host the task, and the "mock" requester is a dummy account since we won't
# be using an external crowd-provider platform such as mTurk to launch the task on.
#
# In the next step, we'll show you how to override these defaults so that you can
# host the task on Heroku and run it on mTurk instead.

# Once completed, a helper script is available for you to quickly
# examine the results of the task:

$ python examine_results.py

```

## Step 2. Run the same task again, but now on mTurk

1. You'll first need to setup a requester. You can do so with the mephisto cli command. (Note: if you haven't set up mephisto with poetry, you should replace the `mephisto` command with `python mephisto/client/cli.py` instead).

```bash
$ mephisto register mturk \
        --name:my_mturk_user \
        --access-key-id:$ACCESS_KEY\
        --secret-access-key:$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

2. Next, let's run the task script again, but this time we'll override the requester and the architect.

```bash
$ cd examples/simple_static_task
$ python static_test_script.py -atype heroku -rname my_mturk_user

# Note: my_mturk_user is what we used to name the requester
# when we registered the mturk account in the previous step.
```
The flags `-atype` (or `--architect-type`) and `-rname` (or `--requester-name`) will tell the the script to use the mturk provider and the heroku architect (as opposed to the mock provider and local architect).

**Note**: If this is your first time running with the heroku architect, you may be asked to do some one-time setup work.

3. As above, you can examine/review the results of the task by running `python examine_results.py` in the example directory.