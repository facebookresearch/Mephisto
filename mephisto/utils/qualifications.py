#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional, Dict, TYPE_CHECKING, Any
from mephisto.data_model.qualification import (
    QUAL_EXISTS,
    QUAL_NOT_EXIST,
    COMPARATOR_OPERATIONS,
    SUPPORTED_COMPARATORS,
    QUAL_GREATER,
    QUAL_LESS,
    QUAL_GREATER_EQUAL,
    QUAL_LESS_EQUAL,
    QUAL_IN_LIST,
    QUAL_NOT_IN_LIST,
)

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.worker import Worker

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


def worker_is_qualified(worker: "Worker", qualifications: List[Dict[str, Any]]):
    db = worker.db
    for qualification in qualifications:
        qual_name = qualification["qualification_name"]
        qual_objs = db.find_qualifications(qual_name)
        if len(qual_objs) == 0:
            logger.warning(
                f"Expected to create qualification for {qual_name}, but none found... skipping."
            )
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
        from mephisto.operations.registry import get_valid_provider_types

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


def find_or_create_qualification(db: "MephistoDB", qualification_name: str) -> str:
    """
    Ensure the given qualification exists in the db,
    creating it if it doesn't already. Returns the id
    """
    found_qualifications = db.find_qualifications(qualification_name)
    if len(found_qualifications) == 0:
        return db.make_qualification(qualification_name)
    else:
        return found_qualifications[0].db_id
