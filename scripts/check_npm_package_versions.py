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
from mephisto.utils.dirs import get_root_dir
from urllib.request import urlopen
from mephisto.utils.logger_core import format_loud


ROOT_DIR = get_root_dir()
CHECK_PACKAGES = ["mephisto-task", "bootstrap-chat"]


def run_check():
    all_success = True
    for pkg in CHECK_PACKAGES:
        package_location = os.path.join(ROOT_DIR, "packages", pkg, "package.json")
        assert os.path.exists(package_location), f"Can't find package {pkg} at {package_location}"
        with open(package_location) as package_json:
            version = json.load(package_json)["version"]

        print()
        print(f"Detected '{pkg}' version '{version}' at '{package_location}'")

        link = f"https://registry.npmjs.org/-/package/{pkg}/dist-tags"

        try:
            f = urlopen(link)
            contents = f.read().decode("utf-8")
            latest_version = json.loads(contents)["latest"]
            print(f"Detected '{pkg}@latest' as version '{latest_version}' on npm")

            if latest_version != version:
                print(
                    f"{format_loud('[VERSION MISMATCH]')} The latest version of the "
                    f"'{pkg}' package on npm ({latest_version}) doesn't match "
                    f"the version in the codebase ({version}). If this is part of a"
                    f"merge onto the main branch, you may want to deploy the packages first."
                )
                all_success &= False
        except:
            print(
                f"{format_loud('[ERROR]')} Could not access latest version of package '{pkg}' on npm."
            )
            all_success &= False

    if not all_success:
        sys.exit(1)


if __name__ == "__main__":
    run_check()
