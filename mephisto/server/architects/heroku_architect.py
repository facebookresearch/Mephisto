#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.architects.heroku_architect import *
import warnings

warnings.warn(
    "Import of architects from `mephisto.server.architects` is going away soon. "
    "Please replace all of your imports from mephisto.server.architects. "
    "to mephisto.abstractions.architects. ",
    PendingDeprecationWarning,
)
