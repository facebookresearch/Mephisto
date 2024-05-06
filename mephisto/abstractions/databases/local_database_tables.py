#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
WARNING: In this module you can find initial table structures, but not final.
There are can be changes in migrations. To see actual fields, constraints, etc.,
see information in databases or look through all migrations for current database
"""

CREATE_IF_NOT_EXISTS_PROJECTS_TABLE = """
    CREATE TABLE IF NOT EXISTS projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL UNIQUE,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_IF_NOT_EXISTS_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS tasks (
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

CREATE_IF_NOT_EXISTS_REQUESTERS_TABLE = """
    CREATE TABLE IF NOT EXISTS requesters (
        requester_id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_name TEXT NOT NULL UNIQUE,
        provider_type TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_IF_NOT_EXISTS_TASK_RUNS_TABLE = """
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

CREATE_IF_NOT_EXISTS_ASSIGNMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS assignments (
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

CREATE_IF_NOT_EXISTS_UNITS_TABLE = """
    CREATE TABLE IF NOT EXISTS units (
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

CREATE_IF_NOT_EXISTS_WORKERS_TABLE = """
    CREATE TABLE IF NOT EXISTS workers (
        worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_name TEXT NOT NULL UNIQUE,
        provider_type TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_IF_NOT_EXISTS_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS agents (
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

CREATE_IF_NOT_EXISTS_ONBOARDING_AGENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS onboarding_agents (
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

CREATE_IF_NOT_EXISTS_QUALIFICATIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS qualifications (
        qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        qualification_name TEXT NOT NULL UNIQUE,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_IF_NOT_EXISTS_GRANTED_QUALIFICATIONS_TABLE = """
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

CREATE_IF_NOT_EXISTS_UNIT_REVIEW_TABLE = """
    CREATE TABLE IF NOT EXISTS unit_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        task_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        review_note TEXT,
        bonus INTEGER,
        blocked_worker BOOLEAN DEFAULT false,
        /* ID of `db.qualifications` (not `db.granted_qualifications`) */
        updated_qualification_id INTEGER,
        updated_qualification_value INTEGER,
        /* ID of `db.qualifications` (not `db.granted_qualifications`) */
        revoked_qualification_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (unit_id) REFERENCES units (unit_id),
        FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
        FOREIGN KEY (task_id) REFERENCES tasks (task_id)
    );
"""

CREATE_IF_NOT_EXISTS_IMPORT_DATA_TABLE = """
    CREATE TABLE IF NOT EXISTS imported_data (
        id INTEGER PRIMARY KEY,
        source_file_name TEXT NOT NULL,
        data_labels TEXT NOT NULL,
        table_name TEXT NOT NULL,
        unique_field_names TEXT NOT NULL,  /* JSON */
        unique_field_values TEXT NOT NULL,  /* JSON */
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

# WARNING: Changing this table, be careful, it will affect all datastores too
CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

# Indices that are used by system-specific calls across Mephisto during live tasks
# that improve the runtime of the system as a whole
CREATE_IF_NOT_EXISTS_CORE_INDICES = """
    CREATE INDEX IF NOT EXISTS requesters_by_provider_index ON requesters(provider_type);
    CREATE INDEX IF NOT EXISTS unit_by_status_index ON units(status);
    CREATE INDEX IF NOT EXISTS unit_by_assignment_id_index ON units(assignment_id);
    CREATE INDEX IF NOT EXISTS unit_by_task_run_index ON units(task_run_id);
    CREATE INDEX IF NOT EXISTS unit_by_task_run_by_worker_by_status_index ON units(task_run_id, worker_id, status);
    CREATE INDEX IF NOT EXISTS unit_by_task_by_worker_index ON units(task_id, worker_id);
    CREATE INDEX IF NOT EXISTS agent_by_worker_by_status_index ON agents(worker_id, status);
    CREATE INDEX IF NOT EXISTS agent_by_task_run_index ON agents(task_run_id);
    CREATE INDEX IF NOT EXISTS assignment_by_task_run_index ON assignments(task_run_id);
    CREATE INDEX IF NOT EXISTS task_run_by_requester_index ON task_runs(requester_id);
    CREATE INDEX IF NOT EXISTS task_run_by_task_index ON task_runs(task_id);
    CREATE INDEX IF NOT EXISTS unit_review_by_unit_index ON unit_review(unit_id);
"""  # noqa: E501
