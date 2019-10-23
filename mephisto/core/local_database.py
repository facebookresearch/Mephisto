#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.database import (
    MephistoDB,
    MephistoDBException,
    EntryAlreadyExistsException,
    EntryDoesNotExistException,
)
from typing import Mapping, Optional, Any, List
from mephisto.core.utils import get_data_dir
from mephisto.data_model.agent import Agent
from mephisto.data_model.assignment import Assignment, Unit
from mephisto.data_model.project import Project
from mephisto.data_model.requester import Requester
from mephisto.data_model.task import Task, TaskRun
from mephisto.data_model.worker import Worker

import sqlite3
from sqlite3 import Connection, Cursor
import threading


def nonesafe_int(in_string: Optional[str]) -> Optional[int]:
    """Cast input to an int or None"""
    if in_string is None:
        return None
    return int(in_string)


CREATE_PROJECTS_TABLE = """CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name STRING NOT NULL UNIQUE,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TASKS_TABLE = """CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name STRING NOT NULL UNIQUE,
    task_type STRING NOT NULL,
    project_id INTEGER,
    parent_task_id INTEGER,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
);
"""

CREATE_REQUESTERS_TABLE = """CREATE TABLE IF NOT EXISTS requesters (
    requester_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_name STRING NOT NULL UNIQUE,
    provider_type STRING NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TASK_RUNS_TABLE = """CREATE TABLE IF NOT EXISTS task_runs (
    task_run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL,
    init_params STRING NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (requester_id) REFERENCES requesters (requester_id)
);
"""

CREATE_ASSIGNMENTS_TABLE = """CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_run_id INTEGER NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_run_id) REFERENCES task_runs (task_id)
);
"""

CREATE_UNITS_TABLE = """CREATE TABLE IF NOT EXISTS units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    unit_index INTEGER NOT NULL,
    pay_amount FLOAT NOT NULL,
    provider_type STRING NOT NULL,
    status STRING NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id)
);
"""

CREATE_WORKERS_TABLE = """CREATE TABLE IF NOT EXISTS workers (
    worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_type STRING NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_AGENTS_TABLE = """CREATE TABLE IF NOT EXISTS agents (
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    task_type STRING NOT NULL,
    provider_type STRING NOT NULL,
    status STRING NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
    FOREIGN KEY (unit_id) REFERENCES units (unit_id)
);
"""


class LocalMephistoDB(MephistoDB):
    """
    Local database for core Mephisto data storage, the LocalMephistoDatabase handles
    grounding all of the python interactions with the Mephisto architecture to
    local files and a database.
    """

    def __init__(self, file_name='database.db'):
        self.db_path = os.path.join(get_data_dir(), file_name)
        self.conn: Dict[int, Connection] = {}
        self.table_access_condition = threading.Condition()
        self.init_tables()

    def _get_connection(self) -> Connection:
        """Returns a singular database connection to be shared amongst all
        calls for a given thread.
        """
        # TODO is there a problem with having just one db connection?
        # Will this cause bugs with failed commits?
        curr_thread = threading.get_ident()
        if curr_thread not in self.conn or self.conn[curr_thread] is None:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                self.conn[curr_thread] = conn
            except sqlite3.Error as e:
                raise MephistoDBException(e)
        return self.conn[curr_thread]

    def init_tables(self) -> None:
        """
        Run all the table creation SQL queries to ensure the expected tables exist
        """
        # TODO maybe raise flag when the schema of existing tables isn't what we expect
        # it to be?
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(CREATE_PROJECTS_TABLE)
            c.execute(CREATE_TASKS_TABLE)
            c.execute(CREATE_REQUESTERS_TABLE)
            c.execute(CREATE_TASK_RUNS_TABLE)
            c.execute(CREATE_ASSIGNMENTS_TABLE)
            c.execute(CREATE_UNITS_TABLE)
            c.execute(CREATE_WORKERS_TABLE)
            c.execute(CREATE_AGENTS_TABLE)
            conn.commit()

    def __get_one_by_id(self, table_name: str, id_name: str, db_id: str) -> Mapping[str, Any]:
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
                (db_id),
            )
            results = c.fetchall()
            if len(results) != 1:
                raise EntryDoesNotExistException
            return results[0]

    def new_project(self, project_name: str) -> str:
        """
        Create a new project with the given project name. Raise EntryAlreadyExistsException if a project
        with this name has already been created.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            try:
                c.execute(
                    'INSERT INTO projects(project_name) VALUES (?);',
                    (project_name, ),
                )
                project_id = str(c.lastrowid)
                conn.commit()
                return project_id
            except sqlite3.IntegrityError:
                # TODO formally check that the entry already existed? Check other exceptions?
                conn.rollback()
                raise EntryAlreadyExistsException()

    def get_project(self, project_id: str) -> Mapping[str, Any]:
        """
        Return project's fields by the given project_id, raise EntryDoesNotExistException
        if no id exists in projects

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('projects', 'project_id', int(project_id))

    def find_projects(
        self, project_name: Optional[str] = None
    ) -> List[Project]:
        """
        Try to find any project that matches the above. When called with no arguments,
        return all projects.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT project_id from projects
                WHERE (?1 IS NULL OR project_name = ?1)
                """,
                (project_name, ),
            )
            rows = c.fetchall()
            return [Project(self, r['project_id']) for r in rows]

    def new_task(
        self,
        task_name: str,
        task_type: str,
        project_id: Optional[str],
        parent_task_id: Optional[str],
    ) -> str:
        """
        Create a new task with the given task name. Raise EntryAlreadyExistsException if a task
        with this name has already been created.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            project_id = nonesafe_int(project_id)
            parent_task_id = nonesafe_int(parent_task_id)
            try:
                c.execute(
                    '''INSERT INTO tasks(
                        task_name,
                        task_type,
                        project_id,
                        parent_task_id
                    ) VALUES (?, ?, ?, ?);''',
                    (
                        task_name,
                        task_type,
                        int(project_id),
                        int(parent_task_id),
                    ),
                )
                task_id = str(c.lastrowid)
                conn.commit()
                return task_id
            except sqlite3.IntegrityError:
                # TODO formally check that the entry already existed? Check other exceptions?
                conn.rollback()
                raise EntryAlreadyExistsException()

    def get_task(self, task_id: str) -> Mapping[str, Any]:
        """
        Return task's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('tasks', 'task_id', int(task_id))

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
            project_id = nonesafe_int(project_id)
            parent_task_id = nonesafe_int(parent_task_id)
            c.execute(
                """
                SELECT task_id from tasks
                WHERE (?1 IS NULL OR task_name = ?1)
                AND (?2 IS NULL OR project_id = ?2)
                AND (?3 IS NULL OR parent_project_id = ?3)
                """,
                (task_name, project_id, parent_task_id),
            )
            rows = c.fetchall()
            return [Task(self, r['task_id']) for r in rows]

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
                'Cannot edit a task that has already been run, for risk of data corruption.'
            )
        with self.table_access_condition:
            conn = self._get_connection()
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
                conn.commit()
            except sqlite3.IntegrityError:
                # TODO formally check that the entry already existed? Check other exceptions?
                conn.rollback()
                raise EntryAlreadyExistsException()

    def new_task_run(self, task_id: str, requester_id: str, init_params: str) -> str:
        """Create a new task_run for the given task."""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """INSERT INTO task_runs(task_id, requester_id, init_params)
                VALUES (?, ?, ?);""",
                (int(task_id), int(requester_id), init_params),
            )
            task_run_id = str(c.lastrowid)
            conn.commit()
            return task_run_id

    def get_task_run(self, task_run_id: str) -> Mapping[str, Any]:
        """
        Return the given task_run's fields by task_run_id, raise EntryDoesNotExistException if no id exists
        in task_runs.

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('task_runs', 'task_run_id', int(task_run_id))

    def find_task_runs(
        self,
        task_id: Optional[str] = None,
        requester_id: Optional[str] = None,
    ) -> List[TaskRun]:
        """
        Try to find any task_run that matches the above. When called with no arguments,
        return all task_runs.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            task_id = nonesafe_int(task_id)
            requester_id = nonesafe_int(requester_id)
            c.execute(
                """
                SELECT task_run_id from task_runs
                WHERE (?1 IS NULL OR task_id = ?1)
                AND (?2 IS NULL OR requester_id = ?2)
                """,
                (task_id, requester_id),
            )
            rows = c.fetchall()
            return [TaskRun(self, r['task_id']) for r in rows]

    def new_assignment(self, task_run_id: str) -> str:
        """
        Create a new assignment for the given task

        Assignments should not be edited or altered once created
        """
        raise NotImplementedError()

    def get_assignment(self, task_id: str) -> Mapping[str, Any]:
        """
        Return assignment's fields by task_id, raise EntryDoesNotExistException if no id exists
        in tasks

        See Assignment for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    def find_assignments(self, task_run_id: Optional[str] = None) -> List[Assignment]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        raise NotImplementedError()

    def new_unit(
        self, assignment_id: str, unit_index: int, pay_amount: float, provider_type: str
    ) -> str:
        """
        Create a new unit with the given index. Raises EntryAlreadyExistsException
        if there is already a unit for the given assignment with the given index.
        """
        raise NotImplementedError()

    def get_unit(self, unit_id: str) -> Mapping[str, Any]:
        """
        Return unit's fields by unit_id, raise EntryDoesNotExistException
        if no id exists in units

        See unit for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    def find_units(
        self,
        assignment_id: Optional[str] = None,
        index: Optional[int] = None,
        agent_id: Optional[str] = None,
    ) -> List[Unit]:
        """
        Try to find any unit that matches the above. When called with no arguments,
        return all units.
        """
        raise NotImplementedError()

    def update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        raise NotImplementedError()

    def new_requester(self, requester_name: str, provider_type: str) -> str:
        """
        Create a new requester with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a requester with this name
        """
        # TODO ensure that provider type is a valid type
        raise NotImplementedError()

    def get_requester(self, requester_id: str) -> Mapping[str, Any]:
        """
        Return requester's fields by requester_id, raise EntryDoesNotExistException
        if no id exists in requesters

        See requester for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    def find_requesters(
        self, requester_name: Optional[str] = None, provider_type: Optional[str] = None
    ) -> List[Requester]:
        """
        Try to find any requester that matches the above. When called with no arguments,
        return all requesters.
        """
        raise NotImplementedError()

    def new_worker(self, worker_name: str, provider_type: str) -> str:
        """
        Create a new worker with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a worker with this name
        """
        # TODO ensure that provider type is a valid type
        raise NotImplementedError()

    def get_worker(self, worker_id: str) -> Mapping[str, Any]:
        """
        Return worker's fields by worker_id, raise EntryDoesNotExistException
        if no id exists in workers

        See worker for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    def find_workers(self, provider_type: Optional[str] = None) -> List[Worker]:
        """
        Try to find any worker that matches the above. When called with no arguments,
        return all workers.
        """
        raise NotImplementedError()

    def new_agent(
        self, worker_id: str, unit_id: str, task_type: str, provider_type: str
    ) -> str:
        """
        Create a new agent with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a agent with this name
        """
        # TODO ensure that provider type is a valid type
        raise NotImplementedError()

    def get_agent(self, agent_id: str) -> Mapping[str, Any]:
        """
        Return agent's fields by agent_id, raise EntryDoesNotExistException
        if no id exists in agents

        See Agent for the expected fields for the returned mapping
        """
        raise NotImplementedError()

    def update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        raise NotImplementedError()

    def find_agents(
        self,
        status: Optional[str] = None,
        unit_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        task_type: Optional[str] = None,
        provider_type: Optional[int] = None,
    ) -> List[Agent]:
        """
        Try to find any agent that matches the above. When called with no arguments,
        return all agents.
        """
        raise NotImplementedError()
