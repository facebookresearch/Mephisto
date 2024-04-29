#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sqlite3
import threading
from typing import Any
from typing import Dict

from mephisto.utils.db import check_if_row_with_params_exists
from . import mock_datastore_tables as tables
from .mock_datastore_export import export_datastore

MTURK_REGION_NAME = "us-east-1"


class MockDatastore:
    """
    Handles storing mock results and statuses across processes for use
    in unit testing and manual experimentation.
    """

    def __init__(self, datastore_root: str):
        """Initialize local storage of active agents, connect to the database"""
        self.agent_data: Dict[str, Dict[str, Any]] = {}
        self.table_access_condition = threading.Condition()
        self.conn: Dict[int, sqlite3.Connection] = {}
        self.db_path = os.path.join(datastore_root, "mock.db")
        self.init_tables()
        self.datastore_root = datastore_root

    def get_connection(self) -> sqlite3.Connection:
        """
        Returns a singular database connection to be shared amongst all
        calls for a given thread.
        """
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.conn[curr_thread] = conn
        return self.conn[curr_thread]

    def init_tables(self) -> None:
        """
        Run all the table creation SQL queries to ensure the expected tables exist
        """
        with self.table_access_condition:
            conn = self.get_connection()
            conn.execute("PRAGMA foreign_keys = on;")

            with conn:
                c = conn.cursor()
                c.execute(tables.CREATE_IF_NOT_EXISTS_REQUESTERS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_UNITS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_WORKERS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE)

    def get_export_data(self, **kwargs) -> dict:
        return export_datastore(self, **kwargs)

    def ensure_requester_exists(self, requester_id: str) -> None:
        """Create a record of this requester if it doesn't exist"""
        already_exists = check_if_row_with_params_exists(
            db=self,
            table_name="requesters",
            params={
                "requester_id": requester_id,
                "is_registered": False,
            },
            select_field="requester_id",
        )

        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()

            if not already_exists:
                c.execute(
                    """
                    INSERT INTO requesters(
                        requester_id,
                        is_registered
                    ) VALUES (?, ?);
                    """,
                    (requester_id, False),
                )
                conn.commit()

            return None

    def set_requester_registered(self, requester_id: str, val: bool) -> None:
        """Set the requester registration status for the given id"""
        self.ensure_requester_exists(requester_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE requesters
                SET is_registered = ?
                WHERE requester_id = ?
                """,
                (val, requester_id),
            )
            conn.commit()
            return None

    def get_requester_registered(self, requester_id: str) -> bool:
        """Get the registration status of a requester"""
        self.ensure_requester_exists(requester_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT is_registered from requesters
                WHERE requester_id = ?
                """,
                (requester_id,),
            )
            results = c.fetchall()
            return bool(results[0]["is_registered"])

    def ensure_worker_exists(self, worker_id: str) -> None:
        """Create a record of this worker if it doesn't exist"""
        already_exists = check_if_row_with_params_exists(
            db=self,
            table_name="workers",
            params={
                "worker_id": worker_id,
            },
            select_field="worker_id",
        )

        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()

            if not already_exists:
                c.execute(
                    """
                    INSERT INTO workers(
                        worker_id,
                        is_blocked
                    ) VALUES (?, ?);
                    """,
                    (worker_id, False),
                )
                conn.commit()

            return None

    def set_worker_blocked(self, worker_id: str, val: bool) -> None:
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
                (val, worker_id),
            )
            conn.commit()
            return None

    def get_worker_blocked(self, worker_id: str) -> bool:
        """Get the registration status of a worker"""
        self.ensure_worker_exists(worker_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT is_blocked from workers
                WHERE worker_id = ?
                """,
                (worker_id,),
            )
            results = c.fetchall()
            return bool(results[0]["is_blocked"])

    def ensure_unit_exists(self, unit_id: str) -> None:
        """Create a record of this unit if it doesn't exist"""
        already_exists = check_if_row_with_params_exists(
            db=self,
            table_name="units",
            params={
                "unit_id": unit_id,
                "is_expired": False,
            },
            select_field="unit_id",
        )

        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()

            if not already_exists:
                c.execute(
                    """
                    INSERT INTO units(
                        unit_id,
                        is_expired
                    ) VALUES (?, ?);
                    """,
                    (unit_id, False),
                )
                conn.commit()

            return None

    def set_unit_expired(self, unit_id: str, val: bool) -> None:
        """Set the unit registration status for the given id"""
        self.ensure_unit_exists(unit_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE units
                SET is_expired = ?
                WHERE unit_id = ?
                """,
                (val, unit_id),
            )
            conn.commit()
            return None

    def get_unit_expired(self, unit_id: str) -> bool:
        """Get the registration status of a unit"""
        self.ensure_unit_exists(unit_id)
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT is_expired from units
                WHERE unit_id = ?
                """,
                (unit_id,),
            )
            results = c.fetchall()
            return bool(results[0]["is_expired"])
