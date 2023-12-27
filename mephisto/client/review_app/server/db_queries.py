#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.abstractions.databases.local_database import nonesafe_int
from mephisto.abstractions.databases.local_database import StringIDRow


def find_units(
    db,
    task_id: int,
    statuses: Optional[List[str]] = None,
    debug: bool = False,
) -> List[StringIDRow]:
    with db.table_access_condition:
        conn = db._get_connection()

        params = []

        task_query = "task_id = ?" if task_id else ""
        if task_id:
            params.append(nonesafe_int(task_id))

        statuses_string = ",".join([f"'{s}'" for s in statuses])
        status_query = f"status IN ({statuses_string})" if statuses else ""

        joined_queries = " AND ".join(list(filter(bool, [task_query, status_query])))

        where_query = f"WHERE {joined_queries}" if joined_queries else ""

        c = conn.cursor()
        c.execute(
            f"""
            SELECT * from units
            {where_query};
            """,
            params,
        )
        rows = c.fetchall()

        return rows
