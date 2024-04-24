#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
1. Rename `unit_review.created_at` -> `unit_review.creation_date`
2. Remove autoincrement parameter for all Primary Keys
3. Add missed Foreign Keys in `agents` table
4. Add `granted_qualifications.update_date`
"""


PREPARING_DB_FOR_MERGE_DBS_COMMAND = """
    ALTER TABLE unit_review RENAME COLUMN created_at TO creation_date;
    
    /* Disable FK constraints */
    PRAGMA foreign_keys = off;
    
    
    /* Projects */
    CREATE TABLE IF NOT EXISTS _projects (
        project_id INTEGER PRIMARY KEY,
        project_name TEXT NOT NULL UNIQUE,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _projects SELECT * FROM projects;
    DROP TABLE projects;
    ALTER TABLE _projects RENAME TO projects;
    
    
    /* Tasks */
    CREATE TABLE IF NOT EXISTS _tasks (
        task_id INTEGER PRIMARY KEY,
        task_name TEXT NOT NULL UNIQUE,
        task_type TEXT NOT NULL,
        project_id INTEGER,
        parent_task_id INTEGER,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id),
        FOREIGN KEY (project_id) REFERENCES projects (project_id)
    );
    INSERT INTO _tasks SELECT * FROM tasks;
    DROP TABLE tasks;
    ALTER TABLE _tasks RENAME TO tasks;
    
    
    /* Requesters */
    CREATE TABLE IF NOT EXISTS _requesters (
        requester_id INTEGER PRIMARY KEY,
        requester_name TEXT NOT NULL UNIQUE,
        provider_type TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _requesters SELECT * FROM requesters;
    DROP TABLE requesters;
    ALTER TABLE _requesters RENAME TO requesters;
    
    
    /* Task Runs */
    CREATE TABLE IF NOT EXISTS _task_runs (
        task_run_id INTEGER PRIMARY KEY,
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
    INSERT INTO _task_runs SELECT * FROM task_runs;
    DROP TABLE task_runs;
    ALTER TABLE _task_runs RENAME TO task_runs;
    
    
    /* Assignments */
    CREATE TABLE IF NOT EXISTS _assignments (
        assignment_id INTEGER PRIMARY KEY,
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
    INSERT INTO _assignments SELECT * FROM assignments;
    DROP TABLE assignments;
    ALTER TABLE _assignments RENAME TO assignments;
    
    
    /* Units */
    CREATE TABLE IF NOT EXISTS _units (
        unit_id INTEGER PRIMARY KEY,
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
    INSERT INTO _units SELECT * FROM units;
    DROP TABLE units;
    ALTER TABLE _units RENAME TO units;
    
    
    /* Workers */
    CREATE TABLE IF NOT EXISTS _workers (
        worker_id INTEGER PRIMARY KEY,
        worker_name TEXT NOT NULL UNIQUE,
        provider_type TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _workers SELECT * FROM workers;
    DROP TABLE workers;
    ALTER TABLE _workers RENAME TO workers;
    
    
    /* Agents */
    CREATE TABLE IF NOT EXISTS _agents (
        agent_id INTEGER PRIMARY KEY,
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
        FOREIGN KEY (unit_id) REFERENCES units (unit_id),
        FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE NO ACTION,
        FOREIGN KEY (task_run_id) REFERENCES task_runs (task_run_id) ON DELETE NO ACTION,
        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE NO ACTION
    );
    INSERT INTO _agents SELECT * FROM agents;
    DROP TABLE agents;
    ALTER TABLE _agents RENAME TO agents;
    
    
    /* Onboarding Agents */
    CREATE TABLE IF NOT EXISTS _onboarding_agents (
        onboarding_agent_id INTEGER PRIMARY KEY,
        worker_id INTEGER NOT NULL,
        task_id INTEGER NOT NULL,
        task_run_id INTEGER NOT NULL,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
        FOREIGN KEY (task_run_id) REFERENCES task_runs (task_run_id)
    );
    INSERT INTO _onboarding_agents SELECT * FROM onboarding_agents;
    DROP TABLE onboarding_agents;
    ALTER TABLE _onboarding_agents RENAME TO onboarding_agents;
    
    
    /* Qualifications */
    CREATE TABLE IF NOT EXISTS _qualifications (
        qualification_id INTEGER PRIMARY KEY,
        qualification_name TEXT NOT NULL UNIQUE,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _qualifications SELECT * FROM qualifications;
    DROP TABLE qualifications;
    ALTER TABLE _qualifications RENAME TO qualifications;
    
    
    /* Granted Qualifications */
    CREATE TABLE IF NOT EXISTS _granted_qualifications (
        granted_qualification_id INTEGER PRIMARY KEY,
        worker_id INTEGER NOT NULL,
        qualification_id INTEGER NOT NULL,
        value INTEGER NOT NULL,
        update_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
        FOREIGN KEY (qualification_id) REFERENCES qualifications (qualification_id),
        UNIQUE (worker_id, qualification_id)
    );
    /* Copy data from backed up table and set value from `creation_date` to `update_date` */
    INSERT INTO _granted_qualifications 
        SELECT 
            granted_qualification_id, 
            worker_id, 
            qualification_id, 
            value, 
            creation_date, 
            creation_date 
        FROM granted_qualifications;
    DROP TABLE granted_qualifications;
    ALTER TABLE _granted_qualifications RENAME TO granted_qualifications;
    
    
    /* Unit Review */
    CREATE TABLE IF NOT EXISTS _unit_review (
        id INTEGER PRIMARY KEY,
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
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (unit_id) REFERENCES units (unit_id),
        FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
        FOREIGN KEY (task_id) REFERENCES tasks (task_id)
    );
    INSERT INTO _unit_review SELECT * FROM unit_review;
    DROP TABLE unit_review;
    ALTER TABLE _unit_review RENAME TO unit_review;
    
    
    /* Enable FK constraints back */
    PRAGMA foreign_keys = on;
"""
