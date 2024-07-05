#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script for an easy rebuild of all FormComposer-related apps/packages (`build` and `node_modules`):
    - examples
    - generators
    - Review App
    - react packages

This is needed due to inter-dependency of Mephisto's rapidly evolving JS components.

To run this command:
    mephisto scripts form_composer rebuild_all_apps
"""

import argparse
import os
import shutil
from pathlib import Path

from rich import print

from mephisto.generators.form_composer.config_validation.utils import set_custom_triggers_js_env_var
from mephisto.generators.form_composer.config_validation.utils import (
    set_custom_validators_js_env_var,
)
from mephisto.tools.scripts import build_custom_bundle


def _clean_examples_form_composer_demo(repo_path: str, remove_package_locks: bool):
    webapp_path = os.path.join(
        repo_path,
        "examples",
        "form_composer_demo",
        "webapp",
    )
    print(f"[blue]Cleaning '{webapp_path}'[/blue]")
    build_path = os.path.join(webapp_path, "build")
    node_modules_path = os.path.join(webapp_path, "node_modules")
    package_locks_path = os.path.join(webapp_path, "package-lock.json")
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(node_modules_path, ignore_errors=True)
    if remove_package_locks:
        Path(package_locks_path).unlink(missing_ok=True)


def _clean_generators_form_composer(repo_path: str, remove_package_locks: bool):
    webapp_path = os.path.join(
        repo_path,
        "mephisto",
        "generators",
        "form_composer",
        "webapp",
    )
    print(f"[blue]Cleaning '{webapp_path}'[/blue]")
    build_path = os.path.join(webapp_path, "build")
    node_modules_path = os.path.join(webapp_path, "node_modules")
    package_locks_path = os.path.join(webapp_path, "package-lock.json")
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(node_modules_path, ignore_errors=True)
    if remove_package_locks:
        Path(package_locks_path).unlink(missing_ok=True)


def _clean_review_app(repo_path: str, remove_package_locks: bool):
    webapp_path = os.path.join(
        repo_path,
        "mephisto",
        "review_app",
        "client",
    )
    print(f"[blue]Cleaning '{webapp_path}'[/blue]")
    build_path = os.path.join(webapp_path, "build")
    node_modules_path = os.path.join(webapp_path, "node_modules")
    package_locks_path = os.path.join(webapp_path, "package-lock.json")
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(node_modules_path, ignore_errors=True)
    if remove_package_locks:
        Path(package_locks_path).unlink(missing_ok=True)


def _clean_packages_mephisto_task_multipart(repo_path: str, remove_package_locks: bool):
    webapp_path = os.path.join(
        repo_path,
        "packages",
        "mephisto-task-multipart",
    )
    print(f"[blue]Cleaning '{webapp_path}'[/blue]")
    build_path = os.path.join(webapp_path, "build")
    node_modules_path = os.path.join(webapp_path, "node_modules")
    package_locks_path = os.path.join(webapp_path, "package-lock.json")
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(node_modules_path, ignore_errors=True)
    if remove_package_locks:
        Path(package_locks_path).unlink(missing_ok=True)


def _clean_packages_react_form_composer(repo_path: str, remove_package_locks: bool):
    webapp_path = os.path.join(
        repo_path,
        "packages",
        "react-form-composer",
    )
    print(f"[blue]Cleaning '{webapp_path}'[/blue]")
    build_path = os.path.join(webapp_path, "build")
    node_modules_path = os.path.join(webapp_path, "node_modules")
    package_locks_path = os.path.join(webapp_path, "package-lock.json")
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(node_modules_path, ignore_errors=True)
    if remove_package_locks:
        Path(package_locks_path).unlink(missing_ok=True)


def _clean(repo_path: str, remove_package_locks: bool):
    print("[blue]Started cleaning up all `build` and `node_modules` directories[/blue]")
    _clean_examples_form_composer_demo(repo_path, remove_package_locks)
    _clean_generators_form_composer(repo_path, remove_package_locks)
    _clean_review_app(repo_path, remove_package_locks)
    _clean_packages_mephisto_task_multipart(repo_path, remove_package_locks)
    _clean_packages_react_form_composer(repo_path, remove_package_locks)
    print(
        "[green]"
        "Finished cleaning up all `build` and `node_modules` directories successfully!"
        "[/green]"
    )


def _build_examples_form_composer_demo(repo_path: str):
    app_path = os.path.join(
        repo_path,
        "examples",
        "form_composer_demo",
    )
    print(f"[blue]Building '{app_path}'[/blue]")

    # Set env var for `custom_validators.js`
    from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME

    data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME, "dynamic")
    set_custom_validators_js_env_var(data_path)
    set_custom_triggers_js_env_var(data_path)

    # Build Review UI for the application
    build_custom_bundle(
        app_path,
        force_rebuild=True,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        app_path,
        force_rebuild=True,
        webapp_name="webapp",
        build_command="dev",
    )


def _build_generators_form_composer(repo_path: str):
    app_path = os.path.join(
        repo_path,
        "mephisto",
        "generators",
        "form_composer",
    )
    print(f"[blue]Building '{app_path}'[/blue]")

    # Set env var for `custom_validators.js`
    from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME

    data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME)
    set_custom_validators_js_env_var(data_path)
    set_custom_triggers_js_env_var(data_path)

    # Build Review UI for the application
    build_custom_bundle(
        app_path,
        force_rebuild=True,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        app_path,
        force_rebuild=True,
        webapp_name="webapp",
        build_command="build",
    )


def _build_review_app(repo_path: str):
    app_path = os.path.join(
        repo_path,
        "mephisto",
        "review_app",
    )
    print(f"[blue]Building '{app_path}'[/blue]")
    build_custom_bundle(
        app_path,
        force_rebuild=True,
        webapp_name="client",
        build_command="build",
    )


def _build_packages_mephisto_task_multipart(repo_path: str):
    webapp_path = os.path.join(repo_path, "packages")
    print(f"[blue]Building '{webapp_path}/mephisto-task-multipart'[/blue]")
    build_custom_bundle(
        webapp_path,
        force_rebuild=True,
        webapp_name="mephisto-task-multipart",
        build_command="build",
    )


def _build_packages_react_form_composer(repo_path: str):
    webapp_path = os.path.join(repo_path, "packages")
    print(f"[blue]Building '{webapp_path}/react-form-composer'[/blue]")
    build_custom_bundle(
        webapp_path,
        force_rebuild=True,
        webapp_name="react-form-composer",
        build_command="build",
    )


def _build(repo_path: str):
    print("[blue]Started building web apps[/blue]")
    _build_packages_mephisto_task_multipart(repo_path)
    _build_packages_react_form_composer(repo_path)
    _build_examples_form_composer_demo(repo_path)
    _build_generators_form_composer(repo_path)
    _build_review_app(repo_path)
    print("[green]Finished building web apps successfully![/green]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scripts")
    parser.add_argument("form_composer")
    parser.add_argument("rebuild_all_apps")
    parser.add_argument("--rebuild-package-locks", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    repo_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    _clean(repo_path, remove_package_locks=args.rebuild_package_locks)
    _build(repo_path)


if __name__ == "__main__":
    main()
