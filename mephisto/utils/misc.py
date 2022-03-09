#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.requester import Requester


def get_mock_requester(db) -> "Requester":
    """Get or create a mock requester to use for test tasks"""
    mock_requesters = db.find_requesters(provider_type="mock")
    if len(mock_requesters) == 0:
        db.new_requester("MOCK_REQUESTER", "mock")
    mock_requesters = db.find_requesters(provider_type="mock")
    return mock_requesters[0]


def find_or_create_qualification(db, qualification_name) -> str:
    """
    Ensure the given qualification exists in the db,
    creating it if it doesn't already. Returns the id
    """
    found_qualifications = db.find_qualifications(qualification_name)
    if len(found_qualifications) == 0:
        return db.make_qualification(qualification_name)
    else:
        return found_qualifications[0].db_id
