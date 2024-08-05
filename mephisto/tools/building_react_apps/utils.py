#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
from pathlib import Path

from mephisto.utils.console_writer import ConsoleWriter

logger = ConsoleWriter()


def clean_single_react_app(
    webapp_path: str,
    remove_package_locks: bool = False,
    verbose: bool = False,
):
    if verbose:
        logger.info(f"[blue]Cleaning '{webapp_path}'[/blue]")

    build_path = os.path.join(webapp_path, "build")
    node_modules_path = os.path.join(webapp_path, "node_modules")
    package_locks_path = os.path.join(webapp_path, "package-lock.json")
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(node_modules_path, ignore_errors=True)

    if remove_package_locks:
        Path(package_locks_path).unlink(missing_ok=True)
