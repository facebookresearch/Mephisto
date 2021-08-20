#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from typing import Set

_seen_logs: Set[str] = set()


def warn_once(msg: str) -> None:
    """
    Log a warning, but only once.

    :param str msg: Message to display
    """
    global _seen_logs
    if msg not in _seen_logs:
        _seen_logs.add(msg)
        logging.warn(msg)
