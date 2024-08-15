#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.providers.inhouse.inhouse_datastore import InhouseDatastore


def export_datastore(
    datastore: "InhouseDatastore",
    mephisto_db_data: dict,
    task_run_ids: Optional[List[str]] = None,
    **kwargs,
) -> dict:
    """Logic of collecting export data from Inhouse datastore"""
    return {}
