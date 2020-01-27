#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from mephisto.data_model.architect import Architect
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB
    from argparse import _ArgumentGroup as ArgumentGroup

MOCK_DEPLOY_URL = "MOCK_DEPLOY_URL"


class MockArchitect(Architect):
    """
    Provides methods for setting up a server somewhere and deploying tasks
    onto that server.
    """

    def __init__(
        self,
        db: "MephistoDB",
        opts: Dict[str, str],
        task_run: "TaskRun",
        build_dir_root: str,
    ):
        """Create an architect for use in testing"""
        self.task_run = task_run
        self.build_dir = build_dir_root
        self.task_run_id = task_run.db_id
        # TODO track state in parent class?
        self.prepared = False
        self.deployed = False
        self.cleaned = False
        self.did_shutdown = False

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        MockArchitects don't have any arguments (yet)
        """
        super(MockArchitect, cls).add_args_to_group(group)
        return

    def prepare(self) -> str:
        """Mark the preparation call"""
        self.prepared = True
        built_dir = os.path.join(
            self.build_dir, "mock_build_{}".format(self.task_run_id)
        )
        os.makedirs(built_dir)
        return built_dir

    def deploy(self) -> str:
        """Mark the deployed call"""
        self.deployed = True
        return MOCK_DEPLOY_URL

    def cleanup(self) -> None:
        """Mark the cleanup call"""
        self.cleaned = True

    def shutdown(self) -> None:
        """Mark the shutdown call"""
        self.did_shutdown = True
