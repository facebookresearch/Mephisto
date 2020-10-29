# 10 minute Quick Start

### Pre-req: Installation

First, clone this repo to your local system.

### Option A (via pip install)
Run the following in the root directory:

```bash
$ pip install -e .

# Verify that mephisto is installed correctly, and handle any required config:
$ mephisto check
Please enter the full path to a location to store Mephisto run data. By default this would be at '/private/home/jju/mephisto/data'. This dir should NOT be on a distributed file store. Press enter to use the default:
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
Please enter the full path to a location to store Mephisto run data. By default this would be at '/private/home/jju/mephisto/data'. This dir should NOT be on a distributed file store. Press enter to use the default:
Mephisto seems to be set up correctly.

```

## Step 1. Run your first task (locally)

```bash
$ cd examples/simple_static_task
$ python static_test_script.py

# This should launch a local server with the task hosted.
# You can then navigate to the task in your browser to complete the task.

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
        name=my_mturk_user \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

You can choose any name for `my_mturk_user`, as this will be the id that you later refer to when using that requester. For an `mturk_sandbox` requester, you should use `my_mturk_user_sandbox` as the name.

```bash
$ mephisto register mturk_sandbox \
        name=my_mturk_user_sandbox \
        access-key-id=$ACCESS_KEY\
        secret-access-key=$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

2. Next, let's run the task script again, but this time we'll override the requester and the architect.

```bash
$ cd examples/simple_static_task
$ python static_test_script.py mephisto/architect=heroku mephisto.provider.requester_name=my_mturk_user_sandbox
Locating heroku...
INFO - Creating a task run under task name: html-static-task-example
[mephisto.operations.operator][INFO] - Creating a task run under task name: html-static-task-example
Building server files...
...

# Note: my_mturk_user_sandbox is what we used to name the requester
# when we registered the mturk account in the previous step.

# The task name mentioned in the logs will be required to examine/review results of the task
```
The arguments `mephisto.provider.requester_name=my_mturk_user_sandbox` and `mephisto/architect=heroku` will tell the the script to use the mturk sandbox provider and the heroku architect (as opposed to the mock provider and local architect). Notice that if we're setting a full abstraction (like the architect) we reference it with `mephisto/abstraction=val`, however when we're setting an argument, we use `mephisto.abstraction.argument=val`. This tells hydra whether we're providing an argument value or the name of a configuration to load.


**Note**: If this is your first time running with the heroku architect, you may be asked to do some one-time setup work.

3. You can examine/review the results of the task by running `python examine_results.py` in the example directory. Enter the task name When prompted for `Input task name:`
