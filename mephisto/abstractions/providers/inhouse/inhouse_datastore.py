#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sqlite3
import threading
import time
from collections import defaultdict
from typing import Any
from typing import Dict

from mephisto.abstractions.databases.local_database import is_unique_failure
from mephisto.abstractions.providers.inhouse.provider_type import PROVIDER_TYPE
from mephisto.utils.db import apply_migrations
from mephisto.utils.db import check_if_row_with_params_exists
from mephisto.utils.db import EntryAlreadyExistsException
from mephisto.utils.db import make_randomized_int_id
from mephisto.utils.db import MephistoDBException
from mephisto.utils.db import retry_generate_id
from mephisto.utils.logger_core import get_logger
from . import inhouse_datastore_tables as tables
from .inhouse_datastore_export import export_datastore
from .migrations import migrations

logger = get_logger(name=__name__)


class InhouseDatastore:
    def __init__(self, datastore_root: str):
        """Initialize local storage of active agents, connect to the database"""
        self.agent_data: Dict[str, Dict[str, Any]] = {}
        self.table_access_condition = threading.Condition()
        self.conn: Dict[int, sqlite3.Connection] = {}
        self.db_path = os.path.join(datastore_root, f"{PROVIDER_TYPE}.db")
        self.init_tables()
        self.datastore_root = datastore_root
        self._last_study_mapping_update_times: Dict[str, float] = defaultdict(
            lambda: time.monotonic()
        )

    def get_connection(self) -> sqlite3.Connection:
        """
        Returns a singular database connection to be shared amongst all calls for a given thread.
        """
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.conn[curr_thread] = conn
        return self.conn[curr_thread]

    def init_tables(self) -> None:
        """Run all the table creation SQL queries to ensure the expected tables exist"""
        with self.table_access_condition:
            conn = self.get_connection()
            conn.execute("PRAGMA foreign_keys = on;")

            with conn:
                c = conn.cursor()
                c.execute(tables.CREATE_IF_NOT_EXISTS_WORKERS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE)

            apply_migrations(self, migrations)

    def get_export_data(self, **kwargs) -> dict:
        return export_datastore(self, **kwargs)

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def ensure_worker_exists(self, worker_id: str) -> None:
        """Create a record of this worker if it doesn't exist"""
        already_exists = check_if_row_with_params_exists(
            db=self,
            table_name="workers",
            params={
                "worker_id": worker_id,
            },
            select_field="id",
        )

        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()

            if not already_exists:
                try:
                    c.execute(
                        """
                        INSERT INTO workers(
                            id,
                            worker_id,
                            is_blocked
                        ) VALUES (?, ?, ?);
                        """,
                        (
                            make_randomized_int_id(),
                            worker_id,
                            False,
                        ),
                    )
                    conn.commit()
                except sqlite3.IntegrityError as e:
                    if is_unique_failure(e):
                        raise EntryAlreadyExistsException(
                            e,
                            db=self,
                            table_name="workers",
                            original_exc=e,
                        )
                    raise MephistoDBException(e)

            return None

    def set_worker_blocked(self, worker_id: str, is_blocked: bool) -> None:
        """Set the worker registration status for the given id"""
        self.ensure_worker_exists(worker_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE workers
                SET is_blocked = ?
                WHERE worker_id = ?
                """,
                (is_blocked, worker_id),
            )
            conn.commit()
            return None

    def get_worker_blocked(self, worker_id: str) -> bool:
        """Get the blocked status of a worker"""
        self.ensure_worker_exists(worker_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT is_blocked FROM workers
                WHERE worker_id = ?
                """,
                (worker_id,),
            )
            results = c.fetchall()
            return bool(results[0]["is_blocked"])
