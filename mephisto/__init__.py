#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from mephisto.operations.registry import fill_registries
from mephisto.operations.config_handler import init_config
from mephisto.operations.hydra_config import initialize_named_configs
from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)

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
logger.warning(
    "\u001b[31;1m"
    "Mephisto Version 0.4.0 has breaking changes for user scripts due "
    "to the Hydra 1.1 upgrade. This may prevent scripts from launching. "
    "See https://github.com/facebookresearch/Mephisto/issues/529 for "
    "remediation details."
    "\u001b[0m"
)
