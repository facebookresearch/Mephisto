#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskBuilder

from distutils.dir_util import copy_tree
import os
import shutil


class StaticReactTaskBuilder(TaskBuilder):
    """
    Builder for a static task, puts required files into
    the server directory for deployment.
    """

    BUILT_FILE = "done.built"
    BUILT_MESSAGE = "built!"

    def build_in_dir(self, build_dir: str):
        """Build the frontend if it doesn't exist, then copy into the server directory"""
        target_resource_dir = os.path.join(build_dir, "static")

        # If any additional task files are required via a source_dir, copy those as well
        extra_dir_path = self.args.blueprint.get("extra_source_dir", None)
        if extra_dir_path is not None:
            extra_dir_path = os.path.expanduser(extra_dir_path)
            copy_tree(extra_dir_path, target_resource_dir)

        # Copy the built core and the given task file to the target path
        use_bundle = os.path.expanduser(self.args.blueprint.task_source)
        target_path = os.path.join(target_resource_dir, "bundle.js")

        should_link_task_source = self.args.blueprint.get("link_task_source", False)
        if should_link_task_source:
            os.symlink(use_bundle, target_path)
        else:
            shutil.copy2(use_bundle, target_path)

        # Write a built file confirmation
        with open(os.path.join(build_dir, self.BUILT_FILE), "w+") as built_file:
            built_file.write(self.BUILT_MESSAGE)
