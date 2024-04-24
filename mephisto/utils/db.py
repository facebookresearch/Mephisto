#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json

import random
from copy import deepcopy
from datetime import datetime
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from dateutil.parser import ParserError

from mephisto.abstractions.database import MephistoDB
from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.misc import serialize_date_to_python

SQLITE_ID_MIN = 1_000_000
SQLITE_ID_MAX = 2**63 - 1

logger = ConsoleWriter()


# --- Exceptions ---

class MephistoDBException(Exception):
    pass


class EntryAlreadyExistsException(MephistoDBException):
    db = None
    original_exc = None
    table_name = None

    def __init__(self, *args, **kwargs):
        self.db = kwargs.pop("db", None)
        self.table_name = kwargs.pop("table_name", None)
        self.original_exc = kwargs.pop("original_exc", None)
        super().__init__(*args, **kwargs)


class EntryDoesNotExistException(MephistoDBException):
    pass


# --- Functions ---

def _select_all_rows_from_table(db: "MephistoDB", table_name: str) -> List[dict]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table_name};")
        rows = c.fetchall()
        return [dict(row) for row in rows]


def _select_rows_from_table_related_to_task(
    db: "MephistoDB", table_name: str, task_ids: List[str],
) -> List[dict]:
    return select_rows_by_list_of_field_values(db, table_name, ["task_id"], [task_ids])


def select_rows_from_table_related_to_task_run(
    db: "MephistoDB", table_name: str, task_run_ids: List[str],
) -> List[dict]:
    return select_rows_by_list_of_field_values(db, table_name, ["task_run_id"], [task_run_ids])


def serialize_data_for_table(rows: List[dict]) -> List[dict]:
    serialized_data = []
    for row in rows:
        _row = dict(row)
        for field_name, field_value in _row.items():
            # SQLite dates
            if field_name.endswith("_at") or field_name.endswith("_date"):
                try:
                    python_datetime_value = serialize_date_to_python(field_value)
                except (ParserError, OverflowError):
                    logger.exception(
                        f"[red]"
                        f"Cannot convert value `{field_value}` of field `field_name` "
                        f"to Python datetime. "
                        f"It seems your DB was corrupted."
                        f"[/red]"
                    )
                    exit()

                _row[field_name] = python_datetime_value.isoformat()

        serialized_data.append(_row)

    return serialized_data


def make_randomized_int_id() -> int:
    return random.randint(SQLITE_ID_MIN, SQLITE_ID_MAX)


def get_task_ids_by_task_names(db: "MephistoDB", task_names: List[str]) -> List[str]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        task_names_string = ",".join([f"'{s}'" for s in task_names])
        c.execute(
            f"""
            SELECT task_id FROM tasks 
            WHERE task_name IN ({task_names_string});
            """
        )
        rows = c.fetchall()
        return [r["task_id"] for r in rows]


def get_task_run_ids_ids_by_task_ids(db: "MephistoDB", task_ids: List[str]) -> List[str]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        task_ids_string = ",".join([f"'{s}'" for s in task_ids])
        c.execute(
            f"""
            SELECT task_run_id FROM task_runs 
            WHERE task_id IN ({task_ids_string});
            """
        )
        rows = c.fetchall()
        return [r["task_run_id"] for r in rows]


def get_task_run_ids_ids_by_labels(db: "MephistoDB", labels: List[str]) -> List[str]:
    with db.table_access_condition, db.get_connection() as conn:
        if not labels:
            return []

        c = conn.cursor()

        where_labels_string = " OR ".join([f"data_labels LIKE '%\"{l}\"%'" for l in labels])
        where_labels_string = f" AND ({where_labels_string})"

        c.execute(
            f"""
            SELECT unique_field_values FROM imported_data 
            WHERE table_name = 'task_runs' {where_labels_string};
            """
        )
        rows = c.fetchall()

        # Serialize data to plain Python list of IDs
        task_run_ids = []
        for row in rows:
            row_task_run_ids: List[List[str]] = json.loads(row["unique_field_values"])
            task_run_ids += row_task_run_ids

        return task_run_ids


def get_table_pk_field_name(db: "MephistoDB", table_name: str):
    """
    Make a request to get the name of PK field of table and
    store it in `self._tables_pk_fields` for next rows
    """
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"SELECT name FROM pragma_table_info('{table_name}') WHERE pk;"
        )
        table_unique_field_name = c.fetchone()["name"]
        return table_unique_field_name


def select_all_table_rows(db: "MephistoDB", table_name: str) -> List[dict]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"SELECT * FROM {table_name};"
        )
        rows = c.fetchall()
        return [dict(row) for row in rows]


def select_rows_by_list_of_field_values(
    db: "MephistoDB",
    table_name: str,
    field_names: List[str],
    field_values: List[List[str]],
    order_by: Optional[str] = None,
) -> List[dict]:
    """
    Select all entries by table name, field name and list of this field values.
    `field_values` is a list of lists of values for each field name in same order as `field_names`

    For instance:
        table_name - granted_qualifications
        field_names - ["qualification_id", "worker_id"]
        field_values - [[<qualification_id_1>, <qualification_id_2>], [<worker_id_1>]]
    And in this case we will select all Granted Qualifications,
    if we have rows in DB with two Qualification IDs _AND_ one Worder ID
    """
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()

        # Combine WHERE statement
        where_list = []
        for i, field_name in enumerate(field_names):
            _field_values = field_values[i]
            field_values_string = ",".join([f"'{s}'" for s in _field_values])
            where_list.append([field_name, field_values_string])
        where_string = " AND ".join([
            f"{field_name} IN ({field_values_string})"
            for field_name, field_values_string in where_list
        ])

        # Combine ORDER BY statement
        order_by_string = ""
        if order_by:
            order_by_direction = "DESC" if order_by.startswith("-") else "ASC"
            order_by_field_name = order_by[1:] if order_by.startswith("-") else order_by
            order_by_string = f" ORDER BY {order_by_field_name} {order_by_direction}"

        c.execute(
            f"""
            SELECT * FROM {table_name} 
            WHERE {where_string}
            {order_by_string};
            """
        )

        rows = c.fetchall()
        return [dict(row) for row in rows]


def delete_exported_data_without_fk_constraints(
    db: "MephistoDB", db_dump: dict, table_names_can_be_cleaned: Optional[List[str]] = None,
):
    table_names_can_be_cleaned = table_names_can_be_cleaned or []

    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "PRAGMA foreign_keys = off;"
        )

        delete_queries = []
        for table_name, rows in db_dump.items():
            if table_name not in table_names_can_be_cleaned:
                continue

            table_pk_name = get_table_pk_field_name(db, table_name)
            table_pks = [r[table_pk_name] for r in rows]
            table_pks_string = ",".join([f"'{s}'" for s in table_pks])
            delete_queries.append(
                f"DELETE FROM {table_name} WHERE {table_pk_name} IN ({table_pks_string});"
            )
        c.executescript("\n".join(delete_queries))

        c.execute(
            "PRAGMA foreign_keys = on;"
        )


def delete_entire_exported_data(db: "MephistoDB"):
    """Delete all rows in tables without dropping tables"""
    exclude_table_names = ["migrations"]
    table_names = get_list_of_db_table_names(db)
    table_names = [tn for tn in table_names if tn not in exclude_table_names]

    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "PRAGMA foreign_keys = off;"
        )

        delete_queries = []
        for table_name in table_names:
            delete_queries.append(
                f"DELETE FROM {table_name};"
                f"DELETE FROM sqlite_sequence WHERE name='{table_name}';"
            )

        c.executescript("\n".join(delete_queries))

        c.execute(
            "PRAGMA foreign_keys = on;"
        )


def get_list_of_provider_types(db: "MephistoDB") -> List[str]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT provider_type FROM requesters;"
        )
        rows = c.fetchall()
        return [r["provider_type"] for r in rows]


def get_latest_row_from_table(
    db: "MephistoDB", table_name: str, order_by: Optional[str] = "creation_date",
) -> Optional[dict]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"""
            SELECT *
            FROM {table_name} 
            ORDER BY {order_by} DESC 
            LIMIT 1;
            """,
        )
        latest_row = c.fetchone()

        return dict(latest_row) if latest_row else None


def apply_migrations(db: "MephistoDB", migrations: dict):
    with db.table_access_condition, db.get_connection() as conn:
        for migration_name, migration_sql in migrations.items():
            try:
                c = conn.cursor()

                c.execute(
                    """SELECT id FROM migrations WHERE name = ?1;""",
                    (migration_name,),
                )
                migration_has_been_applied = c.fetchone()

                if not migration_has_been_applied:
                    c.executescript(migration_sql)
                    c.execute(
                        """
                        INSERT INTO migrations(
                            name, status
                        ) VALUES (?, ?);
                        """,
                        (migration_name, "completed"),
                    )
            except Exception as e:
                c.execute(
                    """
                    INSERT INTO migrations(
                        name, status, error_message
                    ) VALUES (?, ?, ?);
                    """,
                    (migration_name, "errored", str(e)),
                )
                logger.exception(
                    f"Could not apply migration '{migration_name}' for database '{db.db_path}':\n"
                    f"{migration_sql}.\n"
                    f"Error: {e}. Marked it as errored. in 'migrations' table."
                )


def get_list_of_db_table_names(db: "MephistoDB") -> List[str]:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = c.fetchall()
        return [r["name"] for r in rows]


def get_list_of_tables_to_export(db: "MephistoDB") -> List[str]:
    table_names = get_list_of_db_table_names(db)

    filtered_table_names = []
    for table_name in table_names:
        if not table_name.startswith("sqlite_") and table_name not in ["migrations"]:
            filtered_table_names.append(table_name)

    return filtered_table_names


def check_if_row_with_params_exists(
    db: "MephistoDB", table_name: str, params: dict, select_field: Optional[str] = "*",
) -> bool:
    """
    Check if row exists in `table_name` for passed dict of `params`
    """
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()

        where_args = []
        execute_args = []

        for i, (field_name, field_value) in enumerate(params.items(), start=1):
            execute_args.append(field_value)
            where_args.append(f"{field_name} = ?{i}")

        where_string = "WHERE " + " AND ".join(where_args) if where_args else ""

        c.execute(
            f"""
            SELECT {select_field} 
            FROM {table_name} {where_string} 
            LIMIT 1;
            """,
            execute_args,
        )
        existing_row_in_current_db = c.fetchone()

        return bool(existing_row_in_current_db)


def get_providers_datastores(db: "MephistoDB") -> Dict[str, "MephistoDB"]:
    provider_types = get_list_of_provider_types(db)
    provider_datastores = {t: db.get_datastore_for_provider(t) for t in provider_types}
    return provider_datastores


def db_or_datastore_to_dict(db: "MephistoDB") -> dict:
    """Convert all kind of DBs to dict"""
    dump_data = {}
    table_names = get_list_of_tables_to_export(db)
    for table_name in table_names:
        table_rows = _select_all_rows_from_table(db, table_name)
        table_data = serialize_data_for_table(table_rows)
        dump_data[table_name] = table_data

    return dump_data


def mephisto_db_to_dict_for_task_runs(
    db: "MephistoDB",
    task_run_ids: Optional[List[str]] = None,
) -> dict:
    """
    Partial converation Mephisto DB into dict by given TaskRun IDs
    NOTE: does not work with provider datastores, only main database
    """
    dump_data = {}
    table_names = get_list_of_tables_to_export(db)

    tables_with_task_run_relations = [
        "agents",
        "assignments",
        "onboarding_agents",
        "task_runs",
        "units",
    ]

    tables_with_task_relations = [
        "tasks",
        "unit_review",
    ]

    # Find and serialize tables with `task_run_id` field
    for table_name in table_names:
        if table_name in tables_with_task_run_relations:
            table_rows = select_rows_from_table_related_to_task_run(db, table_name, task_run_ids)
            table_data = serialize_data_for_table(table_rows)
            dump_data[table_name] = table_data

    # Find and serialize tables with `task_id` field
    task_ids = list(set(filter(bool, [i["task_id"] for i in dump_data["task_runs"]])))
    for table_name in table_names:
        if table_name in tables_with_task_relations:
            table_rows = _select_rows_from_table_related_to_task(db, table_name, task_ids)
            table_data = serialize_data_for_table(table_rows)
            dump_data[table_name] = table_data

    # Find and serialize `projects`
    project_ids = list(set(filter(bool, [i["project_id"] for i in dump_data["tasks"]])))
    project_rows = select_rows_by_list_of_field_values(
        db, "projects", ["project_id"], [project_ids],
    )
    dump_data["projects"] = serialize_data_for_table(project_rows)

    # Find and serialize `requesters`
    requester_ids = list(set(filter(bool, [i["requester_id"] for i in dump_data["task_runs"]])))
    requester_rows = select_rows_by_list_of_field_values(
        db, "requesters", ["requester_id"], [requester_ids],
    )
    dump_data["requesters"] = serialize_data_for_table(requester_rows)

    # Find and serialize `workers`
    worker_ids = list(set(filter(bool, [i["worker_id"] for i in dump_data["units"]])))
    worker_rows = select_rows_by_list_of_field_values(
        db, "workers", ["worker_id"], [worker_ids],
    )
    dump_data["workers"] = serialize_data_for_table(worker_rows)

    # Find and serialize `granted_qualifications`
    granted_qualification_rows = select_rows_by_list_of_field_values(
        db, "granted_qualifications", ["worker_id"], [worker_ids],
    )
    dump_data["granted_qualifications"] = serialize_data_for_table(granted_qualification_rows)

    # Find and serialize `qualifications`
    qualification_ids = list(set(filter(
        bool, [i["qualification_id"] for i in dump_data["granted_qualifications"]],
    )))
    qualification_rows = select_rows_by_list_of_field_values(
        db, "qualifications", ["qualification_id"], [qualification_ids],
    )
    dump_data["qualifications"] = serialize_data_for_table(qualification_rows)

    return dump_data


def select_task_run_ids_since_date(db: "MephistoDB", since: datetime) -> List[str]:
    # We are not doing this on the database level because SQLite can have different formats
    # for datetime fields and this is more reliable to perform comparing Python datetimes
    task_run_rows = select_all_table_rows(db, "task_runs")
    task_run_ids_since = []
    for row in task_run_rows:
        creation_datetime = serialize_date_to_python(row["creation_date"])

        if creation_datetime >= since:
            task_run_ids_since.append(row["task_run_id"])

    return task_run_ids_since


def select_fk_mappings_for_table(db: "MephistoDB", table_name: str) -> dict:
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM pragma_foreign_key_list('{table_name}');")
        rows = c.fetchall()
        table_fks = {}

        for row in rows:
            fk_table_name = row["table"]
            current_table_field_name = row["from"]
            relating_table_field_name = row["to"]

            table_fks[fk_table_name] = {
                "from": current_table_field_name,
                "to": relating_table_field_name,
            }

        return table_fks


def select_fk_mappings_for_all_tables(db: "MephistoDB", table_names: List[str]) -> dict:
    tables_fks = {}
    for table_name in table_names:
        table_fks = select_fk_mappings_for_table(db, table_name)
        tables_fks.update({table_name: table_fks})
    return tables_fks


def insert_new_row_in_table(db: "MephistoDB", table_name: str, row: dict):
    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()

        columns, values = zip(*row.items())

        columns_string = ",".join(columns)
        columns_questions_string = ",".join(["?"] * len(columns))

        c.execute(
            f"""
            INSERT INTO {table_name}(
                {columns_string}
            ) VALUES ({columns_questions_string});
            """,
            values,
        )


def update_row_in_table(
    db: "MephistoDB", table_name: str, row: dict, pk_field_name: Optional[str] = None,
):
    row = deepcopy(row)

    if not pk_field_name:
        pk_field_name = get_table_pk_field_name(db, table_name=table_name)

    pk_field_value = row.pop(pk_field_name)

    with db.table_access_condition, db.get_connection() as conn:
        c = conn.cursor()

        columns, values = zip(*row.items())

        columns_set_string = ", ".join([f"{c} = ?" for c in columns])

        c.execute(
            f"""
            UPDATE {table_name}
            SET {columns_set_string}
            WHERE {pk_field_name} = {pk_field_value};
            """,
            values,
        )


# --- Decorators ---

def retry_generate_id(caught_excs: Optional[List[Type[Exception]]] = None):
    """
    A decorator that attempts to call create DB entry until ID will be unique.

    Exception object must have next attributes:
        - original_exc
        - db
        - table_name
    """
    def decorator(unreliable_fn: Callable):
        def wrapped_fn(*args, **kwargs):
            caught_excs_tuple = tuple(caught_excs or [Exception])

            pk_exists = True
            while pk_exists:
                pk_exists = False

                try:
                    # happy path
                    result = unreliable_fn(*args, **kwargs)
                    return result
                except caught_excs_tuple as e:
                    # We can check constraint only in case if excpetion was configured well.
                    # Othervise, we just leave error as is
                    exc_message = str(getattr(e, "original_exc", None) or "")
                    db = getattr(e, "db", None)
                    table_name = getattr(e, "table_name", None)
                    is_unique_constraint = exc_message.startswith("UNIQUE constraint")

                    if db and table_name and is_unique_constraint:
                        pk_field_name = get_table_pk_field_name(db, table_name=table_name)
                        if pk_field_name in exc_message:
                            pk_exists = True

        # Set original function name to wrapped one.
        wrapped_fn.__name__ = unreliable_fn.__name__

        return wrapped_fn
    return decorator
