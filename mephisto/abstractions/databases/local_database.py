#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import sqlite3
import threading
from sqlite3 import Connection
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import Union

from mephisto.abstractions.database import MephistoDB
from mephisto.data_model.agent import Agent
from mephisto.data_model.agent import AgentState
from mephisto.data_model.agent import OnboardingAgent
from mephisto.data_model.assignment import Assignment
from mephisto.data_model.assignment import AssignmentState
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.data_model.project import Project
from mephisto.data_model.qualification import GrantedQualification
from mephisto.data_model.qualification import Qualification
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.operations.registry import get_valid_provider_types
from mephisto.utils.db import apply_migrations
from mephisto.utils.db import EntryAlreadyExistsException
from mephisto.utils.db import EntryDoesNotExistException
from mephisto.utils.db import make_randomized_int_id
from mephisto.utils.db import MephistoDBException
from mephisto.utils.db import retry_generate_id
from mephisto.utils.logger_core import get_logger
from . import local_database_tables as tables
from .migrations import migrations

logger = get_logger(name=__name__)


def nonesafe_int(in_string: Optional[Union[str, int]]) -> Optional[int]:
    """Cast input to an int or None"""
    if in_string is None:
        return None
    return int(in_string)


def assert_valid_provider(provider_type: str) -> None:
    """Throw an assertion error if the given provider type is not valid"""
    valid_types = get_valid_provider_types()
    if provider_type not in valid_types:
        raise MephistoDBException(
            f"Supplied provider {provider_type} is not in supported list of "
            f"providers {valid_types}."
        )


def is_key_failure(e: sqlite3.IntegrityError) -> bool:
    """
    Return if the given error is representing a foreign key failure,
    where an insertion was expecting something to exist already in the DB, but it didn't.
    """
    return str(e) == "FOREIGN KEY constraint failed"


def is_unique_failure(e: sqlite3.IntegrityError) -> bool:
    """
    Return if the given error is representing a foreign key failure,
    where an insertion was expecting something to exist already in the DB, but it didn't.
    """
    return str(e).startswith("UNIQUE constraint")


class StringIDRow(sqlite3.Row):
    def __getitem__(self, key: str) -> Any:
        val = super().__getitem__(key)
        if key.endswith("_id") and val is not None:
            return str(val)
        else:
            return val


class LocalMephistoDB(MephistoDB):
    """
    Local database for core Mephisto data storage, the LocalMephistoDatabase handles
    grounding all the python interactions with the Mephisto architecture to
    local files and a database.
    """

    def __init__(self, database_path=None):
        logger.debug(f"database path: {database_path}")
        self.conn: Dict[int, Connection] = {}
        self.table_access_condition = threading.Condition()
        super().__init__(database_path)

    def get_connection(self) -> Connection:
        """Returns a singular database connection to be shared amongst all
        calls for a given thread.
        """
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = StringIDRow
                self.conn[curr_thread] = conn
            except sqlite3.Error as e:
                raise MephistoDBException(e)
        return self.conn[curr_thread]

    def shutdown(self) -> None:
        """Close all open connections"""
        with self.table_access_condition:
            curr_thread = threading.get_ident()
            self.conn[curr_thread].close()
            del self.conn[curr_thread]

    def init_tables(self) -> None:
        """
        Run all the table creation SQL queries to ensure the expected tables exist
        """
        with self.table_access_condition:
            conn = self.get_connection()
            conn.execute("PRAGMA foreign_keys = on;")

            with conn:
                c = conn.cursor()
                c.execute(tables.CREATE_IF_NOT_EXISTS_PROJECTS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_TASKS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_REQUESTERS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_TASK_RUNS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_ASSIGNMENTS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_UNITS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_WORKERS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_AGENTS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_QUALIFICATIONS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_GRANTED_QUALIFICATIONS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_ONBOARDING_AGENTS_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_UNIT_REVIEW_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_IMPORT_DATA_TABLE)
                c.execute(tables.CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE)

            apply_migrations(self, migrations)

            # Creating indices must be after migrations.
            # SQLite have a lack of features comparing to other databases,
            # and, e.g., if we need to change a constraint, we need to recteate a table.
            # We will lose indices in this case, or we need to repeat creating in the migration
            with conn:
                c.executescript(tables.CREATE_IF_NOT_EXISTS_CORE_INDICES)

    def __get_one_by_id(self, table_name: str, id_name: str, db_id: str) -> Mapping[str, Any]:
        """
        Try to request the row for the given table and entry,
        raise EntryDoesNotExistException if it isn't present
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                f"""
                SELECT * FROM {table_name}
                WHERE ({id_name} = ?)
                """,
                (int(db_id),),
            )
            results = c.fetchall()
            if len(results) != 1:
                raise EntryDoesNotExistException(f"Table {table_name} has no {id_name} {db_id}")
            return results[0]

    @staticmethod
    def __create_query_and_tuple(
        arg_list: List[str],
        arg_vals: List[Optional[Union[str, int, bool]]],
    ) -> Tuple[str, tuple]:
        """
        Given a list of the possible filtering args and valid values,
        construct the WHERE part of a query with these and
        a tuple containing the elements
        """
        fin_args = []
        fin_vals = []
        for arg, val in zip(arg_list, arg_vals):
            if val is None:
                continue
            fin_args.append(arg)
            fin_vals.append(val)
        if len(fin_args) == 0:
            return "", ()

        query_lines = [
            f"WHERE {arg_name} = ?{idx+1}\n" if idx == 0 else f"AND {arg_name} = ?{idx+1}\n"
            for idx, arg_name in enumerate(fin_args)
        ]

        return "".join(query_lines), tuple(fin_vals)

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_project(self, project_name: str) -> str:
        """
        Create a new project with the given project name.
        Raise EntryAlreadyExistsException if a project with this name has already been created.
        """
        if project_name in [NO_PROJECT_NAME, ""]:
            raise MephistoDBException(f'Invalid project name "{project_name}')
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO projects(
                        project_id,
                        project_name
                    ) VALUES (?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        project_name,
                    ),
                )
                project_id = str(c.lastrowid)
                return project_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException()
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        f"Project {project_name} already exists",
                        db=self,
                        table_name="projects",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_project(self, project_id: str) -> Mapping[str, Any]:
        """
        Return project's fields by the given project_id, raise EntryDoesNotExistException
        if no id exists in projects

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("projects", "project_id", project_id)

    def _find_projects(self, project_name: Optional[str] = None) -> List[Project]:
        """
        Try to find any project that matches the above. When called with no arguments,
        return all projects.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                ["project_name"], [project_name]
            )
            c.execute(
                """
                SELECT * from projects
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [Project(self, str(r["project_id"]), row=r, _used_new_call=True) for r in rows]

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_task(
        self,
        task_name: str,
        task_type: str,
        project_id: Optional[str] = None,
    ) -> str:
        """
        Create a new task with the given task name. Raise EntryAlreadyExistsException if a task
        with this name has already been created.
        """
        if task_name in [""]:
            raise MephistoDBException(f'Invalid task name "{task_name}')
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO tasks(
                        task_id,
                        task_name,
                        task_type,
                        project_id,
                        parent_task_id
                    ) VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        task_name,
                        task_type,
                        nonesafe_int(project_id),
                        None,
                    ),
                )
                task_id = str(c.lastrowid)
                return task_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="tasks",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_task(self, task_id: str) -> Mapping[str, Any]:
        """
        Return task's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("tasks", "task_id", task_id)

    def _find_tasks(
        self,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Task]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                ["task_name", "project_id", "parent_task_id"],
                [task_name, nonesafe_int(project_id), None],
            )
            c.execute(
                """
                SELECT * from tasks
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [Task(self, str(r["task_id"]), row=r, _used_new_call=True) for r in rows]

    def _update_task(
        self,
        task_id: str,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """
        Update the given task with the given parameters if possible,
        raise appropriate exception otherwise.

        Tasks can only be updated if no runs exist for this task yet,
        otherwise there's too much state, and we shouldn't make changes.
        """
        if len(self.find_task_runs(task_id=task_id)) != 0:
            raise MephistoDBException(
                "Cannot edit a task that has already been run, for risk of data corruption."
            )
        if task_name in [""]:
            raise MephistoDBException(f'Invalid task name "{task_name}')
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                if task_name is not None:
                    c.execute(
                        """
                        UPDATE tasks
                        SET task_name = ?
                        WHERE task_id = ?;
                        """,
                        (task_name, int(task_id)),
                    )
                if project_id is not None:
                    c.execute(
                        """
                        UPDATE tasks
                        SET project_id = ?
                        WHERE task_id = ?;
                        """,
                        (int(project_id), int(task_id)),
                    )
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        f"Task name {task_name} is already in use",
                        db=self,
                        table_name="units",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_task_run(
        self,
        task_id: str,
        requester_id: str,
        init_params: str,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """Create a new task_run for the given task."""
        with self.table_access_condition, self.get_connection() as conn:
            # Ensure given ids are valid
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO task_runs(
                        task_run_id,
                        task_id,
                        requester_id,
                        init_params,
                        is_completed,
                        provider_type,
                        task_type,
                        sandbox
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        int(task_id),
                        int(requester_id),
                        init_params,
                        False,
                        provider_type,
                        task_type,
                        sandbox,
                    ),
                )
                task_run_id = str(c.lastrowid)
                return task_run_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="task_runs",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_task_run(self, task_run_id: str) -> Mapping[str, Any]:
        """
        Return the given task_run's fields by task_run_id, raise EntryDoesNotExistException
        if no id exists in task_runs.

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("task_runs", "task_run_id", task_run_id)

    def _find_task_runs(
        self,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        is_completed: Optional[bool] = None,
    ) -> List[TaskRun]:
        """
        Try to find any task_run that matches the above. When called with no arguments,
        return all task_runs.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                ["task_id", "requester_id", "is_completed"],
                [nonesafe_int(task_id), nonesafe_int(requester_id), is_completed],
            )
            c.execute(
                """
                SELECT * from task_runs
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [TaskRun(self, str(r["task_run_id"]), row=r, _used_new_call=True) for r in rows]

    def _update_task_run(self, task_run_id: str, is_completed: bool):
        """
        Update a task run. At the moment, can only update completion status
        """
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    UPDATE task_runs
                    SET is_completed = ?
                    WHERE task_run_id = ?;
                    """,
                    (is_completed, int(task_run_id)),
                )
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                raise MephistoDBException(e)

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_assignment(
        self,
        task_id: str,
        task_run_id: str,
        requester_id: str,
        task_type: str,
        provider_type: str,
        sandbox: bool = True,
    ) -> str:
        """Create a new assignment for the given task"""
        # Ensure task run exists
        self.get_task_run(task_run_id)
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO assignments(
                        assignment_id,
                        task_id,
                        task_run_id,
                        requester_id,
                        task_type,
                        provider_type,
                        sandbox
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        int(task_id),
                        int(task_run_id),
                        int(requester_id),
                        task_type,
                        provider_type,
                        sandbox,
                    ),
                )
                assignment_id = str(c.lastrowid)
                return assignment_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="assignments",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_assignment(self, assignment_id: str) -> Mapping[str, Any]:
        """
        Return assignment's fields by assignment_id, raise EntryDoesNotExistException
        if no id exists in tasks

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("assignments", "assignment_id", assignment_id)

    def _find_assignments(
        self,
        task_run_id: Optional[str] = None,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[str] = None,
        sandbox: Optional[bool] = None,
    ) -> List[Assignment]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                [
                    "task_run_id",
                    "task_id",
                    "requester_id",
                    "task_type",
                    "provider_type",
                    "sandbox",
                ],
                [
                    nonesafe_int(task_run_id),
                    nonesafe_int(task_id),
                    nonesafe_int(requester_id),
                    task_type,
                    provider_type,
                    sandbox,
                ],
            )
            c.execute(
                """
                SELECT * from assignments
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [
                Assignment(self, str(r["assignment_id"]), row=r, _used_new_call=True) for r in rows
            ]

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_unit(
        self,
        task_id: str,
        task_run_id: str,
        requester_id: str,
        assignment_id: str,
        unit_index: int,
        pay_amount: float,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """
        Create a new unit with the given index. Raises EntryAlreadyExistsException
        if there is already a unit for the given assignment with the given index.
        """
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO units(
                        unit_id,
                        task_id,
                        task_run_id,
                        requester_id,
                        assignment_id,
                        unit_index,
                        pay_amount,
                        provider_type,
                        task_type,
                        sandbox,
                        status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        int(task_id),
                        int(task_run_id),
                        int(requester_id),
                        int(assignment_id),
                        unit_index,
                        pay_amount,
                        provider_type,
                        task_type,
                        sandbox,
                        AssignmentState.CREATED,
                    ),
                )
                unit_id = str(c.lastrowid)
                return unit_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="units",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_unit(self, unit_id: str) -> Mapping[str, Any]:
        """
        Return unit's fields by unit_id, raise EntryDoesNotExistException
        if no id exists in units

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("units", "unit_id", unit_id)

    def _find_units(
        self,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        unit_index: Optional[int] = None,
        provider_type: Optional[str] = None,
        task_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        sandbox: Optional[bool] = None,
        status: Optional[str] = None,
    ) -> List[Unit]:
        """
        Try to find any unit that matches the above. When called with no arguments,
        return all units.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                [
                    "task_id",
                    "task_run_id",
                    "requester_id",
                    "assignment_id",
                    "unit_index",
                    "provider_type",
                    "task_type",
                    "agent_id",
                    "worker_id",
                    "sandbox",
                    "status",
                ],
                [
                    nonesafe_int(task_id),
                    nonesafe_int(task_run_id),
                    nonesafe_int(requester_id),
                    nonesafe_int(assignment_id),
                    unit_index,
                    provider_type,
                    task_type,
                    nonesafe_int(agent_id),
                    nonesafe_int(worker_id),
                    sandbox,
                    status,
                ],
            )
            c.execute(
                """
                SELECT * from units
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [Unit(self, str(r["unit_id"]), row=r, _used_new_call=True) for r in rows]

    def _clear_unit_agent_assignment(self, unit_id: str) -> None:
        """
        Update the given unit by removing the agent that is assigned to it, thus updating
        the status to assignable.
        """
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    UPDATE units
                    SET agent_id = ?, worker_id = ?, status = ?
                    WHERE unit_id = ?;
                    """,
                    (None, None, AssignmentState.LAUNCHED, int(unit_id)),
                )
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(
                        f"Given unit_id {unit_id} not found in the database"
                    )
                raise MephistoDBException(e)

    def _update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """
        Update the given unit with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        if status not in AssignmentState.valid_unit():
            raise MephistoDBException(f"Invalid status {status} for a unit")
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                if agent_id is not None:
                    c.execute(
                        """
                        UPDATE units
                        SET agent_id = ?
                        WHERE unit_id = ?;
                        """,
                        (int(agent_id), int(unit_id)),
                    )
                if status is not None:
                    c.execute(
                        """
                        UPDATE units
                        SET status = ?
                        WHERE unit_id = ?;
                        """,
                        (status, int(unit_id)),
                    )
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(
                        f"Given unit_id {unit_id} not found in the database"
                    )
                raise MephistoDBException(e)

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_requester(self, requester_name: str, provider_type: str) -> str:
        """
        Create a new requester with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a requester with this name
        """
        if requester_name == "":
            raise MephistoDBException("Empty string is not a valid requester name")
        assert_valid_provider(provider_type)
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO requesters(
                        requester_id,
                        requester_name,
                        provider_type
                    ) VALUES (?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        requester_name,
                        provider_type,
                    ),
                )
                requester_id = str(c.lastrowid)
                return requester_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="requesters",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_requester(self, requester_id: str) -> Mapping[str, Any]:
        """
        Return requester's fields by requester_id, raise EntryDoesNotExistException
        if no id exists in requesters

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("requesters", "requester_id", requester_id)

    def _find_requesters(
        self, requester_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Requester]:
        """
        Try to find any requester that matches the above. When called with no arguments,
        return all requesters.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                ["requester_name", "provider_type"], [requester_name, provider_type]
            )
            c.execute(
                """
                SELECT * from requesters
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [
                Requester(self, str(r["requester_id"]), row=r, _used_new_call=True) for r in rows
            ]

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_worker(self, worker_name: str, provider_type: str) -> str:
        """
        Create a new worker with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a worker with this name

        worker_name should be the unique identifier by which the crowd provider
        is using to keep track of this worker
        """
        if worker_name == "":
            raise MephistoDBException("Empty string is not a valid requester name")
        assert_valid_provider(provider_type)
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO workers(
                        worker_id,
                        worker_name,
                        provider_type
                    ) VALUES (?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        worker_name,
                        provider_type,
                    ),
                )
                worker_id = str(c.lastrowid)
                return worker_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="workers",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_worker(self, worker_id: str) -> Mapping[str, Any]:
        """
        Return worker's fields by worker_id, raise EntryDoesNotExistException
        if no id exists in workers

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("workers", "worker_id", worker_id)

    def _find_workers(
        self, worker_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Worker]:
        """
        Try to find any worker that matches the above. When called with no arguments,
        return all workers.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                ["worker_name", "provider_type"], [worker_name, provider_type]
            )
            c.execute(
                """
                SELECT * from workers
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [Worker(self, str(r["worker_id"]), row=r, _used_new_call=True) for r in rows]

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_agent(
        self,
        worker_id: str,
        unit_id: str,
        task_id: str,
        task_run_id: str,
        assignment_id: str,
        task_type: str,
        provider_type: str,
    ) -> str:
        """
        Create a new agent with the given name and provider type.
        Raises EntryAlreadyExistsException if there is already an agent with this name
        """
        assert_valid_provider(provider_type)
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO agents(
                        agent_id,
                        worker_id,
                        unit_id,
                        task_id,
                        task_run_id,
                        assignment_id,
                        task_type,
                        provider_type,
                        status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        int(worker_id),
                        int(unit_id),
                        int(task_id),
                        int(task_run_id),
                        int(assignment_id),
                        task_type,
                        provider_type,
                        AgentState.STATUS_NONE,
                    ),
                )
                agent_id = str(c.lastrowid)
                c.execute(
                    """
                    UPDATE units
                    SET status = ?, agent_id = ?, worker_id = ?
                    WHERE unit_id = ?;
                    """,
                    (
                        AssignmentState.ASSIGNED,
                        int(agent_id),
                        int(worker_id),
                        int(unit_id),
                    ),
                )
                return agent_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="agents",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_agent(self, agent_id: str) -> Mapping[str, Any]:
        """
        Return agent's fields by agent_id, raise EntryDoesNotExistException
        if no id exists in agents.

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("agents", "agent_id", agent_id)

    def _update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """
        Update the given task with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        if status not in AgentState.valid():
            raise MephistoDBException(f"Invalid status {status} for an agent")

        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                UPDATE agents
                SET status = ?
                WHERE agent_id = ?;
                """,
                (status, int(agent_id)),
            )

    def _find_agents(
        self,
        status: Optional[str] = None,
        unit_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[str] = None,
    ) -> List[Agent]:
        """
        Try to find any agent that matches the above. When called with no arguments,
        return all agents.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                [
                    "status",
                    "unit_id",
                    "worker_id",
                    "task_id",
                    "task_run_id",
                    "assignment_id",
                    "task_type",
                    "provider_type",
                ],
                [
                    status,
                    nonesafe_int(unit_id),
                    nonesafe_int(worker_id),
                    nonesafe_int(task_id),
                    nonesafe_int(task_run_id),
                    nonesafe_int(assignment_id),
                    task_type,
                    provider_type,
                ],
            )
            c.execute(
                """
                SELECT * from agents
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [Agent(self, str(r["agent_id"]), row=r, _used_new_call=True) for r in rows]

    def _make_qualification(
        self, qualification_name: str, description: Optional[str] = None
    ) -> str:
        """
        Make a new qualification, throws an error if a qualification by the given name
        already exists. Return the id for the qualification.
        """
        if qualification_name == "":
            raise MephistoDBException("Empty string is not a valid qualification name")
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO qualifications(qualification_name, description) VALUES (?, ?);",
                    (qualification_name, description),
                )
                qualification_id = str(c.lastrowid)
                return qualification_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="units",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _find_qualifications(self, qualification_name: Optional[str] = None) -> List[Qualification]:
        """
        Find a qualification. If no name is supplied, returns all qualifications.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                ["qualification_name"], [qualification_name]
            )
            c.execute(
                """
                SELECT * from qualifications
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [
                Qualification(self, str(r["qualification_id"]), row=r, _used_new_call=True)
                for r in rows
            ]

    def _get_qualification(self, qualification_id: str) -> Mapping[str, Any]:
        """
        Return qualification's fields by qualification_id, raise
        EntryDoesNotExistException if no id exists in qualifications

        See Qualification for the expected fields for the returned mapping
        """
        return self.__get_one_by_id("qualifications", "qualification_id", qualification_id)

    def _delete_qualification(self, qualification_name: str) -> None:
        """
        Remove this qualification from all workers that have it, then delete the qualification
        """
        qualifications = self.find_qualifications(qualification_name=qualification_name)
        if len(qualifications) == 0:
            raise EntryDoesNotExistException(f"No qualification found by name {qualification_name}")
        qualification = qualifications[0]
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM granted_qualifications WHERE qualification_id = ?1;",
                (int(qualification.db_id),),
            )
            c.execute(
                "DELETE FROM qualifications WHERE qualification_name = ?1;",
                (qualification_name,),
            )

    def _update_qualification(
        self,
        qualification_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> None:
        """
        Update the given qualification with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    UPDATE qualifications
                    SET qualification_name = ?2, description = ?3
                    WHERE qualification_id = ?1;
                    """,
                    [
                        nonesafe_int(qualification_id),
                        name,
                        description,
                    ],
                )
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(
                        f"Given qualification_id {qualification_id} not found in the database"
                    )
                raise MephistoDBException(e)

    def _grant_qualification(self, qualification_id: str, worker_id: str, value: int = 1) -> None:
        """
        Grant a worker the given qualification. Update the qualification value if it
        already exists
        """
        # Note that better syntax exists for python 3.8+, as described in PR #223
        try:
            # Update existing entry
            qual_row = self.get_granted_qualification(qualification_id, worker_id)
            with self.table_access_condition, self.get_connection() as conn:
                if value != qual_row["value"]:
                    c = conn.cursor()
                    c.execute(
                        """
                        UPDATE granted_qualifications
                        SET value = ?
                        WHERE (qualification_id = ?)
                        AND (worker_id = ?);
                        """,
                        (value, int(qualification_id), int(worker_id)),
                    )
                    conn.commit()
                    return None
        except EntryDoesNotExistException:
            with self.table_access_condition, self.get_connection() as conn:
                c = conn.cursor()
                try:
                    c.execute(
                        """
                        INSERT INTO granted_qualifications(
                            qualification_id,
                            worker_id,
                            value
                        ) VALUES (?, ?, ?);
                        """,
                        (int(qualification_id), int(worker_id), value),
                    )
                    conn.commit()
                    return None
                except sqlite3.IntegrityError as e:
                    if is_unique_failure(e):
                        raise EntryAlreadyExistsException(
                            e,
                            db=self,
                            table_name="units",
                            original_exc=e,
                        )
                    raise MephistoDBException(e)

    def _check_granted_qualifications(
        self,
        qualification_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        value: Optional[int] = None,
    ) -> List[GrantedQualification]:
        """
        Find granted qualifications that match the given specifications
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from granted_qualifications
                WHERE (?1 IS NULL OR qualification_id = ?1)
                AND (?2 IS NULL OR worker_id = ?2)
                AND (?3 IS NULL OR value = ?3)
                """,
                (qualification_id, worker_id, value),
            )
            rows = c.fetchall()
            return [
                GrantedQualification(
                    self,
                    str(r["qualification_id"]),
                    str(r["worker_id"]),
                    row=r,
                )
                for r in rows
            ]

    def _get_granted_qualification(
        self, qualification_id: str, worker_id: str
    ) -> Mapping[str, Any]:
        """
        Return the granted qualification in the database between the given
        worker and qualification id

        See GrantedQualification for the expected fields for the returned mapping
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                f"""
                SELECT * FROM granted_qualifications
                WHERE (qualification_id = ?1)
                AND (worker_id = ?2);
                """,
                (nonesafe_int(qualification_id), nonesafe_int(worker_id)),
            )
            results = c.fetchall()
            if len(results) != 1:
                raise EntryDoesNotExistException(
                    f"No such granted qualification {qualification_id}, {worker_id}"
                )
            return results[0]

    def _revoke_qualification(self, qualification_id: str, worker_id: str) -> None:
        """
        Remove the given qualification from the given worker
        """
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                DELETE FROM granted_qualifications
                WHERE (qualification_id = ?1)
                AND (worker_id = ?2);
                """,
                (int(qualification_id), int(worker_id)),
            )

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_onboarding_agent(
        self, worker_id: str, task_id: str, task_run_id: str, task_type: str
    ) -> str:
        """
        Create a new agent for the given worker id to assign to the given unit
        Raises EntryAlreadyExistsException
        """
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO onboarding_agents(
                        onboarding_agent_id,
                        worker_id,
                        task_id,
                        task_run_id,
                        task_type,
                        status
                    ) VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        make_randomized_int_id(),
                        int(worker_id),
                        int(task_id),
                        int(task_run_id),
                        task_type,
                        AgentState.STATUS_NONE,
                    ),
                )
                return str(c.lastrowid)
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="onboarding_agents",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _get_onboarding_agent(self, onboarding_agent_id: str) -> Mapping[str, Any]:
        """
        Return onboarding agent's fields by onboarding_agent_id, raise
        EntryDoesNotExistException if no id exists in onboarding_agents

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("onboarding_agents", "onboarding_agent_id", onboarding_agent_id)

    def _update_onboarding_agent(
        self, onboarding_agent_id: str, status: Optional[str] = None
    ) -> None:
        """
        Update the given onboarding agent with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        if status not in AgentState.valid():
            raise MephistoDBException(f"Invalid status {status} for an agent")
        with self.table_access_condition, self.get_connection() as conn:
            c = conn.cursor()
            if status is not None:
                c.execute(
                    """
                    UPDATE onboarding_agents
                    SET status = ?
                    WHERE onboarding_agent_id = ?;
                    """,
                    (status, int(onboarding_agent_id)),
                )

    def _find_onboarding_agents(
        self,
        status: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_run_id: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[OnboardingAgent]:
        """
        Try to find any onboarding agent that matches the above. When called with no arguments,
        return all onboarding agents.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            additional_query, arg_tuple = self.__create_query_and_tuple(
                [
                    "status",
                    "worker_id",
                    "task_id",
                    "task_run_id",
                    "task_type",
                ],
                [
                    status,
                    nonesafe_int(worker_id),
                    nonesafe_int(task_id),
                    nonesafe_int(task_run_id),
                    task_type,
                ],
            )
            c.execute(
                """
                SELECT * from onboarding_agents
                """
                + additional_query
                + " ORDER BY creation_date ASC",
                arg_tuple,
            )
            rows = c.fetchall()
            return [
                OnboardingAgent(self, str(r["onboarding_agent_id"]), row=r, _used_new_call=True)
                for r in rows
            ]

    @retry_generate_id(caught_excs=[EntryAlreadyExistsException])
    def _new_worker_review(
        self,
        worker_id: Union[int, str],
        status: Optional[str] = None,
        task_id: Optional[Union[int, str]] = None,
        unit_id: Optional[Union[int, str]] = None,
        qualification_id: Optional[Union[int, str]] = None,
        value: Optional[int] = None,
        review_note: Optional[str] = None,
        bonus: Optional[str] = None,
        revoke: bool = False,
    ) -> None:
        """Create worker review"""

        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO worker_review (
                        id,
                        unit_id,
                        worker_id,
                        task_id,
                        updated_qualification_id,
                        updated_qualification_value,
                        revoked_qualification_id,
                        status,
                        review_note,
                        bonus
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    [
                        make_randomized_int_id(),
                        nonesafe_int(unit_id),
                        nonesafe_int(worker_id),
                        nonesafe_int(task_id),
                        nonesafe_int(qualification_id) if not revoke else None,
                        value,
                        nonesafe_int(qualification_id) if revoke else None,
                        status,
                        review_note,
                        bonus,
                    ],
                )
                conn.commit()
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        e,
                        db=self,
                        table_name="worker_review",
                        original_exc=e,
                    )
                raise MephistoDBException(e)

    def _update_worker_review(
        self,
        unit_id: Union[int, str],
        qualification_id: Union[int, str],
        worker_id: Union[int, str],
        value: Optional[int] = None,
        revoke: bool = False,
    ) -> None:
        """
        Update the given worker review with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        with self.table_access_condition:
            conn = self.get_connection()
            c = conn.cursor()

            c.execute(
                """
                SELECT * FROM worker_review
                WHERE (unit_id = ?) AND (worker_id = ?)
                ORDER BY creation_date ASC;
                """,
                [
                    nonesafe_int(unit_id),
                    nonesafe_int(worker_id),
                ],
            )
            results = c.fetchall()
            if not results:
                raise EntryDoesNotExistException(
                    f"`worker_review` was not created for this `unit_id={unit_id}`"
                )

            latest_worker_review = results[-1]
            latest_worker_review_id = latest_worker_review["id"]

            has_entry_with_qualification = (
                latest_worker_review["updated_qualification_id"]
                or latest_worker_review["revoked_qualification_id"]
            )

            if not has_entry_with_qualification:
                # Update just created entry when unit was approved
                c.execute(
                    """
                    UPDATE worker_review
                    SET
                        updated_qualification_id = ?,
                        updated_qualification_value = ?,
                        revoked_qualification_id = ?
                    WHERE id = ?;
                    """,
                    (
                        nonesafe_int(qualification_id) if not revoke else None,
                        value,
                        nonesafe_int(qualification_id) if revoke else None,
                        nonesafe_int(latest_worker_review_id),
                    ),
                )
                conn.commit()
            else:
                # If we try to update entry for the same unit,
                # but it was already assigned to another qualifications,
                # create a new entry with the same data, but with another qualification and value
                self._new_worker_review(
                    worker_id=worker_id,
                    status=latest_worker_review["status"],
                    task_id=latest_worker_review["task_id"],
                    unit_id=unit_id,
                    qualification_id=qualification_id,
                    value=value,
                    review_note=latest_worker_review["review_note"],
                    bonus=latest_worker_review["bonus"],
                )

    # File/blob manipulation methods

    def _assert_path_in_domain(self, path_key: str) -> None:
        """Helper method to ensure we only manage data we're supposed to"""
        assert path_key.startswith(
            self.db_root
        ), f"Accessing invalid key {path_key} for root {self.db_root}"

    def write_dict(self, path_key: str, target_dict: Dict[str, Any]):
        """Write an object to the given key"""
        self._assert_path_in_domain(path_key)
        os.makedirs(os.path.dirname(path_key), exist_ok=True)
        with open(path_key, "w+") as data_file:
            json.dump(target_dict, data_file)

    def read_dict(self, path_key: str) -> Dict[str, Any]:
        """Return the dict loaded from the given path key"""
        self._assert_path_in_domain(path_key)
        with open(path_key, "r") as data_file:
            return json.load(data_file)

    def write_text(self, path_key: str, data_string: str):
        """Write the given text to the given key"""
        self._assert_path_in_domain(path_key)
        os.makedirs(os.path.dirname(path_key), exist_ok=True)
        with open(path_key, "w+") as data_file:
            data_file.write(data_string)

    def read_text(self, path_key: str) -> str:
        """Get text data stored at the given key"""
        self._assert_path_in_domain(path_key)
        with open(path_key, "r") as data_file:
            return data_file.read()

    def key_exists(self, path_key: str) -> bool:
        """See if the given path refers to a known file"""
        self._assert_path_in_domain(path_key)
        return os.path.exists(path_key)
