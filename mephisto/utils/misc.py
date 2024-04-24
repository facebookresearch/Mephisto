#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import datetime
from typing import Any

from dateutil.parser import parse as dateutil_parse


def serialize_date_to_python(value: Any) -> datetime:
    """Convert string dates or integer timestamps into Python datetime format"""
    # If integer timestamp
    if isinstance(value, int):
        timestamp_is_in_msec = len(str(value)) == 13
        datetime_value = datetime.fromtimestamp(
            value / 1000 if timestamp_is_in_msec else value
        )
    # If datetime string
    else:
        datetime_value = dateutil_parse(str(value))

    return datetime_value
