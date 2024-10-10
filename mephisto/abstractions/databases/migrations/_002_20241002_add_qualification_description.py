#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
List of changes:
1. Add `description` field into `qualifications` table
"""


ADD_QUALIFICATION_DESCRIPTION = """
    ALTER TABLE qualifications ADD COLUMN description CHAR(500);
"""
