#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mephisto.abstractions.architects.router as router_module
import os
import sh
import shutil
import shlex
import subprocess
import json

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun

ROUTER_ROOT_DIR = os.path.dirname(router_module.__file__)
SERVER_SOURCE_ROOT = os.path.join(ROUTER_ROOT_DIR, "deploy")
CROWD_SOURCE_PATH = "static/wrap_crowd_source.js"
TASK_CONFIG_PATH = "static/task_config.json"


def can_build(build_dir: str, task_run: "TaskRun") -> bool:
    """Determine if the build dir is properly formatted for
    being able to have the router built within. This is a
    validation step that should be run before build_router.
    """
    # TODO(#97) incorporate this step into the blueprint
    # task builder test, as once the task is built, it
    # should be able to have the server build as well.
    # TODO(#97) actually implement this when the full build
    # process for the router is decided
    return True


def install_router_files() -> None:
    """
    Create a new build including the node_modules
    """
    return_dir = os.getcwd()
    os.chdir(SERVER_SOURCE_ROOT)

    packages_installed = subprocess.call(["npm", "install"])
    if packages_installed != 0:
        raise Exception(
            "please make sure npm is installed, otherwise view "
            "the above error for more info."
        )
    os.chdir(return_dir)


def build_router(build_dir: str, task_run: "TaskRun") -> str:
    """
    Copy expected files from the router source into the build dir,
    using existing files in the build dir as replacements for the
    defaults if available
    """
    install_router_files()

    server_source_directory_path = SERVER_SOURCE_ROOT
    local_server_directory_path = os.path.join(build_dir, "router")

    # Delete old server files
    sh.rm(shlex.split("-rf " + local_server_directory_path))

    # Copy over a clean copy into the server directory
    shutil.copytree(server_source_directory_path, local_server_directory_path)

    # Copy the required wrap crowd source path
    local_crowd_source_path = os.path.join(
        local_server_directory_path, CROWD_SOURCE_PATH
    )
    crowd_provider = task_run.get_provider()
    shutil.copy2(crowd_provider.get_wrapper_js_path(), local_crowd_source_path)

    # Copy the task_run's json configuration
    local_task_config_path = os.path.join(local_server_directory_path, TASK_CONFIG_PATH)
    blueprint = task_run.get_blueprint()
    with open(local_task_config_path, "w+") as task_fp:
        json.dump(blueprint.get_frontend_args(), task_fp)

    # Consolidate task files as defined by the task
    TaskBuilderClass = blueprint.TaskBuilderClass
    task_builder = TaskBuilderClass(task_run, task_run.args)

    task_builder.build_in_dir(local_server_directory_path)

    return local_server_directory_path
