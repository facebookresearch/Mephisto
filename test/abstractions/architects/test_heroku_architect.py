#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import os
import pytest

from typing import Type, ClassVar, Optional
from mephisto.abstractions.test.architect_tester import ArchitectTests
from mephisto.abstractions.architects.heroku_architect import (
    HerokuArchitect,
    HerokuArchitectArgs,
)

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.architect import Architect
from mephisto.data_model.constants.assignment_state import AssignmentState

from omegaconf import OmegaConf
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockSharedState

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
        """We need to have the architect saved locally to be sure to shutdown"""
        arch_args = HerokuArchitectArgs(heroku_team=None, use_hobby=False)
        args = OmegaConf.structured(MephistoConfig(architect=arch_args))
        self.curr_architect = self.ArchitectClass(
            self.db, args, MockSharedState(), self.task_run, self.build_dir
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

    @pytest.mark.req_creds
    def test_prepare_cleanup(self) -> None:
        """Test deploying the server, and shutting it down"""
        super().test_prepare_cleanup()

    @pytest.mark.req_creds
    def test_deploy_shutdown(self) -> None:
        """Test deploying the server, and shutting it down"""
        super().test_deploy_shutdown()

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
