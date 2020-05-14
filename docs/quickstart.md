# 10 minute Quick Start

### Pre-req: Installation

First, clone this repo to your local system.

### Option A
Install [poetry](https://github.com/python-poetry/poetry) to help with easy install and dependency management:

```
# install poetry
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# install the project, in the root dir do:
$ poetry install

# Verify that mephisto is installed correctly:
$ mephisto check
Mephisto seems to be set up correctly.

```

### Option B
Alteratively, you can install mephisto by running the following in the root directory. This may be a more familiar and easier approach for some:
```
pip install -e .
```
This however will not give you access to the optional `mephisto` CLI command. You can still use the `mephisto` CLI command though by replacing invoking it directly yourself with `python mephisto/client/cli.py` instead, or setting up an alias on your local system.

## Step 1. Run your first task (locally)

1. Navigate to the `examples/simple_static_task` directory. Run `python static_test_script.py`. This should launch a local server with the task hosted. You can navigate to the task in your browser and complete it.

2. A helper script is available for you to quickly examine the results of the task: `python examples/simple_static_task/examine_results.py`


## Step 2. Run the same task again, but now on mTurk

1. You'll first need to setup a requester. You can do so with the mephisto cli command. (Note: if you haven't set up mephisto with poetry, you should replace the `mephisto` command with `python mephisto/client/cli.py` instead).

```
$ mephisto register mturk \
        --name:my_mturk_user \
        --access-key-id:$ACCESS_KEY\
        --secret-access-key:$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

2. Next, update `examples/simple_static_task/static_test_script.py` by changing the `USE_LOCAL` flag at the top of the file to `false`. This will tell the remainder of the script to use the mturk provider and the heroku architect (as opposed to the mock provider and local architect).

3. Run `python static_test_script.py`. If this is your first time running with the heroku architect, you may be asked to do some one-time setup work.

4. As above, you can examine/review the results of the task by running: `python examples/simple_static_task/examine_results.py`