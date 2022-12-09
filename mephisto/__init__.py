#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
.. include:: README.md
"""
__docformat__ = "restructuredtext"

from mephisto.operations.registry import fill_registries
from mephisto.operations.config_handler import init_config
from mephisto.operations.hydra_config import initialize_named_configs

import os

here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, "VERSION")) as version_file:
        __version__ = version_file.read().strip()
except Exception:
    __version__ = "no_version_file"

init_config()
fill_registries()
initialize_named_configs()
