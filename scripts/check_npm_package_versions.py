#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script that checks if the deployed packages on npm match
the version that's in our source repository.
"""

import os
import sys
import json
from mephisto.operations.utils import get_root_dir
from urllib.request import urlopen
from mephisto.operations.logger_core import format_loud


ROOT_DIR = get_root_dir()
MEPHISTO_TASK_PACKAGE = os.path.join(ROOT_DIR, "packages/mephisto-task/package.json")


def run_check():
    assert os.path.exists(
        MEPHISTO_TASK_PACKAGE
    ), f"Can't find task package at {MEPHISTO_TASK_PACKAGE}"
    with open(MEPHISTO_TASK_PACKAGE) as mephisto_task_package:
        version = json.load(mephisto_task_package)["version"]

    print(f"Detected mephisto-task version '{version}' at '{MEPHISTO_TASK_PACKAGE}'")

    link = "https://registry.npmjs.org/-/package/mephisto-task/dist-tags"

    try:
        f = urlopen(link)
        contents = f.read().decode("utf-8")
        latest_version = json.loads(contents)["latest"]
        print(f"Detected mephisto-task@latest as version '{version}' on npm")
    except:
        print(
            f"{format_loud('[ERROR]')} Could not access latest version of package on npm."
        )
        sys.exit(1)

    if latest_version != version:
        print(
            f"{format_loud('[VERSION MISMATCH]')} The latest version of the "
            f"'mephisto-task' package on npm ({latest_version}) doesn't match "
            f"the version in the codebase ({version}). If this is part of a"
            f"merge onto the main branch, you may want to deploy the packages first."
        )
        sys.exit(1)


if __name__ == "__main__":
    run_check()
