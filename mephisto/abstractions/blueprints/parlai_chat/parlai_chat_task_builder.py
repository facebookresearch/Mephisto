#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskBuilder

from distutils.dir_util import copy_tree
import os
import time
import sh  # type: ignore
import shutil
import subprocess

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.assignment import Assignment

PARLAI_TASK_DIR = os.path.dirname(__file__)
FRONTEND_SOURCE_DIR = os.path.join(PARLAI_TASK_DIR, "webapp")
FRONTEND_BUILD_DIR = os.path.join(FRONTEND_SOURCE_DIR, "build")

BUILT_FILE = "done.built"
CUSTOM_BUILD_DIRNAME = "_generated"


class ParlAIChatTaskBuilder(TaskBuilder):
    """
    Builder for a parlai chat task, pulls the appropriate html,
    builds the frontend (if a build doesn't already exist),
    then puts the file into the server directory
    """

    BUILT_FILE = BUILT_FILE
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

    def build_custom_bundle(self, custom_src_dir):
        """Locate all of the custom files used for a custom build, create
        a prebuild directory containing all of them, then build the
        custom source.

        Check dates to only go through this build process when files have changes
        """
        TARGET_BUILD_FILES = {
            "main.js": "src/main.js",
            "package.json": "package.json",
            "style.css": "src/style.css",
        }
        TARGET_BUILD_FOLDERS = {"components": "src/components"}

        prebuild_path = os.path.join(custom_src_dir, CUSTOM_BUILD_DIRNAME)
        build_path = os.path.join(prebuild_path, "build", "bundle.js")

        # see if we need to rebuild
        if os.path.exists(build_path):
            created_date = os.path.getmtime(build_path)
            up_to_date = True
            for fn in TARGET_BUILD_FILES.keys():
                possible_conflict = os.path.join(custom_src_dir, fn)
                if os.path.exists(possible_conflict):
                    if os.path.getmtime(possible_conflict) > created_date:
                        up_to_date = False
                        break
            for fn in TARGET_BUILD_FOLDERS.keys():
                if not up_to_date:
                    break
                possible_conflict_dir = os.path.join(custom_src_dir, fn)
                for root, dirs, files in os.walk(possible_conflict_dir):
                    if not up_to_date:
                        break
                    for fname in files:
                        path = os.path.join(root, fname)
                        if os.path.getmtime(path) > created_date:
                            up_to_date = False
                            break
                if os.path.exists(possible_conflict):
                    if os.path.getmtime(possible_conflict) > created_date:
                        up_to_date = False
                        break
            if up_to_date:
                return build_path

        # build anew
        REQUIRED_SOURCE_FILES = [
            ".babelrc",
            ".eslintrc",
            "package.json",
            "webpack.config.js",
        ]
        REQUIRED_SOURCE_DIRS = ["src"]
        if not os.path.exists(os.path.join(prebuild_path, "build")):
            os.makedirs(os.path.join(prebuild_path, "build"), exist_ok=True)

        # Copy default files
        for src_dir in REQUIRED_SOURCE_DIRS:
            src_path = os.path.join(FRONTEND_SOURCE_DIR, src_dir)
            dst_path = os.path.join(prebuild_path, src_dir)
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        for src_file in REQUIRED_SOURCE_FILES:
            src_path = os.path.join(FRONTEND_SOURCE_DIR, src_file)
            dst_path = os.path.join(prebuild_path, src_file)
            shutil.copy2(src_path, dst_path)

        # copy custom files
        for src_file in TARGET_BUILD_FILES.keys():
            src_path = os.path.join(custom_src_dir, src_file)
            if os.path.exists(src_path):
                dst_path = os.path.join(prebuild_path, TARGET_BUILD_FILES[src_file])
                shutil.copy2(src_path, dst_path)
        for src_dir in TARGET_BUILD_FOLDERS.keys():
            src_path = os.path.join(custom_src_dir, src_dir)
            dst_path = os.path.join(prebuild_path, TARGET_BUILD_FOLDERS[src_dir])
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)

        # navigate and build
        return_dir = os.getcwd()
        os.chdir(prebuild_path)
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

        # cleanup and return
        os.chdir(return_dir)
        return build_path

    def build_in_dir(self, build_dir: str):
        """Build the frontend if it doesn't exist, then copy into the server directory"""
        # Only build this task if it hasn't already been built
        if not os.path.exists(FRONTEND_BUILD_DIR):
            self.rebuild_core()

        custom_source_dir = self.args.blueprint.get("custom_source_dir", None)
        build_bundle = None
        if custom_source_dir is not None:
            custom_source_dir = os.path.expanduser(custom_source_dir)
            build_bundle = self.build_custom_bundle(custom_source_dir)

        # Copy over the preview file as preview.html, use the default if none specified
        target_resource_dir = os.path.join(build_dir, "static")
        preview_file = self.args.blueprint.get("preview_source", None)
        if preview_file is not None:
            use_preview_file = os.path.expanduser(preview_file)
            target_path = os.path.join(target_resource_dir, "preview.html")
            shutil.copy2(use_preview_file, target_path)

        # If any additional task files are required via a source_dir, copy those as well
        extra_dir_path = self.args.blueprint.get("extra_source_dir", None)
        if extra_dir_path is not None:
            extra_dir_path = os.path.expanduser(extra_dir_path)
            copy_tree(extra_dir_path, target_resource_dir)

        bundle_js_file = self.args.blueprint.get("custom_source_bundle", None)
        if bundle_js_file is None:
            if build_bundle is not None:
                bundle_js_file = build_bundle
            else:
                bundle_js_file = os.path.join(FRONTEND_BUILD_DIR, "bundle.js")
        target_path = os.path.join(target_resource_dir, "bundle.js")
        shutil.copy2(bundle_js_file, target_path)

        # Copy over the static files for this task:
        for fin_file in ["index.html", "notif.mp3"]:
            copied_static_file = os.path.join(
                FRONTEND_SOURCE_DIR, "src", "static", fin_file
            )
            target_path = os.path.join(target_resource_dir, fin_file)
            shutil.copy2(copied_static_file, target_path)

        # Write a built file confirmation
        with open(os.path.join(build_dir, self.BUILT_FILE), "w+") as built_file:
            built_file.write(self.BUILT_MESSAGE)
