#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)

from typing import Optional, Mapping, TYPE_CHECKING, Any


if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


QUAL_GREATER = "GreaterThan"
QUAL_GREATER_EQUAL = "GreaterThanOrEqualTo"
QUAL_LESS = "LessThan"
QUAL_LESS_EQUAL = "LessThanOrEqualTo"
QUAL_EQUAL = "EqualTo"
QUAL_NOT_EQUAL = "NotEqualTo"
QUAL_EXISTS = "Exists"
QUAL_NOT_EXIST = "DoesNotExist"
QUAL_IN_LIST = "In"
QUAL_NOT_IN_LIST = "NotIn"

SUPPORTED_COMPARATORS = [
    QUAL_GREATER,
    QUAL_GREATER_EQUAL,
    QUAL_LESS,
    QUAL_LESS_EQUAL,
    QUAL_EQUAL,
    QUAL_NOT_EQUAL,
    QUAL_EXISTS,
    QUAL_NOT_EXIST,
    QUAL_IN_LIST,
    QUAL_NOT_IN_LIST,
]

COMPARATOR_OPERATIONS = {
    QUAL_GREATER: lambda x, y: x > y,
    QUAL_GREATER_EQUAL: lambda x, y: x >= y,
    QUAL_LESS: lambda x, y: x < y,
    QUAL_LESS_EQUAL: lambda x, y: x <= y,
    QUAL_EQUAL: lambda x, y: x == y,
    QUAL_NOT_EQUAL: lambda x, y: not x == y,
    QUAL_IN_LIST: lambda x, y: x in y,
    QUAL_NOT_IN_LIST: lambda x, y: x not in y,
}


class Qualification(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    """Simple convenience wrapper for Qualifications in the data model"""

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct Qualification and data model access via Qualification(db, id) is "
                "now deprecated in favor of calling Qualification.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_qualification(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["qualification_id"]
        self.qualification_name: str = row["qualification_name"]


class GrantedQualification:
    """Convenience wrapper for tracking granted qualifications"""

    def __init__(
        self,
        db: "MephistoDB",
        qualification_id: str,
        worker_id: str,
        row: Optional[Mapping[str, Any]] = None,
    ):
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_granted_qualification(qualification_id, worker_id)
        assert row is not None, f"Granted qualification did not exist in given db"
        self.worker_id: str = row["worker_id"]
        self.qualification_id: str = row["qualification_id"]
        self.value: str = row["value"]
