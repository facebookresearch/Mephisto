#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile

from mephisto.abstractions.databases.local_database import LocalMephistoDB

# from ...examples.simple_static_task import
# from ...examples.static_react_task import

from hydra.experimental import initialize, compose


class TestExampleScripts(unittest.TestCase):
    """
    Unit testing for our example scripts

    Launches tasks from the main functions of the scripts, and ensures
    it's possible to register and then disconnect agents and shutdown without
    any errors.
    """

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_simple_static_task(self) -> None:
        from mephisto.examples.simple_static_task.static_test_script import (
            TASK_DIRECTORY,
        )
        from mephisto.examples.simple_static_task.static_test_script import (
            main as static_main,
        )

        with initialize(config_path="./"):
            # config is relative to a module
            cfg = compose(
                config_name="scriptconfig",
                overrides=[
                    "conf=simple_static_task",
                    f"+mephisto.datapath={self.data_dir}",
                ],
            )
            static_main(cfg)

            assert False


if __name__ == "__main__":
    unittest.main()
