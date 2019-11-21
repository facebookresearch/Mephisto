#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mephisto.server.architects.router as router_module
import os
import sh
import shutil
import shlex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun

ROUTER_ROOT_DIR = os.path.dirname(router_module.__file__)
SERVER_SOURCE_ROOT = os.path.join(ROUTER_ROOT_DIR, 'deploy')

def can_build(build_dir: str, task_run: 'TaskRun') -> bool:
    """Determine if the build dir is properly formatted for
    being able to have the router built within. This is a
    validation step that should be run before build_router.
    """
    # TODO incorporate this step into the blueprint
    # task builder test, as once the task is built, it
    # should be able to have the server build as well.
    # TODO actually implement this when the full build
    # process for the router is decided
    return True

def build_router(build_dir: str, task_run: 'TaskRun') -> str:
    """
    Copy expected files from the router source into the build dir,
    using existing files in the build dir as replacements for the
    defaults if available
    """
    server_source_directory_path = SERVER_SOURCE_ROOT
    local_server_directory_path = os.path.join(
        build_dir, 'router'
    )

    # Delete old server files
    sh.rm(shlex.split('-rf ' + local_server_directory_path))

    # Copy over a clean copy into the server directory
    shutil.copytree(server_source_directory_path, local_server_directory_path)

    # Consolidate task files
    # TODO any required management for task-related deployment files
    # (html/static/task config)
    # for file_path in task_files_to_copy:
    #     try:
    #         shutil.copy2(file_path, task_directory_path)
    #     except IsADirectoryError:  # noqa: F821 we don't support python2
    #         dir_name = os.path.basename(os.path.normpath(file_path))
    #         shutil.copytree(file_path, os.path.join(task_directory_path, dir_name))
    #     except FileNotFoundError:  # noqa: F821 we don't support python2
    #         pass

    return local_server_directory_path
