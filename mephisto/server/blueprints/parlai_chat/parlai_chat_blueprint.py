#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import *
import warnings

warnings.warn(
    "Import of blueprints from `mephisto.server.blueprints` is going away soon. "
    "Please replace all of your imports from mephisto.server.blueprints "
    "to mephisto.abstractions.blueprints ",
    PendingDeprecationWarning,
)
