#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskBuilder


class EmptyStaticTaskBuilder(TaskBuilder):
    """
    Abstract class for a task builder for static tasks
    """

    def build_in_dir(self, build_dir: str):
        """Build the frontend if it doesn't exist, then copy into the server directory"""
        raise AssertionError(
            "Classes that extend the abstract StaticBlueprint must define a custom "
            "TaskBuilder class that pulls the correct frontend together. Examples "
            "can be seen in the static_react_task and static_html_task folders. "
            "Note that extra static content will be provided in `args.blueprint.extra_source_dir` "
        )
