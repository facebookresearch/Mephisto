#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from mephisto.core.registry import fill_registries
from mephisto.core.config_handler import init_config

__version__ = "0.1.0"

init_config()
fill_registries()
