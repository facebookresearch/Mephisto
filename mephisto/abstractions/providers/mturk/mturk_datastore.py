#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import boto3  # type: ignore
import sqlite3
import os
import threading
import time

from datetime import datetime
from collections import defaultdict


from botocore.exceptions import ClientError  # type: ignore
from botocore.exceptions import ProfileNotFound  # type: ignore
from mephisto.abstractions.databases.local_database import is_unique_failure

from typing import Dict, Any, Optional

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)

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

CREATE_RUN_MAP_TABLE = """CREATE TABLE IF NOT EXISTS run_mappings (
    hit_id TEXT,
    run_id TEXT
);
"""

CREATE_RUNS_TABLE = """CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY UNIQUE,
    arn_id TEXT,
    hit_type_id TEXT NOT NULL,
    hit_config_path TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    frame_height INTEGER NOT NULL DEFAULT 650
);
"""

UPDATE_RUNS_TABLE_1 = """ALTER TABLE runs
    ADD COLUMN frame_height INTEGER NOT NULL DEFAULT 650;
"""

CREATE_QUALIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS qualifications (
    qualification_name TEXT PRIMARY KEY UNIQUE,
    requester_id TEXT,
    mturk_qualification_name TEXT,
    mturk_qualification_id TEXT,
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
        self._last_hit_mapping_update_times: Dict[str, float] = defaultdict(
            lambda: time.monotonic()
        )

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a singular database connection to be shared amongst all
        calls for a given thread.
        """
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.conn[curr_thread] = conn
        return self.conn[curr_thread]

    def _mark_hit_mapping_update(self, unit_id: str) -> None:
        """
        Update the last hit mapping time to mark a change to the hit
        mappings table and allow dependents to invalidate caches
        """
        self._last_hit_mapping_update_times[unit_id] = time.monotonic()

    def init_tables(self) -> None:
        """
        Run all the table creation SQL queries to ensure the expected tables exist
        """
        with self.table_access_condition:
            conn = self._get_connection()
            conn.execute("PRAGMA foreign_keys = 1")
            with conn:
                c = conn.cursor()
                c.execute(CREATE_HITS_TABLE)
                c.execute(CREATE_RUNS_TABLE)
                c.execute(CREATE_RUN_MAP_TABLE)
                c.execute(CREATE_QUALIFICATIONS_TABLE)
            with conn:
                try:
                    c = conn.cursor()
                    c.execute(UPDATE_RUNS_TABLE_1)
                except Exception as _e:
                    pass  # extra column already exists

    def is_hit_mapping_in_sync(self, unit_id: str, compare_time: float):
        """
        Determine if a cached value from the given compare time is still valid
        """
        return compare_time > self._last_hit_mapping_update_times[unit_id]

    def new_hit(self, hit_id: str, hit_link: str, duration: int, run_id: str) -> None:
        """Register a new HIT mapping in the table"""
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO hits(
                    hit_id,
                    link,
                    assignment_time_in_seconds
                ) VALUES (?, ?, ?);""",
                (hit_id, hit_link, duration),
            )
            c.execute(
                """INSERT INTO run_mappings(
                    hit_id,
                    run_id
                ) VALUES (?, ?);""",
                (hit_id, run_id),
            )

    def get_unassigned_hit_ids(self, run_id: str):
        """
        Return a list of all HIT ids that haven't been assigned
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT
                    hit_id,
                    unit_id,
                    run_id
                FROM
                    hits
                INNER JOIN run_mappings
                    USING  (hit_id)
                WHERE unit_id IS NULL
                AND run_id = ?;
                """,
                (run_id,),
            )
            results = c.fetchall()
            return [r["hit_id"] for r in results]

    def register_assignment_to_hit(
        self,
        hit_id: str,
        unit_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
    ) -> None:
        """
        Register a specific assignment and hit to the given unit,
        or clear the assignment after a return
        """
        logger.debug(
            f"Attempting to assign HIT {hit_id}, Unit {unit_id}, Assignment {assignment_id}."
        )
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT * from hits
                WHERE hit_id = ?
                """,
                (hit_id,),
            )
            results = c.fetchall()
            if len(results) > 0 and results[0]["unit_id"] is not None:
                old_unit_id = results[0]["unit_id"]
                self._mark_hit_mapping_update(old_unit_id)
                logger.debug(
                    f"Cleared HIT mapping cache for previous unit, {old_unit_id}"
                )

            c.execute(
                """UPDATE hits
                SET assignment_id = ?, unit_id = ?
                WHERE hit_id = ?
                """,
                (assignment_id, unit_id, hit_id),
            )
            if unit_id is not None:
                self._mark_hit_mapping_update(unit_id)

    def clear_hit_from_unit(self, unit_id: str) -> None:
        """
        Clear the hit mapping that maps the given unit,
        if such a unit-hit map exists
        """
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT * from hits
                WHERE unit_id = ?
                """,
                (unit_id,),
            )
            results = c.fetchall()
            if len(results) == 0:
                return
            if len(results) > 1:
                print(
                    "WARNING - UNIT HAD MORE THAN ONE HIT MAPPED TO IT!",
                    unit_id,
                    [dict(r) for r in results],
                )
            result_hit_id = results[0]["hit_id"]
            c.execute(
                """UPDATE hits
                SET assignment_id = ?, unit_id = ?
                WHERE hit_id = ?
                """,
                (None, None, result_hit_id),
            )
            self._mark_hit_mapping_update(unit_id)

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
        self,
        run_id: str,
        hit_type_id: str,
        hit_config_path: str,
        frame_height: int = 0,
    ) -> None:
        """Register a new task run in the mturk table"""
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO runs(
                    run_id,
                    arn_id,
                    hit_type_id,
                    hit_config_path,
                    frame_height
                ) VALUES (?, ?, ?, ?, ?);""",
                (run_id, "unused", hit_type_id, hit_config_path, frame_height),
            )

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

    def create_qualification_mapping(
        self,
        qualification_name: str,
        requester_id: str,
        mturk_qualification_name: str,
        mturk_qualification_id: str,
    ) -> None:
        """
        Create a mapping between mephisto qualification name and mturk
        qualification details in the local datastore.

        Repeat entries with the same `qualification_name` will be idempotent
        """
        try:
            with self.table_access_condition, self._get_connection() as conn:
                c = conn.cursor()
                c.execute(
                    """INSERT INTO qualifications(
                        qualification_name,
                        requester_id,
                        mturk_qualification_name,
                        mturk_qualification_id
                    ) VALUES (?, ?, ?, ?);""",
                    (
                        qualification_name,
                        requester_id,
                        mturk_qualification_name,
                        mturk_qualification_id,
                    ),
                )
                return None
        except sqlite3.IntegrityError as e:
            if is_unique_failure(e):
                # Ignore attempt to add another mapping for an existing key
                qual = self.get_qualification_mapping(qualification_name)
                logger.debug(
                    f"Multiple mturk mapping creations for qualification {qualification_name}. "
                    f"Found existing one: {qual}. "
                )
                assert (
                    qual is not None
                ), "Cannot be none given is_unique_failure on insert"
                cur_requester_id = qual["requester_id"]
                cur_mturk_qualification_name = qual["mturk_qualification_name"]
                cur_mturk_qualification_id = qual["mturk_qualification_id"]
                if cur_requester_id != requester_id:
                    logger.warning(
                        f"MTurk Qualification mapping create for {qualification_name} under requester "
                        f"{requester_id}, already exists under {cur_requester_id}."
                    )
                if cur_mturk_qualification_name != mturk_qualification_name:
                    logger.warning(
                        f"MTurk Qualification mapping create for {qualification_name} with mturk name "
                        f"{mturk_qualification_name}, already exists under {cur_mturk_qualification_name}."
                    )
                return None
            else:
                raise e

    def get_qualification_mapping(
        self, qualification_name: str
    ) -> Optional[sqlite3.Row]:
        """Get the mapping between Mephisto qualifications and MTurk qualifications"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from qualifications
                WHERE qualification_name = ?
                """,
                (qualification_name,),
            )
            results = c.fetchall()
            if len(results) == 0:
                return None
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
