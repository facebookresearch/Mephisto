#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.core.utils import get_crowd_provider_from_type

from typing import List, Optional, Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup


class Qualification:
    """Simple convenience wrapper for Qualifications in the data model"""

    def __init__(self, db: "MephistoDB", db_id: str):
        self.db_id: str = db_id
        self.db: "MephistoDB" = db
        row = db.get_qualification(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.qualification_name: str = row["qualification_name"]


class GrantedQualification:
    """Convenience wrapper for tracking granted qualifications"""

    def __init__(self, db: "MephistoDB", qualification_id: str, worker_id: str):
        self.db: "MephistoDB" = db
        row = db.get_granted_qualification(qualification_id, worker_id)
        assert row is not None, f"Granted qualification did not exist in given db"
        self.worker_id: str = row["worker_id"]
        self.qualification_id: str = row["qualification_id"]
        self.value: str = row["value"]
