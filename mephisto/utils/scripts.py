#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.tools.scripts import *
import warnings

warnings.warn(
    "Import of script tools from `mephisto.utils` is going away soon. "
    "Please replace all of your imports from mephisto.utils.scripts "
    "to mephisto.tools.scripts ",
    PendingDeprecationWarning,
)
