---
sidebar_position: 1
---

# 10-minute Quickstart

First, clone this repo to your local system.

Mephisto requires >= Python 3.8 and >= npm v6.

### Installation

Run the following in the root repo directory:

```bash
$ pip install -e .
```

*Alternatively, we also support installation via the dependency/environment manager project [poetry](https://github.com/python-poetry/poetry) as an option:*

```bash
# install poetry
$ curl -sSL https://install.python-poetry.org | python3 -
# from the root dir, install Mephisto:
$ poetry install
```

*Are you a Docker user? We support that too! Check out [our Docker guide](../how_to_use/efficiency_organization/docker).*

### Setup

Now that you have Mephisto installed, you should have access to the `mephisto` CLI tool.

Let's use this CLI tool to set up a data directory via the `mephisto config` command. The data directory is where the results of your crowdsourcing tasks will be stored.

The command below expects that you have created a folder named "mephisto-data" at your home directory and a folder named "data" inside of it.

```bash
$ mephisto config core.main_data_directory ~/mephisto-data/data
```

Check that everything is set up correctly!
```bash
$ mephisto check
Mephisto seems to be set up correctly.
```

### (Optional) Set up MTurk

If you want to be launching requests on MTurk, you'll want to create a requester. To do this you'll want to create an IAM role on AWS with the `MechanicalTurkFullAccess` permission, on an AWS account that is linked to the requester you want to use. You will be given an `access_key_id` and a `secret_access_key`. To register these with Mephisto, a new requester can be setup via the Mephisto CLI (make sure to replace `$ACCESS_KEY` and `$SECRET_KEY` below):

```bash
$ mephisto register mturk \
        name=my_mturk_user \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

You can choose any name here instead of `my_mturk_user` - this will be the id that you later refer to when using that requester.

For an `mturk_sandbox` requester, you should suffix the requester name with *"_sandbox"*, e.g.: `my_mturk_user_sandbox`.

Here's an example of setting up an "mturk_sandbox" requester:

```bash
$ mephisto register mturk_sandbox \
        name=my_mturk_user_sandbox \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY

Registered successfully.
```

Note that registering a sandbox user will not create a new entry in your `~/.aws/credentials` file if it's for the same account as your production user, as sandbox and prod use the same access keys.

After this, you can use `mephisto.provider.requester_name=my_mturk_user` or `mephisto.provider.requester_name=my_mturk_user_sandbox` respectively to launch a task live or on sandbox.

### (Optional) Set up Heroku

If you want to launch a task publicly, you'll need to use an `Architect` with external access. At the moment, we support the `HerokuArchitect` and `EC2Architect`, though the former is simpler to use. The steps for setup can be found by running:
```bash
$ python mephisto/scripts/heroku/initialize_heroku.py 
```
If you get the message "Successfully identified a logged in heroku user.", then you're done. Otherwise, this script will give you a set of steps to log in to the heroku CLI.

## Let's get launching!

Now that you have your environment set up, you're ready to get your first task running. [Continue here.](../tutorials/first_task)
