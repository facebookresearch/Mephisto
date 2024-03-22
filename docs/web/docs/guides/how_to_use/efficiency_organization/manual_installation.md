---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 4
---

# Manual installation Mephisto

_(THIS FILE IS WORK IN PROGRESS)_

First, clone this repo to your local system.

Mephisto requires >= Python 3.8 and >= npm v6.

### Installation

You can install Mephisto in a few ways (Docker being the safest choice):

- **Using docker:** see [Running Mephisto with Docker](/docs/guides/how_to_use/efficiency_organization/docker/)
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

Now that you have Mephisto installed, you should have access to the `mephisto` CLI tool. _If using Docker, you will need to SSH into the Docker container first._

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

Note that registering a sandbox user will not create a new entry in your `~/.aws/credentials` file if it's for the same account as your production user, as sandbox and prod on AWS use the same access keys.

#### Task parameters

After registering a requester, you can use `mephisto.provider.requester_name=my_mturk_user` or `mephisto.provider.requester_name=my_mturk_user_sandbox` respectively to launch a task on Mturk.

---

## Let's get running!

Now that you have your environment set up, you're ready for [Running your first task.](/docs/guides/tutorials/first_task/)
