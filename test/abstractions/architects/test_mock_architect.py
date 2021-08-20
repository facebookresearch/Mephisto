#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from typing import Type, ClassVar
from mephisto.abstractions.test.architect_tester import ArchitectTests
from mephisto.abstractions.architects.mock_architect import (
    MockArchitect,
    MOCK_DEPLOY_URL,
)

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.architect import Architect
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.abstractions.blueprints.mock.mock_task_builder import MockTaskBuilder
from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner


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
