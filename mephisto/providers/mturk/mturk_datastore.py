#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import boto3
import sqlite3
import os
import threading

from datetime import datetime


from botocore.exceptions import ClientError
from botocore.exceptions import ProfileNotFound

from typing import Dict, Any, Optional

MTURK_REGION_NAME = "us-east-1"

CREATE_HITS_TABLE = """CREATE TABLE IF NOT EXISTS hits (
    hit_id TEXT PRIMARY KEY UNIQUE,
    unit_id TEXT,
    assignment_id TEXT,
    link TEXT,
    assignment_time_in_seconds INTEGER NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_RUNS_TABLE = """CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY UNIQUE,
    arn_id TEXT,
    hit_type_id TEXT NOT NULL,
    hit_config_path TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


class MTurkDatastore:
    """
    Handles storing multiple sessions for different requesters
    across a single mephisto thread (locked to a MephistoDB).
    Also creates a relevant tables for mapping between MTurk
    and mephisto.
    """

    def __init__(self, datastore_root: str):
        """Initialize the session storage to empty, initialize tables if needed"""
        self.session_storage: Dict[str, boto3.Session] = {}
        self.table_access_condition = threading.Condition()
        self.conn: Dict[int, sqlite3.Connection] = {}
        self.db_path = os.path.join(datastore_root, "mturk.db")
        self.init_tables()
        self.datastore_root = datastore_root

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a singular database connection to be shared amongst all
        calls for a given thread.
        """
        # TODO is there a problem with having just one db connection?
        # Will this cause bugs with failed commits?
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self.conn[curr_thread] = conn
        return self.conn[curr_thread]

    def init_tables(self) -> None:
        """
        Run all the table creation SQL queries to ensure the expected tables exist
        """
        with self.table_access_condition:
            conn = self._get_connection()
            conn.execute("PRAGMA foreign_keys = 1")
            c = conn.cursor()
            c.execute(CREATE_HITS_TABLE)
            c.execute(CREATE_RUNS_TABLE)
            conn.commit()

    def new_hit(self, hit_id: str, hit_link: str, duration: int) -> None:
        """Register a new HIT mapping in the table"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """INSERT INTO hits(
                    hit_id,
                    link,
                    assignment_time_in_seconds
                ) VALUES (?, ?, ?);""",
                (hit_id, hit_link, duration),
            )
            conn.commit()
            return None

    def get_unassigned_hit_ids(self):
        """
        Return a list of all HIT ids that haven't been assigned
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT hit_id from hits
                WHERE unit_id IS NULL
                """,
                ()
            )
            results = c.fetchall()
            return results

    def register_assignment_to_hit(self, hit_id: str, unit_id: Optional[str] = None, assignment_id: Optional[str] = None) -> None:
        """
        Register a specific assignment and hit to the given unit, 
        or clear the assignment after a return
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """UPDATE hits
                SET assignment_id = ?, unit_id = ?
                WHERE hit_id = ?
                """,
                (assignment_id, unit_id, hit_id),
            )
            conn.commit()
        
    def get_hit_mapping(self, unit_id: str) -> sqlite3.Row:
        """Get the mapping between Mephisto IDs and MTurk ids"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from hits
                WHERE unit_id = ?
                """,
                (unit_id,),
            )
            results = c.fetchall()
            return results[0]

    def register_run(
        self, run_id: str, arn_id: str, hit_type_id: str, hit_config_path: str
    ) -> None:
        """Register a new task run in the mturk table"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """INSERT INTO runs(
                    run_id,
                    arn_id,
                    hit_type_id,
                    hit_config_path
                ) VALUES (?, ?, ?, ?);""",
                (run_id, arn_id, hit_type_id, hit_config_path),
            )
            conn.commit()
            return None

    def get_run(self, run_id: str) -> sqlite3.Row:
        """Get the details for a run by task_run_id"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from runs
                WHERE run_id = ?
                """,
                (run_id,),
            )
            results = c.fetchall()
            return results[0]

    def get_session_for_requester(self, requester_name: str) -> boto3.Session:
        """
        Either create a new session for the given requester or return
        the existing one if it has already been created
        """
        if requester_name not in self.session_storage:
            session = boto3.Session(
                profile_name=requester_name, region_name=MTURK_REGION_NAME
            )
            self.session_storage[requester_name] = session

        return self.session_storage[requester_name]

    def get_client_for_requester(self, requester_name: str) -> Any:
        """
        Return the client for the given requester, which should allow
        direct calls to the mturk surface
        """
        return self.get_session_for_requester(requester_name).client("mturk")

    def get_sandbox_client_for_requester(self, requester_name: str) -> Any:
        """
        Return the client for the given requester, which should allow
        direct calls to the mturk surface
        """
        return self.get_session_for_requester(requester_name).client(
            service_name="mturk",
            region_name="us-east-1",
            endpoint_url="https://mturk-requester-sandbox.us-east-1.amazonaws.com",
        )
