#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script to pull the current version of `mephisto-task` in the
repo and push that version to all files setting a CURR_MEPHISTO_TASK_VERSION
constant value
"""

import os
import re
import json
from mephisto.operations.utils import get_root_dir

ROOT_DIR = get_root_dir()
PATTERN = r'(CURR_MEPHISTO_TASK_VERSION = "[0-9a-zA-Z.]*")'
TARGET_FILES = [
    "mephisto/abstractions/architects/router/flask/mephisto_flask_blueprint.py",
    "mephisto/abstractions/architects/router/node/server.js",
    "mephisto/abstractions/architects/router/build_router.py",
]
MEPHISTO_TASK_PACKAGE = os.path.join(ROOT_DIR, "packages/mephisto-task/package.json")


def run_replace():
    assert os.path.exists(
        MEPHISTO_TASK_PACKAGE
    ), f"Can't find task package at {MEPHISTO_TASK_PACKAGE}"
    with open(MEPHISTO_TASK_PACKAGE) as mephisto_task_package:
        version = json.load(mephisto_task_package)["version"]

    print(f"Updating files to use mephisto-task version {version}")
    output = f'CURR_MEPHISTO_TASK_VERSION = "{version}"'

    for fn in TARGET_FILES:
        target_file = os.path.join(ROOT_DIR, fn)
        assert os.path.exists(target_file), f"Missing target replace file {target_file}"
        print(f"Replacing contents in: {target_file}")
        with open(target_file, "r") as file_to_replace:
            file_contents = file_to_replace.read()
        new_contents = re.sub(PATTERN, output, file_contents)
        with open(target_file, "w") as file_to_replace:
            file_to_replace.write(new_contents)


if __name__ == "__main__":
    run_replace()
