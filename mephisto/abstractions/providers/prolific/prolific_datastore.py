#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
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

from mephisto.abstractions.databases.local_database import is_unique_failure
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.utils.logger_core import get_logger
from . import api as prolific_api
from . import prolific_datastore_tables as tables

logger = get_logger(name=__name__)


class ProlificDatastore:
    def __init__(self, datastore_root: str):
        """Initialize local storage of active agents, connect to the database"""
        self.session_storage: Dict[str, Any] = {}  # TODO (#1008): Implement type
        self.agent_data: Dict[str, Dict[str, Any]] = {}
        self.table_access_condition = threading.Condition()
        self.conn: Dict[int, sqlite3.Connection] = {}
        self.db_path = os.path.join(datastore_root, f"{PROVIDER_TYPE}.db")
        self.init_tables()
        self.datastore_root = datastore_root
        self._last_study_mapping_update_times: Dict[str, float] = defaultdict(
            lambda: time.monotonic()
        )

    def _get_connection(self) -> sqlite3.Connection:
        """
        Returns a singular database connection to be shared amongst all calls for a given thread.
        """
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.conn[curr_thread] = conn
        return self.conn[curr_thread]

    def _mark_study_mapping_update(self, unit_id: str) -> None:
        """
        Update the last Study mapping time to mark a change to the Study
        mappings table and allow dependents to invalidate caches
        """
        self._last_study_mapping_update_times[unit_id] = time.monotonic()

    def init_tables(self) -> None:
        """Run all the table creation SQL queries to ensure the expected tables exist"""
        with self.table_access_condition:
            conn = self._get_connection()
            conn.execute('PRAGMA foreign_keys = 1')
            c = conn.cursor()
            c.execute(tables.CREATE_STUDIES_TABLE)
            c.execute(tables.CREATE_REQUESTERS_TABLE)
            c.execute(tables.CREATE_UNITS_TABLE)
            c.execute(tables.CREATE_WORKERS_TABLE)
            c.execute(tables.CREATE_RUNS_TABLE)
            c.execute(tables.CREATE_RUN_MAP_TABLE)
            c.execute(tables.CREATE_QUALIFICATIONS_TABLE)
            conn.commit()

    def is_study_mapping_in_sync(self, unit_id: str, compare_time: float):
        """Determine if a cached value from the given compare time is still valid"""
        return compare_time > self._last_study_mapping_update_times[unit_id]

    def new_study(
        self, study_id: str, study_link: str, duration_in_seconds: int, run_id: str,
    ) -> None:
        """Register a new Study mapping in the table"""
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO studies(
                    study_id,
                    link,
                    assignment_time_in_seconds
                ) VALUES (?, ?, ?);
                """,
                (study_id, study_link, duration_in_seconds),
            )
            c.execute(
                """
                INSERT INTO run_mappings(
                    study_id,
                    run_id
                ) VALUES (?, ?);
                """,
                (study_id, run_id),
            )

    def get_unassigned_study_ids(self, run_id: str):
        """Return a list of all Study ids that haven't been assigned"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT
                    study_id,
                    unit_id,
                    run_id
                FROM
                    studies
                INNER JOIN run_mappings
                    USING  (study_id)
                WHERE unit_id IS NULL
                AND run_id = ?;
                """,
                (run_id,),
            )
            results = c.fetchall()
            return [r['study_id'] for r in results]

    def ensure_requester_exists(self, requester_id: str) -> None:
        """Create a record of this requester if it doesn't exist"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                INSERT OR IGNORE INTO requesters(
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
            conn = self._get_connection()
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT is_registered FROM requesters
                WHERE requester_id = ?
                """,
                (requester_id,),
            )
            results = c.fetchall()
            return bool(results[0]["is_registered"])

    def ensure_worker_exists(self, worker_id: str) -> None:
        """Create a record of this worker if it doesn't exist"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                INSERT OR IGNORE INTO workers(
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
            conn = self._get_connection()
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
            conn = self._get_connection()
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

    def ensure_unit_exists(self, unit_id: str) -> None:
        """Create a record of this unit if it doesn't exist"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                INSERT OR IGNORE INTO units(
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
            conn = self._get_connection()
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT is_expired FROM units
                WHERE unit_id = ?
                """,
                (unit_id,),
            )
            results = c.fetchall()
            return bool(results[0]["is_expired"])

    def get_session_for_requester(self, requester_name: str) -> prolific_api:
        """
        Either create a new session for the given requester or return
        the existing one if it has already been created
        """
        if requester_name not in self.session_storage:
            session = prolific_api
            self.session_storage[requester_name] = session

        return self.session_storage[requester_name]

    def get_client_for_requester(self, requester_name: str) -> prolific_api:
        """
        Return the client for the given requester, which should allow
        direct calls to the Prolific surface
        """
        return self.get_session_for_requester(requester_name)

    def get_qualification_mapping(self, qualification_name: str) -> Optional[sqlite3.Row]:
        """Get the mapping between Mephisto qualifications and Prolific Participant Group"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * FROM qualifications
                WHERE qualification_name = ?
                """,
                (qualification_name,),
            )
            results = c.fetchall()
            if len(results) == 0:
                return None
            return results[0]

    def create_qualification_mapping(
        self,
        qualification_name: str,
        requester_id: str,
        prolific_project_id: str,
        prolific_participant_group_name: str,
        prolific_participant_group_id: str,
    ) -> None:
        """
        Create a mapping between mephisto qualification name and Prolific
        Participant Group details in the local datastore.

        Repeat entries with the same `qualification_name` will be idempotent
        """
        try:
            with self.table_access_condition, self._get_connection() as conn:
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO qualifications(
                        qualification_name,
                        requester_id,
                        prolific_project_id,
                        prolific_participant_group_name,
                        prolific_participant_group_id
                    ) VALUES (?, ?, ?, ?);
                    """,
                    (
                        qualification_name,
                        requester_id,
                        prolific_project_id,
                        prolific_participant_group_name,
                        prolific_participant_group_id,
                    ),
                )
                return None

        except sqlite3.IntegrityError as e:
            if is_unique_failure(e):
                # Ignore attempt to add another mapping for an existing key
                db_qualification = self.get_qualification_mapping(qualification_name)

                logger.debug(
                    f'Multiple Prolific mapping creations '
                    f'for qualification "{qualification_name}". '
                    f'Found existing one: {db_qualification}. '
                )
                assert \
                    db_qualification is not None, \
                    'Cannot be none given is_unique_failure on insert'

                db_requester_id = db_qualification['requester_id']
                db_prolific_qualification_name = db_qualification['prolific_participant_group_name']

                if db_requester_id != requester_id:
                    logger.warning(
                        f'Prolific Qualification mapping create for {qualification_name} '
                        f'under requester {requester_id}, already exists under {db_requester_id}.'
                    )

                if db_prolific_qualification_name != prolific_participant_group_name:
                    logger.warning(
                        f'Prolific Qualification mapping create for {qualification_name} '
                        f'with Prolific name {prolific_participant_group_name}, '
                        f'already exists under {db_prolific_qualification_name}.'
                    )

                return None
            else:
                raise e

    def clear_study_from_unit(self, unit_id: str) -> None:
        """
        Clear the Study mapping that maps the given unit,
        if such a unit-study map exists
        """
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT * FROM studies
                WHERE unit_id = ?
                """,
                (unit_id,),
            )
            results = c.fetchall()
            if len(results) == 0:
                return
            if len(results) > 1:
                logger.warning(
                    'WARNING - UNIT HAD MORE THAN ONE STUDY MAPPED TO IT!',
                    unit_id,
                    [dict(r) for r in results],
                )
            result_study_id = results[0]['study_id']
            c.execute(
                """
                UPDATE studies
                SET assignment_id = ?, unit_id = ?
                WHERE srudy_id = ?
                """,
                (None, None, result_study_id),
            )
            self._mark_study_mapping_update(unit_id)

    def get_study_mapping(self, unit_id: str) -> sqlite3.Row:
        """Get the mapping between Mephisto IDs and Prolific IDs"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from studies
                WHERE unit_id = ?
                """,
                (unit_id,),
            )
            results = c.fetchall()
            return results[0]

    def register_run(
        self,
        run_id: str,
        prolific_workspace_id: str,
        prolific_project_id: str,
        prolific_study_id: str,
        prolific_study_config_path: str,
        frame_height: int = 0,
    ) -> None:
        """Register a new task run in the Task Runs table"""
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO runs(
                    run_id,
                    arn_id,
                    prolific_workspace_id,
                    prolific_project_id,
                    prolific_study_id,
                    prolific_study_config_path,
                    frame_height
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    "unused",
                    prolific_workspace_id,
                    prolific_project_id,
                    prolific_study_id,
                    prolific_study_config_path,
                    frame_height,
                ),
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
