#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.utils import db as db_utils


def export_datastore(
    datastore: "MTurkDatastore",
    mephisto_db_data: dict,
    task_run_ids: Optional[List[str]] = None,
    **kwargs,
) -> dict:
    """Logic of collecting export data from MTurk datastore"""

    dump_data = db_utils.db_or_datastore_to_dict(datastore)

    if not task_run_ids:
        # Exporting the entire DB
        return dump_data

    tables_with_task_run_relations = [
        "run_mappings",
        "runs",
    ]

    for table_name in tables_with_task_run_relations:
        table_rows = db_utils.select_rows_by_list_of_field_values(
            datastore,
            table_name,
            ["run_id"],
            [task_run_ids],
        )
        runs_table_data = db_utils.serialize_data_for_table(table_rows)
        dump_data[table_name] = runs_table_data

    # Find and serialize `hits`
    hit_ids = list(set(filter(bool, [i["hit_id"] for i in dump_data["run_mappings"]])))
    hit_rows = db_utils.select_rows_by_list_of_field_values(
        datastore,
        "hits",
        ["hit_id"],
        [hit_ids],
    )
    dump_data["hits"] = db_utils.serialize_data_for_table(hit_rows)

    # Find and serialize `qualifications`
    qualification_names = [i["qualification_name"] for i in mephisto_db_data["qualifications"]]
    if qualification_names:
        qualification_rows = db_utils.select_rows_by_list_of_field_values(
            datastore,
            "qualifications",
            ["qualification_name"],
            [qualification_names],
        )
    else:
        qualification_rows = db_utils.select_all_table_rows(datastore, "qualifications")
    dump_data["qualifications"] = db_utils.serialize_data_for_table(qualification_rows)

    return dump_data
