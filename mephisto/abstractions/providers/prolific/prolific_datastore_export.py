#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.utils import db as db_utils


def export_datastore(
    datastore: "ProlificDatastore",
    mephisto_db_data: dict,
    task_run_ids: Optional[List[str]] = None,
    **kwargs,
) -> dict:
    """Logic of collecting export data from Prolific datastore"""

    dump_data = db_utils.db_or_datastore_to_dict(datastore)

    if not task_run_ids:
        # Exporting the entire DB
        return dump_data

    tables_with_task_run_relations = [
        "qualifications",
        "run_mappings",
        "runs",
        "studies",
        "units",
    ]

    for table_name in tables_with_task_run_relations:
        table_rows = db_utils.select_rows_from_table_related_to_task_run(
            datastore, table_name, task_run_ids,
        )
        runs_table_data = db_utils.serialize_data_for_table(table_rows)
        dump_data[table_name] = runs_table_data

    # Find and serialize `submissions`
    study_ids = list(set(filter(bool, [i["prolific_study_id"] for i in dump_data["studies"]])))
    submission_rows = db_utils.select_rows_by_list_of_field_values(
        datastore, "submissions", ["prolific_study_id"], [study_ids],
    )
    dump_data["submissions"] = db_utils.serialize_data_for_table(submission_rows)

    # Find and serialize `participant_groups`
    participant_group_ids = list(set(filter(bool, [
        i["prolific_participant_group_id"] for i in dump_data["qualifications"]
    ])))
    participant_group_rows = db_utils.select_rows_by_list_of_field_values(
        datastore, "participant_groups", ["prolific_participant_group_id"], [participant_group_ids],
    )
    dump_data["participant_groups"] = db_utils.serialize_data_for_table(participant_group_rows)

    # Find and serialize `workers`
    worker_ids = [i["worker_name"] for i in mephisto_db_data["workers"]]
    if worker_ids:
        worker_rows = db_utils.select_rows_by_list_of_field_values(
            datastore, "workers", ["worker_id"], [worker_ids],
        )
    else:
        worker_rows = db_utils.select_all_table_rows(datastore, "workers")
    dump_data["workers"] = db_utils.serialize_data_for_table(worker_rows)

    return dump_data
