#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile
import sh
import shlex
import subprocess

from typing import Type, ClassVar, Optional
from mephisto.data_model.test.architect_tester import ArchitectTests
from mephisto.server.architects.heroku_architect import HerokuArchitect

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.architect import Architect
from mephisto.data_model.assignment_state import AssignmentState


# TODO(#104) these tests should be marked as nightly's rather than on every run?
# Maybe with some kind of LONG TEST flag? Investigate
class HerokuArchitectTests(ArchitectTests):
    """
    Runs architect tests on Heroku. Ensures that deploying to heroku still
    works and nothing has broken it.
    """

    ArchitectClass: Type[Architect] = HerokuArchitect
    db: MephistoDB
    data_dir: str
    build_dir: str
    curr_architect: Optional[HerokuArchitect] = None

    def get_architect(self) -> HerokuArchitect:
        """We need to specify that the architect is launching on localhost for testing"""
        opts = {"heroku_team": None, "use_hobby": False}
        self.curr_architect = HerokuArchitect(
            self.db, opts, self.task_run, self.build_dir
        )
        return self.curr_architect

    def server_is_prepared(self, build_dir: str) -> bool:
        """Ensure the build directory exists"""
        assert self.curr_architect is not None, "No architect to check"
        return os.path.exists(build_dir)

    def server_is_cleaned(self, build_dir: str) -> bool:
        """Ensure the build directory is gone"""
        assert self.curr_architect is not None, "No architect to check"
        return self.curr_architect.build_is_clean()

    def server_is_shutdown(self) -> bool:
        """Ensure process is no longer running"""
        assert self.curr_architect is not None, "No architect to check"
        return not self.curr_architect.server_is_running()

    # TODO(#102) maybe a test where we need to re-instance an architect?

    def tearDown(self) -> None:
        """Overrides teardown to kill the server if it exists"""
        super().tearDown()
        if self.curr_architect is not None:
            if self.curr_architect.server_is_running():
                self.curr_architect.shutdown()
            if not self.curr_architect.build_is_clean():
                self.curr_architect.cleanup()


if __name__ == "__main__":
    unittest.main()
