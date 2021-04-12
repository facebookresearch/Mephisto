#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)
from typing import Mapping, Optional, Any, List, Dict
from mephisto.operations.utils import get_data_dir
from mephisto.operations.registry import get_valid_provider_types
from mephisto.data_model.agent import Agent, AgentState, OnboardingAgent
from mephisto.data_model.unit import Unit
from mephisto.data_model.assignment import Assignment, AssignmentState
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import Qualification, GrantedQualification

import sqlite3
from sqlite3 import Connection, Cursor
import threading

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


def nonesafe_int(in_string: Optional[str]) -> Optional[int]:
    """Cast input to an int or None"""
    if in_string is None:
        return None
    return int(in_string)


def assert_valid_provider(provider_type: str) -> None:
    """Throw an assertion error if the given provider type is not valid"""
    valid_types = get_valid_provider_types()
    if provider_type not in valid_types:
        raise MephistoDBException(
            f"Supplied provider {provider_type} is not in supported list of providers {valid_types}."
        )


def is_key_failure(e: sqlite3.IntegrityError) -> bool:
    """
    Return if the given error is representing a foreign key
    failure, where an insertion was expecting something to
    exist already in the DB but it didn't.
    """
    return str(e) == "FOREIGN KEY constraint failed"


def is_unique_failure(e: sqlite3.IntegrityError) -> bool:
    """
    Return if the given error is representing a foreign key
    failure, where an insertion was expecting something to
    exist already in the DB but it didn't.
    """
    return str(e).startswith("UNIQUE constraint")


CREATE_PROJECTS_TABLE = """CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL UNIQUE,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TASKS_TABLE = """CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL UNIQUE,
    task_type TEXT NOT NULL,
    project_id INTEGER,
    parent_task_id INTEGER,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
);
"""

CREATE_REQUESTERS_TABLE = """CREATE TABLE IF NOT EXISTS requesters (
    requester_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_name TEXT NOT NULL UNIQUE,
    provider_type TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TASK_RUNS_TABLE = """
    CREATE TABLE IF NOT EXISTS task_runs (
    task_run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL,
    init_params TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL,
    provider_type TEXT NOT NULL,
    task_type TEXT NOT NULL,
    sandbox BOOLEAN NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (requester_id) REFERENCES requesters (requester_id)
);
"""

CREATE_ASSIGNMENTS_TABLE = """CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    task_run_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    sandbox BOOLEAN NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (task_run_id) REFERENCES task_runs (task_run_id),
    FOREIGN KEY (requester_id) REFERENCES requesters (requester_id)
);
"""

CREATE_UNITS_TABLE = """CREATE TABLE IF NOT EXISTS units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    unit_index INTEGER NOT NULL,
    pay_amount FLOAT NOT NULL,
    provider_type TEXT NOT NULL,
    status TEXT NOT NULL,
    agent_id INTEGER,
    worker_id INTEGER,
    task_type TEXT NOT NULL,
    task_id INTEGER NOT NULL,
    task_run_id INTEGER NOT NULL,
    sandbox BOOLEAN NOT NULL,
    requester_id INTEGER NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id),
    FOREIGN KEY (agent_id) REFERENCES agents (agent_id),
    FOREIGN KEY (task_run_id) REFERENCES task_runs (task_run_id),
    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (requester_id) REFERENCES requesters (requester_id),
    FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
    UNIQUE (assignment_id, unit_index)
);
"""

CREATE_WORKERS_TABLE = """CREATE TABLE IF NOT EXISTS workers (
    worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_name TEXT NOT NULL UNIQUE,
    provider_type TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_AGENTS_TABLE = """CREATE TABLE IF NOT EXISTS agents (
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    task_run_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    status TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
    FOREIGN KEY (unit_id) REFERENCES units (unit_id)
);
"""

CREATE_ONBOARDING_AGENTS_TABLE = """CREATE TABLE IF NOT EXISTS onboarding_agents (
    onboarding_agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    task_run_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
    FOREIGN KEY (task_run_id) REFERENCES task_runs (task_run_id)
);
"""

CREATE_QUALIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS qualifications (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    qualification_name TEXT NOT NULL UNIQUE,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_GRANTED_QUALIFICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS granted_qualifications (
    granted_qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    qualification_id INTEGER NOT NULL,
    value INTEGER NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
    FOREIGN KEY (qualification_id) REFERENCES qualifications (qualification_id),
    UNIQUE (worker_id, qualification_id)
);
"""


class StringIDRow(sqlite3.Row):
    def __getitem__(self, key: str) -> Any:
        val = super().__getitem__(key)
        if key.endswith("_id") and val is not None:
            return str(val)
        else:
            return val


# TODO(101) find_x queries are pretty slow right now, as we query the same table once to get
# all of the rows, but only select the ids, then we later construct them individually,
# making a second set of requests.
# It would be better to expose an init param for DB Objects that takes in the full row
# and inits with that if provided, and queries the database if not.
class LocalMephistoDB(MephistoDB):
    """
    Local database for core Mephisto data storage, the LocalMephistoDatabase handles
    grounding all of the python interactions with the Mephisto architecture to
    local files and a database.
    """

    def __init__(self, database_path=None):
        logger.debug(f"database path: {database_path}")
        self.conn: Dict[int, Connection] = {}
        self.table_access_condition = threading.Condition()
        super().__init__(database_path)

    def _get_connection(self) -> Connection:
        """Returns a singular database connection to be shared amongst all
        calls for a given thread.
        """
        # TODO(101) is there a problem with having just one db connection?
        # Will this cause bugs with failed commits?
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            try:
                conn = sqlite3.connect(self.db_path)
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
        # TODO(#93) maybe raise flag when the schema of existing tables isn't what we expect
        # it to be?
        # "How to know that schema changes?"
        # logger.warning("some message")
        with self.table_access_condition:
            conn = self._get_connection()
            conn.execute("PRAGMA foreign_keys = 1")
            with conn:
                c = conn.cursor()
                c.execute(CREATE_PROJECTS_TABLE)
                c.execute(CREATE_TASKS_TABLE)
                c.execute(CREATE_REQUESTERS_TABLE)
                c.execute(CREATE_TASK_RUNS_TABLE)
                c.execute(CREATE_ASSIGNMENTS_TABLE)
                c.execute(CREATE_UNITS_TABLE)
                c.execute(CREATE_WORKERS_TABLE)
                c.execute(CREATE_AGENTS_TABLE)
                c.execute(CREATE_QUALIFICATIONS_TABLE)
                c.execute(CREATE_GRANTED_QUALIFICATIONS_TABLE)
                c.execute(CREATE_ONBOARDING_AGENTS_TABLE)

    def __get_one_by_id(
        self, table_name: str, id_name: str, db_id: str
    ) -> Mapping[str, Any]:
        """
        Try to request the row for the given table and entry,
        raise EntryDoesNotExistException if it isn't present
        """
        with self.table_access_condition:
            conn = self._get_connection()
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
                raise EntryDoesNotExistException(
                    f"Table {table_name} has no {id_name} {db_id}"
                )
            return results[0]

    def new_project(self, project_name: str) -> str:
        """
        Create a new project with the given project name. Raise EntryAlreadyExistsException if a project
        with this name has already been created.
        """
        if project_name in [NO_PROJECT_NAME, ""]:
            raise MephistoDBException(f'Invalid project name "{project_name}')
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO projects(project_name) VALUES (?);", (project_name,)
                )
                project_id = str(c.lastrowid)
                return project_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException()
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(
                        f"Project {project_name} already exists"
                    )
                raise MephistoDBException(e)

    def get_project(self, project_id: str) -> Mapping[str, Any]:
        """
        Return project's fields by the given project_id, raise EntryDoesNotExistException
        if no id exists in projects

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("projects", "project_id", project_id)

    def find_projects(self, project_name: Optional[str] = None) -> List[Project]:
        """
        Try to find any project that matches the above. When called with no arguments,
        return all projects.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from projects
                WHERE (?1 IS NULL OR project_name = ?1)
                """,
                (project_name,),
            )
            rows = c.fetchall()
            return [Project(self, str(r["project_id"]), row=r) for r in rows]

    def new_task(
        self,
        task_name: str,
        task_type: str,
        project_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
    ) -> str:
        """
        Create a new task with the given task name. Raise EntryAlreadyExistsException if a task
        with this name has already been created.
        """
        if task_name in [""]:
            raise MephistoDBException(f'Invalid task name "{task_name}')
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """INSERT INTO tasks(
                        task_name,
                        task_type,
                        project_id,
                        parent_task_id
                    ) VALUES (?, ?, ?, ?);""",
                    (
                        task_name,
                        task_type,
                        nonesafe_int(project_id),
                        nonesafe_int(parent_task_id),
                    ),
                )
                task_id = str(c.lastrowid)
                return task_id
            except sqlite3.IntegrityError as e:
                if is_key_failure(e):
                    raise EntryDoesNotExistException(e)
                elif is_unique_failure(e):
                    raise EntryAlreadyExistsException(e)
                raise MephistoDBException(e)

    def get_task(self, task_id: str) -> Mapping[str, Any]:
        """
        Return task's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("tasks", "task_id", task_id)

    def find_tasks(
        self,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
    ) -> List[Task]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from tasks
                WHERE (?1 IS NULL OR task_name = ?1)
                AND (?2 IS NULL OR project_id = ?2)
                AND (?3 IS NULL OR parent_task_id = ?3)
                """,
                (task_name, nonesafe_int(project_id), nonesafe_int(parent_task_id)),
            )
            rows = c.fetchall()
            return [Task(self, str(r["task_id"]), row=r) for r in rows]

    def update_task(
        self,
        task_id: str,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.

        Tasks can only be updated if no runs exist for this task yet, otherwise there's too much state
        and we shouldn't make changes.
        """
        if len(self.find_task_runs(task_id=task_id)) != 0:
            raise MephistoDBException(
                "Cannot edit a task that has already been run, for risk of data corruption."
            )
        if task_name in [""]:
            raise MephistoDBException(f'Invalid task name "{task_name}')
        with self.table_access_condition, self._get_connection() as conn:
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
                        f"Task name {task_name} is already in use"
                    )
                raise MephistoDBException(e)

    def new_task_run(
        self,
        task_id: str,
        requester_id: str,
        init_params: str,
        provider_type: str,
        task_type: str,
        sandbox: bool = True,
    ) -> str:
        """Create a new task_run for the given task."""
        with self.table_access_condition, self._get_connection() as conn:
            # Ensure given ids are valid
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO task_runs(
                        task_id,
                        requester_id,
                        init_params,
                        is_completed,
                        provider_type,
                        task_type,
                        sandbox
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?);""",
                    (
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
                raise MephistoDBException(e)

    def get_task_run(self, task_run_id: str) -> Mapping[str, Any]:
        """
        Return the given task_run's fields by task_run_id, raise EntryDoesNotExistException if no id exists
        in task_runs.

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("task_runs", "task_run_id", task_run_id)

    def find_task_runs(
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from task_runs
                WHERE (?1 IS NULL OR task_id = ?1)
                AND (?2 IS NULL OR requester_id = ?2)
                AND (?3 IS NULL OR is_completed = ?3)
                """,
                (nonesafe_int(task_id), nonesafe_int(requester_id), is_completed),
            )
            rows = c.fetchall()
            return [TaskRun(self, str(r["task_run_id"]), row=r) for r in rows]

    def update_task_run(self, task_run_id: str, is_completed: bool):
        """
        Update a task run. At the moment, can only update completion status
        """
        with self.table_access_condition, self._get_connection() as conn:
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

    def new_assignment(
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
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO assignments(
                    task_id,
                    task_run_id,
                    requester_id,
                    task_type,
                    provider_type,
                    sandbox
                ) VALUES (?, ?, ?, ?, ?, ?);""",
                (
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

    def get_assignment(self, assignment_id: str) -> Mapping[str, Any]:
        """
        Return assignment's fields by assignment_id, raise EntryDoesNotExistException
        if no id exists in tasks

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("assignments", "assignment_id", assignment_id)

    def find_assignments(
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                    SELECT * from assignments
                    WHERE (?1 IS NULL OR task_run_id = ?1)
                    AND (?2 IS NULL OR task_id = ?2)
                    AND (?3 IS NULL OR requester_id = ?3)
                    AND (?4 IS NULL OR task_type = ?4)
                    AND (?5 IS NULL OR provider_type = ?5)
                    AND (?6 IS NULL OR sandbox = ?6)
                """,
                (
                    nonesafe_int(task_run_id),
                    nonesafe_int(task_id),
                    nonesafe_int(requester_id),
                    task_type,
                    provider_type,
                    sandbox,
                ),
            )
            rows = c.fetchall()
            return [Assignment(self, str(r["assignment_id"]), row=r) for r in rows]

    def new_unit(
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
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """INSERT INTO units(
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
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                    (
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
                    raise EntryAlreadyExistsException(e)
                raise MephistoDBException(e)

    def get_unit(self, unit_id: str) -> Mapping[str, Any]:
        """
        Return unit's fields by unit_id, raise EntryDoesNotExistException
        if no id exists in units

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("units", "unit_id", unit_id)

    def find_units(
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from units
                WHERE (?1 IS NULL OR task_id = ?1)
                AND (?2 IS NULL OR task_run_id = ?2)
                AND (?3 IS NULL OR requester_id = ?3)
                AND (?4 IS NULL OR assignment_id = ?4)
                AND (?5 IS NULL OR unit_index = ?5)
                AND (?6 IS NULL OR provider_type = ?6)
                AND (?7 IS NULL OR task_type = ?7)
                AND (?8 IS NULL OR agent_id = ?8)
                AND (?9 IS NULL OR worker_id = ?9)
                AND (?10 IS NULL OR sandbox = ?10)
                AND (?11 IS NULL OR status = ?11)
                """,
                (
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
                ),
            )
            rows = c.fetchall()
            return [Unit(self, str(r["unit_id"]), row=r) for r in rows]

    def clear_unit_agent_assignment(self, unit_id: str) -> None:
        """
        Update the given unit by removing the agent that is assigned to it, thus updating
        the status to assignable.
        """
        with self.table_access_condition, self._get_connection() as conn:
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

    def update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        if status not in AssignmentState.valid_unit():
            raise MephistoDBException(f"Invalid status {status} for a unit")
        with self.table_access_condition, self._get_connection() as conn:
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

    def new_requester(self, requester_name: str, provider_type: str) -> str:
        """
        Create a new requester with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a requester with this name
        """
        if requester_name == "":
            raise MephistoDBException("Empty string is not a valid requester name")
        assert_valid_provider(provider_type)
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO requesters(requester_name, provider_type) VALUES (?, ?);",
                    (requester_name, provider_type),
                )
                requester_id = str(c.lastrowid)
                return requester_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException()
                raise MephistoDBException(e)

    def get_requester(self, requester_id: str) -> Mapping[str, Any]:
        """
        Return requester's fields by requester_id, raise EntryDoesNotExistException
        if no id exists in requesters

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("requesters", "requester_id", requester_id)

    def find_requesters(
        self, requester_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Requester]:
        """
        Try to find any requester that matches the above. When called with no arguments,
        return all requesters.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from requesters
                WHERE (?1 IS NULL OR requester_name = ?1)
                AND (?2 IS NULL OR provider_type = ?2)
                """,
                (requester_name, provider_type),
            )
            rows = c.fetchall()
            return [Requester(self, str(r["requester_id"]), row=r) for r in rows]

    def new_worker(self, worker_name: str, provider_type: str) -> str:
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
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO workers(worker_name, provider_type) VALUES (?, ?);",
                    (worker_name, provider_type),
                )
                worker_id = str(c.lastrowid)
                return worker_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException()
                raise MephistoDBException(e)

    def get_worker(self, worker_id: str) -> Mapping[str, Any]:
        """
        Return worker's fields by worker_id, raise EntryDoesNotExistException
        if no id exists in workers

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("workers", "worker_id", worker_id)

    def find_workers(
        self, worker_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Worker]:
        """
        Try to find any worker that matches the above. When called with no arguments,
        return all workers.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from workers
                WHERE (?1 IS NULL OR worker_name = ?1)
                AND (?2 IS NULL OR provider_type = ?2)
                """,
                (worker_name, provider_type),
            )
            rows = c.fetchall()
            return [Worker(self, str(r["worker_id"]), row=r) for r in rows]

    def new_agent(
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
        Raises EntryAlreadyExistsException
        if there is already a agent with this name
        """
        assert_valid_provider(provider_type)
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """INSERT INTO agents(
                        worker_id,
                        unit_id,
                        task_id,
                        task_run_id,
                        assignment_id,
                        task_type,
                        provider_type,
                        status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                    (
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
                raise MephistoDBException(e)

    def get_agent(self, agent_id: str) -> Mapping[str, Any]:
        """
        Return agent's fields by agent_id, raise EntryDoesNotExistException
        if no id exists in agents

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id("agents", "agent_id", agent_id)

    def update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        if status not in AgentState.valid():
            raise MephistoDBException(f"Invalid status {status} for an agent")

        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                UPDATE agents
                SET status = ?
                WHERE agent_id = ?;
                """,
                (status, int(agent_id)),
            )

    def find_agents(
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from agents
                WHERE (?1 IS NULL OR status = ?1)
                AND (?2 IS NULL OR unit_id = ?2)
                AND (?3 IS NULL OR worker_id = ?3)
                AND (?4 IS NULL OR task_id = ?4)
                AND (?5 IS NULL OR task_run_id = ?5)
                AND (?6 IS NULL OR assignment_id = ?6)
                AND (?7 IS NULL OR task_type = ?7)
                AND (?8 IS NULL OR provider_type = ?8)
                """,
                (
                    status,
                    nonesafe_int(unit_id),
                    nonesafe_int(worker_id),
                    nonesafe_int(task_id),
                    nonesafe_int(task_run_id),
                    nonesafe_int(assignment_id),
                    task_type,
                    provider_type,
                ),
            )
            rows = c.fetchall()
            return [Agent(self, str(r["agent_id"]), row=r) for r in rows]

    def make_qualification(self, qualification_name: str) -> str:
        """
        Make a new qualification, throws an error if a qualification by the given name
        already exists. Return the id for the qualification.
        """
        if qualification_name == "":
            raise MephistoDBException("Empty string is not a valid qualification name")
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO qualifications(qualification_name) VALUES (?);",
                    (qualification_name,),
                )
                qualification_id = str(c.lastrowid)
                return qualification_id
            except sqlite3.IntegrityError as e:
                if is_unique_failure(e):
                    raise EntryAlreadyExistsException()
                raise MephistoDBException(e)

    def find_qualifications(
        self, qualification_name: Optional[str] = None
    ) -> List[Qualification]:
        """
        Find a qualification. If no name is supplied, returns all qualifications.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from qualifications
                WHERE (?1 IS NULL OR qualification_name = ?1)
                """,
                (qualification_name,),
            )
            rows = c.fetchall()
            return [
                Qualification(self, str(r["qualification_id"]), row=r) for r in rows
            ]

    def get_qualification(self, qualification_id: str) -> Mapping[str, Any]:
        """
        Return qualification's fields by qualification_id, raise
        EntryDoesNotExistException if no id exists in qualifications

        See Qualification for the expected fields for the returned mapping
        """
        return self.__get_one_by_id(
            "qualifications", "qualification_id", qualification_id
        )

    def _delete_qualification(self, qualification_name: str) -> None:
        """
        Remove this qualification from all workers that have it, then delete the qualification
        """
        qualifications = self.find_qualifications(qualification_name=qualification_name)
        if len(qualifications) == 0:
            raise EntryDoesNotExistException(
                f"No qualification found by name {qualification_name}"
            )
        qualification = qualifications[0]
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM granted_qualifications WHERE qualification_id = ?1;",
                (int(qualification.db_id),),
            )
            c.execute(
                "DELETE FROM qualifications WHERE qualification_name = ?1;",
                (qualification_name,),
            )

    def grant_qualification(
        self, qualification_id: str, worker_id: str, value: int = 1
    ) -> None:
        """
        Grant a worker the given qualification. Update the qualification value if it
        already exists
        """
        # Note that better syntax exists for python 3.8+, as described in PR #223
        try:
            # Update existing entry
            qual_row = self.get_granted_qualification(qualification_id, worker_id)
            with self.table_access_condition, self._get_connection() as conn:
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
            with self.table_access_condition, self._get_connection() as conn:
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
                    qualification_id = str(c.lastrowid)
                    conn.commit()
                    return None
                except sqlite3.IntegrityError as e:
                    if is_unique_failure(e):
                        raise EntryAlreadyExistsException()
                    raise MephistoDBException(e)

    def check_granted_qualifications(
        self,
        qualification_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        value: Optional[int] = None,
    ) -> List[GrantedQualification]:
        """
        Find granted qualifications that match the given specifications
        """
        with self.table_access_condition:
            conn = self._get_connection()
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
                    self, str(r["qualification_id"]), str(r["worker_id"])
                )
                for r in rows
            ]

    # TODO(101) these should not be optional
    def get_granted_qualification(
        self, qualification_id: Optional[str] = None, worker_id: Optional[str] = None
    ) -> Mapping[str, Any]:
        """
        Return the granted qualification in the database between the given
        worker and qualification id

        See GrantedQualification for the expected fields for the returned mapping
        """
        with self.table_access_condition:
            conn = self._get_connection()
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

    def revoke_qualification(self, qualification_id: str, worker_id: str) -> None:
        """
        Remove the given qualification from the given worker
        """
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """DELETE FROM granted_qualifications
                WHERE (qualification_id = ?1)
                AND (worker_id = ?2);
                """,
                (int(qualification_id), int(worker_id)),
            )

    def new_onboarding_agent(
        self, worker_id: str, task_id: str, task_run_id: str, task_type: str
    ) -> str:
        """
        Create a new agent for the given worker id to assign to the given unit
        Raises EntryAlreadyExistsException
        """
        with self.table_access_condition, self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """INSERT INTO onboarding_agents(
                        worker_id,
                        task_id,
                        task_run_id,
                        task_type,
                        status
                    ) VALUES (?, ?, ?, ?, ?);""",
                    (
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
                raise MephistoDBException(e)

    def get_onboarding_agent(self, onboarding_agent_id: str) -> Mapping[str, Any]:
        """
        Return onboarding agent's fields by onboarding_agent_id, raise
        EntryDoesNotExistException if no id exists in onboarding_agents

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id(
            "onboarding_agents", "onboarding_agent_id", onboarding_agent_id
        )

    def update_onboarding_agent(
        self, onboarding_agent_id: str, status: Optional[str] = None
    ) -> None:
        """
        Update the given onboarding agent with the given parameters if possible,
        raise appropriate exception otherwise.
        """
        if status not in AgentState.valid():
            raise MephistoDBException(f"Invalid status {status} for an agent")
        with self.table_access_condition, self._get_connection() as conn:
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

    def find_onboarding_agents(
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
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT * from onboarding_agents
                WHERE (?1 IS NULL OR status = ?1)
                AND (?2 IS NULL OR worker_id = ?2)
                AND (?3 IS NULL OR task_id = ?3)
                AND (?4 IS NULL OR task_run_id = ?4)
                AND (?5 IS NULL OR task_type = ?5)
                """,
                (
                    status,
                    nonesafe_int(worker_id),
                    nonesafe_int(task_id),
                    nonesafe_int(task_run_id),
                    task_type,
                ),
            )
            rows = c.fetchall()
            return [
                OnboardingAgent(self, str(r["onboarding_agent_id"]), row=r)
                for r in rows
            ]
