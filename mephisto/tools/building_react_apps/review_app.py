#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from mephisto.tools.scripts import build_custom_bundle
from mephisto.utils.console_writer import ConsoleWriter
from .utils import clean_single_react_app

REPO_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
REVIEW_APP_PATH = os.path.join(REPO_PATH, "mephisto", "review_app")

logger = ConsoleWriter()


# --- CLEAN ---


def clean_review_app(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(REVIEW_APP_PATH, "client")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


# --- BUILD ---


def build_review_app_ui(force_rebuild: bool = False, verbose: bool = False):
    if verbose:
        logger.info(f"[blue]Building '{REVIEW_APP_PATH}'[/blue]")

    build_custom_bundle(
        REVIEW_APP_PATH,
        force_rebuild=force_rebuild,
        webapp_name="client",
        build_command="build",
    )
