#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.requester import Requester


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


def ensure_user_confirm(display_text, skip_input=False) -> None:
    """
    Helper to provide the flow for having a user confirm a specific occurrence
    before it happens. skip_input will make this method return without
    checking, which is useful for automated scripts
    """
    if skip_input:
        return
    res = input(f'{display_text}\nEnter "n" to exit and anything else to continue:')
    if res == "n":
        raise SystemExit(0)
    return


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
