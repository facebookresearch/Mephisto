#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from datetime import datetime

import pytest
from dateutil.parser import ParserError
from dateutil.tz import tzlocal

from mephisto.utils.misc import serialize_date_to_python


@pytest.mark.utils
class TestUtilsMisc(unittest.TestCase):
    def test_serialize_date_to_python(self, *args):
        common_datetime_string = "2001-01-01 01:01:01.000"
        common_date_string = "2001-01-01"
        iso8601_datetime_string = "2002-02-02T02:02:02.000Z"
        unix_timestamp_string = 1046660583000
        wrong_date_string = "wrong_date"

        python_datetime_1 = serialize_date_to_python(common_datetime_string)
        self.assertEqual(python_datetime_1, datetime(2001, 1, 1, 1, 1, 1))

        python_datetime_2 = serialize_date_to_python(common_date_string)
        self.assertEqual(python_datetime_2, datetime(2001, 1, 1, 0, 0, 0))

        python_datetime_3 = serialize_date_to_python(iso8601_datetime_string)
        self.assertEqual(python_datetime_3, datetime(2002, 2, 2, 2, 2, 2, tzinfo=tzlocal()))

        python_datetime_4 = serialize_date_to_python(unix_timestamp_string)
        self.assertEqual(python_datetime_4, datetime(2003, 3, 3, 3, 3, 3))

        with self.assertRaises(ParserError) as cm:
            serialize_date_to_python(wrong_date_string)
        self.assertEqual(cm.exception.__str__(), f"Unknown string format: {wrong_date_string}")
