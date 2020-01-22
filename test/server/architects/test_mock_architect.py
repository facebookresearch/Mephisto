#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from typing import Type, ClassVar
from mephisto.data_model.test.architect_tester import ArchitectTests
from mephisto.server.architects.mock_architect import MockArchitect, MOCK_DEPLOY_URL

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.architect import Architect
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.server.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.server.blueprints.mock.mock_task_builder import MockTaskBuilder
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner

from mephisto.core.argparse_parser import get_default_arg_dict

class MockArchitectTests(ArchitectTests):
    """
    Runs architect tests on the mock class. Tests the general architect interface is
    still working properly, and that the tests are correctly operating.
    """

    ArchitectClass: Type[Architect] = MockArchitect
    db: MephistoDB
    data_dir: str
    build_dir: str

    curr_architect: MockArchitect

    warned_about_setup = False

    def get_architect(self) -> MockArchitect:
        """
        For testing, we need to be able to examine the architect to be sure that
        the correct calls have been made
        """
        opts = get_default_arg_dict(MockArchitect)
        self.curr_architect = MockArchitect(self.db, opts, self.task_run, self.build_dir)
        return self.curr_architect

    def server_is_prepared(self, build_dir: str) -> bool:
        """Mock architect is prepared when we say it was"""
        return self.curr_architect.prepared

    def server_is_cleaned(self, build_dir: str) -> bool:
        """Mock architect is cleaned when we say it was"""
        return self.curr_architect.cleaned

    def server_is_up(self, url: str) -> bool:
        """pretend to ping the url to see if anything is running"""
        self.assertIn(MOCK_DEPLOY_URL, url, "Not using the mock url with MockArchitect")
        return self.curr_architect.deployed and not self.curr_architect.did_shutdown

    def server_is_shutdown(self) -> bool:
        """Note that the server is down"""
        return self.curr_architect.did_shutdown


if __name__ == "__main__":
    unittest.main()
