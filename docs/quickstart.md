# 10 minute Quick Start

### Pre-req: Installation

1. Clone this repo to your local system.
2. Install [poetry](https://github.com/python-poetry/poetry) to help with easy install and dependency management:

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

3. Run `poetry install` in the root mephisto project folder.

4. Voila! Test that mephisto is installed correctly by running the optional web interface with `mephisto web`.

### Step 1. Set up a requester

```
$ mephisto register mturk \
        --name:my_mturk_user \
        --access-key-id:$ACCESS_KEY\
        --secret-access-key:$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.

```

### Step 2. Run your first task

TODO: add here