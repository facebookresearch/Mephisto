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
from typing import Optional

import boto3  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from botocore.exceptions import ProfileNotFound  # type: ignore

from mephisto.abstractions.databases.local_database import is_unique_failure
from mephisto.utils.db import apply_migrations
from mephisto.utils.logger_core import get_logger
from . import mturk_datastore_tables as tables
from .migrations import migrations
from .mturk_datastore_export import export_datastore

MTURK_REGION_NAME = "us-east-1"

logger = get_logger(name=__name__)


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
            conn = self.get_connection()
            conn.execute("PRAGMA foreign_keys = on;")

            with conn:
                c = conn.cursor()
                c.execute(tables.CREATE_IF_NOT_EXISTS_HITS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_RUNS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_RUN_MAP_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_QUALIFICATIONS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE)

            # Migrations
            with conn:
                try:
                    c = conn.cursor()
                    c.execute(tables.UPDATE_RUNS_TABLE_1)
                except Exception:
                    pass  # extra column already exists

            apply_migrations(self, migrations)

    def get_export_data(self, **kwargs) -> dict:
        return export_datastore(self, **kwargs)

    def is_hit_mapping_in_sync(self, unit_id: str, compare_time: float):
        """
        Determine if a cached value from the given compare time is still valid
        """
        return compare_time > self._last_hit_mapping_update_times[unit_id]

    def new_hit(self, hit_id: str, hit_link: str, duration: int, run_id: str) -> None:
        """Register a new HIT mapping in the table"""
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO hits(
                    hit_id,
                    link,
                    assignment_time_in_seconds
                ) VALUES (?, ?, ?);
                """,
                (hit_id, hit_link, duration),
            )
            c.execute(
                """
                INSERT INTO run_mappings(
                    hit_id,
                    run_id
                ) VALUES (?, ?);
                """,
                (hit_id, run_id),
            )

    def get_unassigned_hit_ids(self, run_id: str):
        """
        Return a list of all HIT ids that haven't been assigned
        """
        with self.table_access_condition:
            conn = self.get_connection()
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
        with self.table_access_condition, self.get_connection() as conn:
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
                logger.debug(f"Cleared HIT mapping cache for previous unit, {old_unit_id}")

            c.execute(
                """
                UPDATE hits
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
        with self.table_access_condition, self.get_connection() as conn:
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
                """
                UPDATE hits
                SET assignment_id = ?, unit_id = ?
                WHERE hit_id = ?
                """,
                (None, None, result_hit_id),
            )
            self._mark_hit_mapping_update(unit_id)

    def get_hit_mapping(self, unit_id: str) -> sqlite3.Row:
        """Get the mapping between Mephisto IDs and MTurk ids"""
        with self.table_access_condition:
            conn = self.get_connection()
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
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO runs(
                    run_id,
                    arn_id,
                    hit_type_id,
                    hit_config_path,
                    frame_height
                ) VALUES (?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    "unused",
                    hit_type_id,
                    hit_config_path,
                    frame_height,
                ),
            )

    def get_run(self, run_id: str) -> sqlite3.Row:
        """Get the details for a run by task_run_id"""
        with self.table_access_condition:
            conn = self.get_connection()
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
            with self.table_access_condition, self.get_connection() as conn:
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO qualifications(
                        qualification_name,
                        requester_id,
                        mturk_qualification_name,
                        mturk_qualification_id
                    ) VALUES (?, ?, ?, ?);
                    """,
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
                assert qual is not None, "Cannot be none given is_unique_failure on insert"

                cur_requester_id = qual["requester_id"]
                cur_mturk_qualification_name = qual["mturk_qualification_name"]
                if cur_requester_id != requester_id:
                    logger.warning(
                        f"MTurk Qualification mapping create for {qualification_name} "
                        f"under requester {requester_id}, already exists under {cur_requester_id}."
                    )

                if cur_mturk_qualification_name != mturk_qualification_name:
                    logger.warning(
                        f"MTurk Qualification mapping create "
                        f"for {qualification_name} with mturk name "
                        f"{mturk_qualification_name}, already exists "
                        f"under {cur_mturk_qualification_name}."
                    )

                return None
            else:
                raise e

    def get_qualification_mapping(self, qualification_name: str) -> Optional[sqlite3.Row]:
        """Get the mapping between Mephisto qualifications and MTurk qualifications"""
        with self.table_access_condition:
            conn = self.get_connection()
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
            session = boto3.Session(profile_name=requester_name, region_name=MTURK_REGION_NAME)
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
