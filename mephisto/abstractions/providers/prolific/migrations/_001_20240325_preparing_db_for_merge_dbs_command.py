#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
1. Remove autoincrement parameter for all Primary Keys
2. Added `update_date` and `creation_date` in `workers` table
3. Added `creation_date` in `units` table
4. Rename field `run_id` -> `task_run_id`
5. Remove table `requesters`
"""


PREPARING_DB_FOR_MERGE_DBS_COMMAND = """
    /* Disable FK constraints */
    PRAGMA foreign_keys = off;
    
    
    /* Studies */
    CREATE TABLE IF NOT EXISTS _studies (
        id INTEGER PRIMARY KEY,
        prolific_study_id TEXT UNIQUE,
        status TEXT,
        link TEXT,
        task_run_id TEXT UNIQUE,
        assignment_time_in_seconds INTEGER NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _studies SELECT * FROM studies;
    DROP TABLE studies;
    ALTER TABLE _studies RENAME TO studies;
    
    
    /* Submissions */
    CREATE TABLE IF NOT EXISTS _submissions (
        id INTEGER PRIMARY KEY,
        prolific_submission_id TEXT UNIQUE,
        prolific_study_id TEXT,
        status TEXT DEFAULT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _submissions SELECT * FROM submissions;
    DROP TABLE submissions;
    ALTER TABLE _submissions RENAME TO submissions;
    
    
    /* Run Mappings */
    CREATE TABLE IF NOT EXISTS _run_mappings (
        id INTEGER PRIMARY KEY,
        prolific_study_id TEXT,
        run_id TEXT
    );
    INSERT INTO _run_mappings SELECT * FROM run_mappings;
    DROP TABLE run_mappings;
    ALTER TABLE _run_mappings RENAME TO run_mappings;
    
    
    /* Units */
    CREATE TABLE IF NOT EXISTS _units (
        id INTEGER PRIMARY KEY,
        unit_id TEXT UNIQUE,
        run_id TEXT,
        prolific_study_id TEXT,
        prolific_submission_id TEXT,
        is_expired BOOLEAN DEFAULT false,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    /* Copy data from backed up table and set values for `creation_date` */
    INSERT INTO _units 
        SELECT 
            id, 
            unit_id, 
            run_id, 
            prolific_study_id, 
            prolific_submission_id, 
            is_expired, 
            datetime('now', 'localtime') 
        FROM units;
    DROP TABLE units;
    ALTER TABLE _units RENAME TO units;
    
    
    /* Workers */
    CREATE TABLE IF NOT EXISTS _workers (
        id INTEGER PRIMARY KEY,
        worker_id TEXT UNIQUE,
        is_blocked BOOLEAN default false,
        update_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    /* Copy data from backed up table and set values for `creation_date` and `update_date` */
    INSERT INTO _workers 
        SELECT 
            id, 
            worker_id, 
            is_blocked, 
            datetime('now', 'localtime'), 
            datetime('now', 'localtime') 
        FROM workers;
    DROP TABLE workers;
    ALTER TABLE _workers RENAME TO workers;
    
    
    /* Runs */
    CREATE TABLE IF NOT EXISTS _runs (
        id INTEGER PRIMARY KEY,
        run_id TEXT UNIQUE,
        arn_id TEXT,
        prolific_workspace_id TEXT NOT NULL,
        prolific_project_id TEXT NOT NULL,
        prolific_study_id TEXT,
        prolific_study_config_path TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        frame_height INTEGER NOT NULL DEFAULT 650,
        actual_available_places INTEGER DEFAULT NULL,
        listed_available_places INTEGER DEFAULT NULL
    );
    INSERT INTO _runs SELECT * FROM runs;
    DROP TABLE runs;
    ALTER TABLE _runs RENAME TO runs;
    
    
    /* Participant Groups */
    CREATE TABLE IF NOT EXISTS _participant_groups (
        id INTEGER PRIMARY KEY,
        qualification_name TEXT UNIQUE,
        requester_id TEXT,
        prolific_project_id TEXT,
        prolific_participant_group_name TEXT,
        prolific_participant_group_id TEXT,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _participant_groups SELECT * FROM participant_groups;
    DROP TABLE participant_groups;
    ALTER TABLE _participant_groups RENAME TO participant_groups;
    
    
    /* Runs */
    CREATE TABLE IF NOT EXISTS _qualifications (
        id INTEGER PRIMARY KEY,
        prolific_participant_group_id TEXT,
        task_run_id TEXT,
        json_qual_logic TEXT,
        qualification_ids TEXT,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO _qualifications SELECT * FROM qualifications;
    DROP TABLE qualifications;
    ALTER TABLE _qualifications RENAME TO qualifications;
    
    
    /* Enable FK constraints back */
    PRAGMA foreign_keys = on;
    
    
    ALTER TABLE run_mappings RENAME COLUMN run_id TO task_run_id;
    ALTER TABLE units RENAME COLUMN run_id TO task_run_id;
    ALTER TABLE runs RENAME COLUMN run_id TO task_run_id;
    
    
    DROP TABLE IF EXISTS requesters;
"""
