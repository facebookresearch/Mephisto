#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import sqlite3
import threading
import time
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from mephisto.abstractions.databases.local_database import is_unique_failure
from mephisto.abstractions.providers.prolific.api.constants import StudyStatus
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.utils.logger_core import get_logger
from mephisto.utils.qualifications import QualificationType
from . import prolific_datastore_tables as tables
from .api.client import ProlificClient
from .prolific_utils import get_authenticated_client

logger = get_logger(name=__name__)


class ProlificDatastore:
    def __init__(self, datastore_root: str):
        """Initialize local storage of active agents, connect to the database"""
        self.session_storage: Dict[str, ProlificClient] = {}
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
            conn.execute("PRAGMA foreign_keys = 1")
            c = conn.cursor()
            c.execute(tables.CREATE_STUDIES_TABLE)
            c.execute(tables.CREATE_SUBMISSIONS_TABLE)
            c.execute(tables.CREATE_REQUESTERS_TABLE)
            c.execute(tables.CREATE_UNITS_TABLE)
            c.execute(tables.CREATE_WORKERS_TABLE)
            c.execute(tables.CREATE_RUNS_TABLE)
            c.execute(tables.CREATE_RUN_MAP_TABLE)
            c.execute(tables.CREATE_PARTICIPANT_GROUPS_TABLE)
            c.execute(tables.CREATE_PARTICIPANT_GROUP_QUALIFICATIONS_MAPPING_TABLE)
            conn.commit()

    def is_study_mapping_in_sync(self, unit_id: str, compare_time: float):
        """Determine if a cached value from the given compare time is still valid"""
        return compare_time > self._last_study_mapping_update_times[unit_id]

    def new_study(
        self,
        prolific_study_id: str,
        study_link: str,
        duration_in_seconds: int,
        task_run_id: str,
        status: str = StudyStatus.UNPUBLISHED,
    ) -> None:
        """Register a new Study mapping in the table"""
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO studies(
                    prolific_study_id,
                    task_run_id,
                    link,
                    assignment_time_in_seconds,
                    status
                ) VALUES (?, ?, ?, ?, ?);
                """,
                (prolific_study_id, task_run_id, study_link, duration_in_seconds, status),
            )
            c.execute(
                """
                INSERT INTO run_mappings(
                    prolific_study_id,
                    run_id
                ) VALUES (?, ?);
                """,
                (prolific_study_id, task_run_id),
            )

    def update_study_status(self, study_id: str, status: str) -> None:
        """Set the study status in datastore"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE studies
                SET status = ?
                WHERE prolific_study_id = ?
                """,
                (status, study_id),
            )
            conn.commit()
            return None

    def all_study_units_are_expired(self, run_id: str) -> bool:
        """Return a list of all Study ids that haven't been assigned"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()

            c.execute(
                """
                SELECT
                    prolific_study_id,
                    (
                        SELECT
                            count(units.unit_id)
                        FROM units
                        WHERE
                            units.prolific_study_id = studies.prolific_study_id AND
                            units.is_expired = 0
                    ) AS unexpired_units_count
                FROM studies
                INNER JOIN run_mappings USING (prolific_study_id)
                WHERE
                    run_mappings.run_id = ? AND
                    unexpired_units_count == 0
                GROUP BY prolific_study_id;
                """,
                (run_id,),
            )
            results = c.fetchall()
            return bool(results)

    def register_submission_to_study(
        self,
        prolific_study_id: str,
        unit_id: Optional[str] = None,
        prolific_submission_id: Optional[str] = None,
    ) -> None:
        """
        Register a specific Submission and Study to the given unit,
        or clear the assignment after a return
        """
        logger.debug(
            f"Attempting to assign Study {prolific_study_id}, "
            f"Unit {unit_id}, "
            f"Submission {prolific_submission_id}."
        )
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()

            c.execute(
                """
                INSERT OR IGNORE INTO submissions(
                    prolific_study_id,
                    prolific_submission_id
                ) VALUES (?, ?);
                """,
                (prolific_study_id, prolific_submission_id),
            )

            if unit_id is not None:
                self._mark_study_mapping_update(unit_id)

    def update_submission_status(self, prolific_submission_id: str, status: str) -> None:
        """Set prolific_submission_id to unit"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE submissions
                SET status = ?
                WHERE prolific_submission_id = ?
                """,
                (status, prolific_submission_id),
            )
            conn.commit()
            return None

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

    def set_worker_blocked(self, worker_id: str, is_blocked: bool) -> None:
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
                (is_blocked, worker_id),
            )
            conn.commit()
            return None

    def get_worker_blocked(self, worker_id: str) -> bool:
        """Get the blocked status of a worker"""
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

    def get_blocked_workers(self) -> List[dict]:
        """Get all workers with blocked status"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT worker_id FROM workers
                WHERE is_blocked = ?
                """,
                (True,),
            )
            results = c.fetchall()
            return results

    def get_bloked_participant_ids(self) -> List[str]:
        return [w["worker_id"] for w in self.get_blocked_workers()]

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

    def create_unit(self, unit_id: str, run_id: str, prolific_study_id: str) -> None:
        """Create the unit if not exists"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                INSERT OR IGNORE INTO units(
                    unit_id,
                    run_id,
                    prolific_study_id,
                    is_expired
                ) VALUES (?, ?, ?, ?);
                """,
                (unit_id, run_id, prolific_study_id, False),
            )
            conn.commit()
            return None

    def get_unit(self, unit_id: str) -> sqlite3.Row:
        """Get the details for a unit by unit_id"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from units
                WHERE unit_id = ?;
                """,
                (unit_id,),
            )
            results = c.fetchall()
            return results[0]

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

    def set_submission_for_unit(self, unit_id: str, prolific_submission_id: str) -> None:
        """Set prolific_submission_id to unit"""
        self.ensure_unit_exists(unit_id)
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE units
                SET prolific_submission_id = ?
                WHERE unit_id = ?
                """,
                (prolific_submission_id, unit_id),
            )
            conn.commit()
            return None

    def get_session_for_requester(self, requester_name: str) -> ProlificClient:
        """
        Either create a new session for the given requester or return
        the existing one if it has already been created
        """
        if requester_name not in self.session_storage:
            session = get_authenticated_client(requester_name)
            self.session_storage[requester_name] = session

        return self.session_storage[requester_name]

    def get_client_for_requester(self, requester_name: str) -> ProlificClient:
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
                SELECT * FROM participant_groups
                WHERE qualification_name = ?
                """,
                (qualification_name,),
            )
            results = c.fetchall()
            if len(results) == 0:
                return None
            return results[0]

    def create_participant_group_mapping(
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
                    INSERT INTO participant_groups(
                        qualification_name,
                        requester_id,
                        prolific_project_id,
                        prolific_participant_group_name,
                        prolific_participant_group_id
                    ) VALUES (?, ?, ?, ?, ?);
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
                    f"Multiple Prolific mapping creations "
                    f'for qualification "{qualification_name}". '
                    f"Found existing one: {db_qualification}. "
                )
                assert (
                    db_qualification is not None
                ), "Cannot be none given is_unique_failure on insert"

                db_requester_id = db_qualification["requester_id"]
                db_prolific_qualification_name = db_qualification["prolific_participant_group_name"]

                if db_requester_id != requester_id:
                    logger.warning(
                        f"Prolific Qualification mapping create for {qualification_name} "
                        f"under requester {requester_id}, already exists under {db_requester_id}."
                    )

                if db_prolific_qualification_name != prolific_participant_group_name:
                    logger.warning(
                        f"Prolific Qualification mapping create for {qualification_name} "
                        f"with Prolific name {prolific_participant_group_name}, "
                        f"already exists under {db_prolific_qualification_name}."
                    )

                return None
            else:
                raise e

    def delete_participant_groups_by_participant_group_ids(
        self,
        participant_group_ids: List[str] = None,
    ) -> None:
        """Delete participant_groups by Participant Group IDs"""
        if not participant_group_ids:
            return None

        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()

            participant_group_ids_block = ""
            if participant_group_ids:
                task_run_ids_str = ",".join([f'"{pgi}"' for pgi in participant_group_ids])
                participant_group_ids_block = (
                    f"AND prolific_participant_group_id IN ({task_run_ids_str})"
                )

            c.execute(
                f"""
                DELETE FROM participant_groups
                WHERE {participant_group_ids_block};
                """
            )
            return None

    def create_qualification_mapping(
        self,
        run_id: str,
        prolific_participant_group_id: str,
        qualifications: List[QualificationType],
        qualification_ids: List[int],
    ) -> None:
        """Register a new participant group mapping with qualifications"""
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            qualifications_json = json.dumps(qualifications)
            qualification_ids_json = json.dumps(qualification_ids)
            c.execute(
                """
                INSERT INTO qualifications(
                    prolific_participant_group_id,
                    task_run_id,
                    json_qual_logic,
                    qualification_ids
                ) VALUES (?, ?, ?, ?);
                """,
                (
                    prolific_participant_group_id,
                    run_id,
                    qualifications_json,
                    qualification_ids_json,
                ),
            )

    def find_studies_by_status(self, statuses: List[str], exclude: bool = False) -> List[dict]:
        """Find all studies having or excluding certain statuses"""
        if not statuses:
            return []

        logic_str = "NOT" if exclude else ""
        statuses_str = ",".join([f'"{s}"' for s in statuses])

        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"""
                SELECT * from studies
                WHERE status {logic_str} IN ({statuses_str});
                """
            )
            results = c.fetchall()
            return results

    def find_qualifications_for_running_studies(
        self,
        qualification_ids: List[str],
    ) -> List[dict]:
        """Find qualifications by Mephisto ids of qualifications for all incomplete studies"""
        if not qualification_ids:
            return []

        running_studies = self.find_studies_by_status(
            statuses=[StudyStatus.COMPLETED, StudyStatus.AWAITING_REVIEW],
            exclude=True,
        )
        task_run_ids = [s["task_run_id"] for s in running_studies]
        return self.find_qualifications_by_ids(
            qualification_ids=qualification_ids,
            task_run_ids=task_run_ids,
        )

    def find_qualifications_by_ids(
        self,
        qualification_ids: List[str] = None,
        task_run_ids: Optional[List[str]] = None,
    ) -> List[dict]:
        """Find qualifications by Mephisto ids of qualifications and task runs"""
        if not qualification_ids:
            return []

        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()

            qualification_ids_block = ""
            if qualification_ids:
                qualification_ids_block = " OR ".join(
                    "qualification_ids LIKE '%\"" + str(_id) + "\"%'" for _id in qualification_ids
                )
                qualification_ids_block = f"({qualification_ids_block})"

            task_run_ids_block = ""
            if task_run_ids:
                task_run_ids_str = ",".join([f'"{tid}"' for tid in task_run_ids])
                task_run_ids_block = f"AND task_run_id IN ({task_run_ids_str})"

            c.execute(
                f"""
                SELECT * FROM qualifications
                WHERE {qualification_ids_block} {task_run_ids_block};
                """
            )
            results = c.fetchall()
            return results

    def delete_qualifications_by_participant_group_ids(
        self,
        participant_group_ids: List[str] = None,
    ) -> None:
        """Delete qualifications by Participant Group IDs"""
        if not participant_group_ids:
            return None

        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()

            participant_group_ids_block = ""
            if participant_group_ids:
                task_run_ids_str = ",".join([f'"{pgi}"' for pgi in participant_group_ids])
                participant_group_ids_block = (
                    f"AND prolific_participant_group_id IN ({task_run_ids_str})"
                )

            c.execute(
                f"""
                DELETE FROM qualifications
                WHERE {participant_group_ids_block};
                """
            )
            return None

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
                INNER JOIN units USING (prolific_study_id)
                WHERE units.unit_id = ?;
                """,
                (unit_id,),
            )
            results = c.fetchall()
            if len(results) == 0:
                return
            if len(results) > 1:
                logger.warning(
                    "WARNING - UNIT HAD MORE THAN ONE STUDY MAPPED TO IT!",
                    unit_id,
                    [dict(r) for r in results],
                )
            result_study_id = results[0]["prolific_study_id"]
            c.execute(
                """
                UPDATE units
                SET prolific_study_id = ?
                WHERE unit_id = ? AND prolific_study_id = ?;
                """,
                (None, unit_id, result_study_id),
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
                INNER JOIN units USING (prolific_study_id)
                WHERE units.unit_id = ?;
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
        prolific_study_config_path: str,
        frame_height: int = 0,
        actual_available_places: Optional[int] = None,
        listed_available_places: Optional[int] = None,
        prolific_study_id: Optional[str] = None,
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
                    frame_height,
                    actual_available_places,
                    listed_available_places
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    "unused",
                    prolific_workspace_id,
                    prolific_project_id,
                    prolific_study_id,
                    prolific_study_config_path,
                    frame_height,
                    actual_available_places,
                    listed_available_places,
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
                WHERE run_id = ?;
                """,
                (run_id,),
            )
            results = c.fetchall()
            return results[0]

    def set_available_places_for_run(
        self,
        run_id: str,
        actual_available_places: int,
        listed_available_places: int,
    ) -> None:
        """Set available places for a run by task_run_id"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                UPDATE runs
                SET actual_available_places = ?, listed_available_places = ?
                WHERE run_id = ?
                """,
                (
                    actual_available_places,
                    listed_available_places,
                    run_id,
                ),
            )
            conn.commit()
            return None
