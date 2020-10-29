#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.mturk_sandbox.sandbox_mturk_agent import *
import warnings

warnings.warn(
    "Import of provider content from `mephisto.providers` is going away soon. "
    "Please replace all of your imports from mephisto.providers "
    "to mephisto.abstractions.providers. ",
    PendingDeprecationWarning,
)
