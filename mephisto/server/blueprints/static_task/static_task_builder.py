#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskBuilder

from distutils.dir_util import copy_tree
import os
import time
import sh
import shutil
import subprocess

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Assignment

STATIC_TASK_DIR = os.path.dirname(__file__)
FRONTEND_SOURCE_DIR = os.path.join(STATIC_TASK_DIR, "source")
FRONTEND_BUILD_DIR = os.path.join(FRONTEND_SOURCE_DIR, "build")


class StaticTaskBuilder(TaskBuilder):
    """
    Builder for a static task, pulls the appropriate html,
    builds the frontend (if a build doesn't already exist),
    then puts the file into the server directory
    """

    BUILT_FILE = "done.built"
    BUILT_MESSAGE = "built!"

    def rebuild_core(self):
        """Rebuild the frontend for this task"""
        return_dir = os.getcwd()
        os.chdir(FRONTEND_SOURCE_DIR)
        if os.path.exists(FRONTEND_BUILD_DIR):
            shutil.rmtree(FRONTEND_BUILD_DIR)
        packages_installed = subprocess.call(["npm", "install"])
        if packages_installed != 0:
            raise Exception(
                "please make sure npm is installed, otherwise view "
                "the above error for more info."
            )

        webpack_complete = subprocess.call(["npm", "run", "dev"])
        if webpack_complete != 0:
            raise Exception(
                "Webpack appears to have failed to build your "
                "frontend. See the above error for more information."
            )
        os.chdir(return_dir)

    def build_in_dir(self, build_dir: str):
        """Build the frontend if it doesn't exist, then copy into the server directory"""
        # Only build this task if it hasn't already been built
        if not os.path.exists(FRONTEND_BUILD_DIR):
            self.rebuild_core()

        # Copy the built core and the given task file to the target path
        use_html_file = os.path.expanduser(self.opts["task_source"])

        target_resource_dir = os.path.join(build_dir, "static")
        file_name = os.path.basename(use_html_file)
        target_path = os.path.join(target_resource_dir, file_name)
        shutil.copy2(use_html_file, target_path)

        # Copy over the preview file as preview.html, default to the task file if none specified
        preview_file = self.opts.get("preview_source") or use_html_file
        use_preview_file = os.path.expanduser(preview_file)

        target_path = os.path.join(target_resource_dir, "preview.html")
        shutil.copy2(use_preview_file, target_path)

        # If any additional task files are required via a source_dir, copy those as well
        extra_dir_path = self.opts.get("extra_source_dir")
        if extra_dir_path is not None:
            extra_dir_path = os.path.expanduser(extra_dir_path)
            copy_tree(extra_dir_path, target_resource_dir)

        bundle_js_file = os.path.join(FRONTEND_BUILD_DIR, "bundle.js")
        target_path = os.path.join(target_resource_dir, "bundle.js")
        shutil.copy2(bundle_js_file, target_path)

        # Write a built file confirmation
        with open(os.path.join(build_dir, self.BUILT_FILE), "w+") as built_file:
            built_file.write(self.BUILT_MESSAGE)

    # TODO update test validation
    @staticmethod
    def task_dir_is_valid(task_dir: str) -> bool:
        """Mocks are always valid, we don't have any special resources"""
        return True

    # TODO failed static tasks should be requeued?
    def cleanup_assignment(self, assignment: "Assignment"):
        """Failed static tasks may need to be requeued?"""
        pass
