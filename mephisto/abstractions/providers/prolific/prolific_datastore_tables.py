#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

CREATE_STUDIES_TABLE = """
    CREATE TABLE IF NOT EXISTS studies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prolific_study_id TEXT UNIQUE,
        status TEXT,
        link TEXT,
        task_run_id TEXT UNIQUE,
        assignment_time_in_seconds INTEGER NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_SUBMISSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prolific_submission_id TEXT UNIQUE,
        prolific_study_id TEXT,
        status TEXT DEFAULT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_RUN_MAP_TABLE = """
    CREATE TABLE IF NOT EXISTS run_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prolific_study_id TEXT,
        run_id TEXT
    );
"""

CREATE_REQUESTERS_TABLE = """
    CREATE TABLE IF NOT EXISTS requesters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_id TEXT UNIQUE,
        is_registered BOOLEAN
    );
"""

CREATE_UNITS_TABLE = """
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id TEXT UNIQUE,
        run_id TEXT,
        prolific_study_id TEXT,
        prolific_submission_id TEXT,
        is_expired BOOLEAN DEFAULT false
    );
"""

CREATE_WORKERS_TABLE = """
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id TEXT UNIQUE,
        is_blocked BOOLEAN default false
    );
"""

CREATE_RUNS_TABLE = """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
"""

CREATE_PARTICIPANT_GROUPS_TABLE = """
    CREATE TABLE IF NOT EXISTS participant_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qualification_name TEXT UNIQUE,
        requester_id TEXT,
        prolific_project_id TEXT,
        prolific_participant_group_name TEXT,
        prolific_participant_group_id TEXT,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_PARTICIPANT_GROUP_QUALIFICATIONS_MAPPING_TABLE = """
    CREATE TABLE IF NOT EXISTS qualifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prolific_participant_group_id TEXT,
        task_run_id TEXT,
        json_qual_logic TEXT,
        qualification_ids TEXT,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""
