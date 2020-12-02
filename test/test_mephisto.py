#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto import __version__
from mephisto.operations.utils import get_root_dir
import os


def test_version():
    with open(os.path.join(get_root_dir(), "mephisto", "VERSION")) as version_file:
        version = version_file.read().strip()
    assert __version__ == version
