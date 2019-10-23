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
from mephisto.core.utils import get_data_dir, get_valid_provider_types
from mephisto.data_model.agent import Agent, AgentState
from mephisto.data_model.assignment import Assignment, Unit, AssignmentState
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


def assert_valid_provider(provider_type: str) -> None:
    """Throw an assertion error if the given provider type is not valid"""
    valid_types = get_valid_provider_types()
    assert provider_type in valid_types, f"Supplied provider {provider_type} is not in supported list of providers {valid_types}."


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
    agent_id STRING,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id),
    FOREIGN KEY (agent_id) REFERENCES agents (agent_id),
    UNIQUE (assignment_id, unit_index)
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


# TODO find_x queries are pretty slow right now, as we query the same table once to get
# all of the rows, but only select the ids, then we later construct them individually, making
# a second set of requests.
# It would be better to expose an init param for DB Objects that takes in the full row
# and inits with that if provided, and queries the database if not.
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
            return [TaskRun(self, r['task_run_id']) for r in rows]

    def new_assignment(self, task_run_id: str) -> str:
        """Create a new assignment for the given task"""
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'INSERT INTO assignments(task_run_id) VALUES (?);',
                (int(task_run_id), ),
            )
            assignment_id = str(c.lastrowid)
            conn.commit()
            return assignment_id

    def get_assignment(self, assignment_id: str) -> Mapping[str, Any]:
        """
        Return assignment's fields by assignment_id, raise EntryDoesNotExistException
        if no id exists in tasks

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('assignments', 'assignment_id', int(assignment_id))

    def find_assignments(self, task_run_id: Optional[str] = None) -> List[Assignment]:
        """
        Try to find any task that matches the above. When called with no arguments,
        return all tasks.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            task_run_id = nonesafe_int(task_run_id)
            c.execute(
                """
                SELECT assignment_id from assignments
                WHERE (?1 IS NULL OR task_run_id = ?1)
                """,
                (task_run_id, ),
            )
            rows = c.fetchall()
            return [Assignment(self, r['assignment_id']) for r in rows]

    def new_unit(
        self, assignment_id: str, unit_index: int, pay_amount: float, provider_type: str
    ) -> str:
        """
        Create a new unit with the given index. Raises EntryAlreadyExistsException
        if there is already a unit for the given assignment with the given index.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            try:
                c.execute(
                    '''INSERT INTO units(
                        assignment_id,
                        unit_index,
                        pay_amount,
                        provider_type,
                        status
                    ) VALUES (?, ?, ?, ?, ?);''',
                    (
                        int(assignment_id),
                        unit_index,
                        pay_amount,
                        provider_type,
                        AssignmentState.CREATED,
                    ),
                )
                unit_id = str(c.lastrowid)
                conn.commit()
                return unit_id
            except sqlite3.IntegrityError:
                # TODO formally check that the entry already existed? Check other exceptions?
                conn.rollback()
                raise EntryAlreadyExistsException()

    def get_unit(self, unit_id: str) -> Mapping[str, Any]:
        """
        Return unit's fields by unit_id, raise EntryDoesNotExistException
        if no id exists in units

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('units', 'unit_id', int(unit_id))

    def find_units(
        self,
        assignment_id: Optional[str] = None,
        unit_index: Optional[int] = None,
        provider_type: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> List[Unit]:
        """
        Try to find any unit that matches the above. When called with no arguments,
        return all units.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            assignment_id = nonesafe_int(assignment_id)
            agent_id = nonesafe_int(agent_id)
            c.execute(
                """
                SELECT unit_id from units
                WHERE (?1 IS NULL OR assignment_id = ?1)
                AND (?2 IS NULL OR unit_index = ?2)
                AND (?3 IS NULL OR provider_type = ?3)
                AND (?4 IS NULL OR agent_id = ?4)
                """,
                (assignment_id, unit_index, provider_type, agent_id),
            )
            rows = c.fetchall()
            return [Unit(self, r['unit_id']) for r in rows]

    def update_unit(
        self, unit_id: str, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        assert status in AssignmentState.valid_unit(), f'Invalid status {status} for a unit'
        with self.table_access_condition:
            conn = self._get_connection()
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
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()
                raise MephistoDBException(f'Given agent_id {agent_id} not found in the database')

    def new_requester(self, requester_name: str, provider_type: str) -> str:
        """
        Create a new requester with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a requester with this name
        """
        assert_valid_provider(provider_type)
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            try:
                c.execute(
                    'INSERT INTO requesters(requester_name, provider_type) VALUES (?, ?);',
                    (requester_name, provider_type),
                )
                requester_id = str(c.lastrowid)
                conn.commit()
                return requester_id
            except sqlite3.IntegrityError:
                # TODO formally check that the entry already existed? Check other exceptions?
                conn.rollback()
                raise EntryAlreadyExistsException()

    def get_requester(self, requester_id: str) -> Mapping[str, Any]:
        """
        Return requester's fields by requester_id, raise EntryDoesNotExistException
        if no id exists in requesters

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('requesters', 'requester_id', int(requester_id))

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
                SELECT requester_id from requesters
                WHERE (?1 IS NULL OR requester_name = ?1)
                AND (?2 IS NULL OR provider_type = ?2)
                """,
                (requester_name, provider_type),
            )
            rows = c.fetchall()
            return [Requester(self, r['requester_id']) for r in rows]

    def new_worker(self, worker_name: str, provider_type: str) -> str:
        """
        Create a new worker with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a worker with this name

        worker_name should be the unique identifier by which the crowd provider
        is using to keep track of this worker
        """
        assert_valid_provider(provider_type)
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            try:
                c.execute(
                    'INSERT INTO workers(worker_name, provider_type) VALUES (?, ?);',
                    (worker_name, provider_type),
                )
                worker_id = str(c.lastrowid)
                conn.commit()
                return worker_id
            except sqlite3.IntegrityError:
                # TODO formally check that the entry already existed? Check other exceptions?
                conn.rollback()
                raise EntryAlreadyExistsException()

    def get_worker(self, worker_id: str) -> Mapping[str, Any]:
        """
        Return worker's fields by worker_id, raise EntryDoesNotExistException
        if no id exists in workers

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('workers', 'worker_id', int(worker_id))

    def find_workers(self, provider_type: Optional[str] = None) -> List[Worker]:
        """
        Try to find any worker that matches the above. When called with no arguments,
        return all workers.
        """
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                """
                SELECT worker_id from workers
                WHERE (?1 IS NULL OR provider_type = ?1)
                """,
                (provider_type, ),
            )
            rows = c.fetchall()
            return [Worker(self, r['task_id']) for r in rows]

    def new_agent(
        self, worker_id: str, unit_id: str, task_type: str, provider_type: str
    ) -> str:
        """
        Create a new agent with the given name and provider type.
        Raises EntryAlreadyExistsException
        if there is already a agent with this name
        """
        assert_valid_provider(provider_type)
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            try:
                c.execute(
                    '''INSERT INTO agents(
                        worker_id,
                        unit_id,
                        task_type,
                        provider_type,
                        status
                    ) VALUES (?, ?, ?, ?, ?);''',
                    (
                        int(worker_id),
                        int(unit_id),
                        task_type,
                        provider_type,
                        AgentState.STATUS_NONE
                    ),
                )
                agent_id = str(c.lastrowid)
                conn.commit()
                return agent_id
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise MephistoDBException(e)

    def get_agent(self, agent_id: str) -> Mapping[str, Any]:
        """
        Return agent's fields by agent_id, raise EntryDoesNotExistException
        if no id exists in agents

        Returns a SQLite Row object with the expected fields
        """
        return self.__get_one_by_id('agents', 'agent_id', int(agent_id))

    def update_agent(self, agent_id: str, status: Optional[str] = None) -> None:
        """
        Update the given task with the given parameters if possible, raise appropriate exception otherwise.
        """
        assert status in AgentState.valid(), f'Invalid status {status} for an agent'
        with self.table_access_condition:
            conn = self._get_connection()
            c = conn.cursor()
            try:
                if status is not None:
                    c.execute(
                        """
                        UPDATE agents
                        SET status = ?
                        WHERE agent_id = ?;
                        """,
                        (status, int(unit_id)),
                    )
                conn.commit()

    def find_agents(
        self,
        status: Optional[str] = None,
        unit_id: Optional[str] = None,
        worker_id: Optional[str] = None,
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
            unit_id = nonesafe_int(unit_id)
            worker_id = nonesafe_int(worker_id)
            c.execute(
                """
                SELECT worker_id from workers
                WHERE (?1 IS NULL OR status = ?1)
                AND (?1 IS NULL OR unit_id = ?1)
                AND (?1 IS NULL OR worker_id = ?1)
                AND (?1 IS NULL OR task_type = ?1)
                AND (?1 IS NULL OR provider_type = ?1)
                """,
                (status, unit_id, worker_id, task_type, provider_type),
            )
            rows = c.fetchall()
            return [Agent(self, r['task_id']) for r in rows]
