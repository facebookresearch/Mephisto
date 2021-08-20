#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.tools.misc import warn_once
from mephisto.operations.registry import (
    get_crowd_provider_from_type,
    get_valid_provider_types,
)
from mephisto.data_model.db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)

from typing import List, Optional, Mapping, Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.worker import Worker
    from argparse import _ArgumentGroup as ArgumentGroup

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


def worker_is_qualified(worker: "Worker", qualifications: List[Dict[str, Any]]):
    db = worker.db
    for qualification in qualifications:
        qual_name = qualification["qualification_name"]
        qual_objs = db.find_qualifications(qual_name)
        if len(qual_objs) == 0:
            # TODO warn users of missing qualification object
            continue
        qual_obj = qual_objs[0]
        granted_quals = db.check_granted_qualifications(
            qualification_id=qual_obj.db_id, worker_id=worker.db_id
        )
        comp = qualification["comparator"]
        compare_value = qualification["value"]
        if comp == QUAL_EXISTS and len(granted_quals) == 0:
            return False
        elif comp == QUAL_NOT_EXIST and len(granted_quals) != 0:
            return False
        elif comp in [QUAL_EXISTS, QUAL_NOT_EXIST]:
            continue
        else:
            granted_qual = granted_quals[0]
            if not COMPARATOR_OPERATIONS[comp](granted_qual.value, compare_value):
                return False
    return True


def as_valid_qualification_dict(qual_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check to ensure that a qualification dict properly checks
    against a Mephisto qualification
    """
    required_keys = [
        "qualification_name",
        "comparator",
        "value",
        "applicable_providers",
    ]
    for key in required_keys:
        if key not in qual_dict:
            raise AssertionError(
                f"Required key {key} not in qualification dict {qual_dict}"
            )

    qual_name = qual_dict["qualification_name"]
    if type(qual_name) is not str or len(qual_name) == 0:
        raise AssertionError(
            f"Qualification name '{qual_name}' is not a string with length > 0"
        )

    comparator = qual_dict["comparator"]
    if comparator not in SUPPORTED_COMPARATORS:
        raise AssertionError(
            f"Qualification comparator '{comparator}' not in supported list: {SUPPORTED_COMPARATORS}'"
        )

    value = qual_dict["value"]

    if (
        comparator in [QUAL_GREATER, QUAL_LESS, QUAL_GREATER_EQUAL, QUAL_LESS_EQUAL]
        and type(value) != int
    ):
        raise AssertionError(
            f"Value {value} is not valid for comparator {comparator}, must be an int"
        )

    if comparator in [QUAL_EXISTS, QUAL_NOT_EXIST] and value is not None:
        raise AssertionError(
            f"Value {value} is not valid for comparator {comparator}, must be None"
        )

    if comparator in [QUAL_IN_LIST, QUAL_NOT_IN_LIST] and type(value) != list:
        raise AssertionError(
            f"Value {value} is not valid for comparator {comparator}, must be a list"
        )

    if qual_dict["applicable_providers"] is not None:
        assert (
            type(qual_dict["applicable_providers"]) == list
        ), "Applicable providers must be a string list of providers or none."
        valid_providers = get_valid_provider_types()
        for provider_name in qual_dict["applicable_providers"]:
            assert (
                provider_name in valid_providers
            ), f"Noted applicable provider name {provider_name} not in list of usable providers: {valid_providers}"

    return qual_dict


def make_qualification_dict(
    qualification_name: str,
    comparator: str,
    value: Any,
    applicable_providers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a qualification dict to pass to an operator as part
    of extra_args
    """
    qual_dict = {
        "qualification_name": qualification_name,
        "comparator": comparator,
        "value": value,
        "applicable_providers": applicable_providers,
    }
    return as_valid_qualification_dict(qual_dict)


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
            warn_once(
                "Direct Qualification and data model access via Qualification(db, id) is "
                "now deprecated in favor of calling Qualification.get(db, id). "
                "Please update callsites, as we'll remove this compatibility "
                "in the 1.0 release, targetting October 2021",
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
