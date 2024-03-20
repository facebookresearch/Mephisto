---
sidebar_position: 1
---

# 10-minute Quickstart

First, clone this repo to your local system.

Mephisto requires >= Python 3.8 and >= npm v6.

### Installation

You can install Mephisto in a few ways (Docker being the safest choice):

- **Using Docker:** see [our Docker guide](../how_to_use/efficiency_organization/docker).
- **Using pip:** run this in the root repo directory
    ```bash
    $ pip install -e .
    ```
- **Using [poetry](https://github.com/python-poetry/poetry):** run this in the root repo directory
    ```bash
    # install poetry
    $ curl -sSL https://install.python-poetry.org | python3 -
    # from the root dir, install Mephisto:
    $ poetry install
    ```

### Setup

Now that you have Mephisto installed, you should have access to the `mephisto` CLI tool.

- We can use this CLI tool to change data directory (where the results of your crowdsourcing tasks will be stored). Its default location is `data` inside the repo root; and here we will set it to `~/mephisto-data/data` directory:
    ```bash
    $ mkdir ~/mephisto-data
    $ mkdir ~/mephisto-data/data
    $ mephisto config core.main_data_directory ~/mephisto-data/data
    ```
- We can check that everything has been set up correctly:
```bash
$ mephisto check
Mephisto seems to be set up correctly.
```

### (Optional) Set up MTurk

If you want to  launch your tasks on MTurk, you'll want to create a requester. Doing this requires an IAM role on AWS with the `MechanicalTurkFullAccess` permission, on an AWS account that is linked to the requester you want to use. Once you obtain the API credentials for that role, register these with Mephisto, by creating a new requester (make sure to replace `$ACCESS_KEY` and `$SECRET_KEY` below):

```bash
$ mephisto register mturk \
        name=my_mturk_user \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

where `my_mturk_user` can be any name of your choice referring to this particular requester.

#### MTurk Sandbox

For an `mturk_sandbox` requester, you should suffix the requester name with *"_sandbox"* (e.g. `my_mturk_user_sandbox`).

Here's how to register an "mturk_sandbox" requester:

```bash
$ mephisto register mturk_sandbox \
        name=my_mturk_user_sandbox \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY

Registered successfully.
```

Note that registering a sandbox user will not create a new entry in your `~/.aws/credentials` file if it's for the same account as your production user, as sandbox and prod on AWS use the same access keys.

#### Task parameters

After registering a requester, you can use `mephisto.provider.requester_name=my_mturk_user` or `mephisto.provider.requester_name=my_mturk_user_sandbox` respectively to launch a task on Mturk.

---

### (Optional) Set up Heroku

If you want to launch a task publicly, you'll need to use an `Architect` with external access. At the moment, we support the `HerokuArchitect` and `EC2Architect`, though the former is simpler to use. The steps for setup can be found by running:
```bash
$ python mephisto/scripts/heroku/initialize_heroku.py
```

If you get the message "Successfully identified a logged in heroku user.", then you're done. Otherwise, this script will give you a set of steps to log in to the heroku CLI.

## Let's get running!

Now that you have your environment set up, you're ready for [Running your first task.](../tutorials/first_task)
