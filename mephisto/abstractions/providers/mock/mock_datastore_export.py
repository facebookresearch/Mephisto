#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.utils import db as db_utils


def export_datastore(
    datastore: "MockDatastore",
    mephisto_db_data: dict,
    task_run_ids: Optional[List[str]] = None,
    **kwargs,
) -> dict:
    """Logic of collecting export data from Mock datastore"""

    dump_data = db_utils.db_or_datastore_to_dict(datastore)

    if not task_run_ids:
        # Exporting the entire DB
        return dump_data

    # Find and serialize `units`
    unit_ids = [i["unit_id"] for i in mephisto_db_data["units"]]
    unit_rows = db_utils.select_rows_by_list_of_field_values(
        datastore, "units", ["unit_id"], [unit_ids],
    )
    dump_data["units"] = db_utils.serialize_data_for_table(unit_rows)

    # Find and serialize `workers`
    worker_ids = [i["worker_id"] for i in mephisto_db_data["workers"]]
    workers_rows = db_utils.select_rows_by_list_of_field_values(
        datastore, "workers", ["worker_id"], [worker_ids],
    )
    dump_data["workers"] = db_utils.serialize_data_for_table(workers_rows)

    return dump_data
