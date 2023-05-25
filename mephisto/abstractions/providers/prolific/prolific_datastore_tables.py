#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

CREATE_STUDIES_TABLE = """
    CREATE TABLE IF NOT EXISTS studies (
        study_id TEXT PRIMARY KEY UNIQUE,
        unit_id TEXT,
        assignment_id TEXT,
        link TEXT,
        assignment_time_in_seconds INTEGER NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_RUN_MAP_TABLE = """
    CREATE TABLE IF NOT EXISTS run_mappings (
        study_id TEXT,
        run_id TEXT
    );
"""

CREATE_REQUESTERS_TABLE = """
    CREATE TABLE IF NOT EXISTS requesters (
        requester_id TEXT PRIMARY KEY UNIQUE,
        is_registered BOOLEAN
    );
"""

CREATE_UNITS_TABLE = """
    CREATE TABLE IF NOT EXISTS units (
        unit_id TEXT PRIMARY KEY UNIQUE,
        is_expired BOOLEAN
    );
"""

CREATE_WORKERS_TABLE = """
    CREATE TABLE IF NOT EXISTS workers (
        worker_id TEXT PRIMARY KEY UNIQUE,
        is_blocked BOOLEAN
    );
"""

CREATE_QUALIFICATIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS qualifications (
        qualification_name TEXT PRIMARY KEY UNIQUE,
        requester_id TEXT,
        prolific_project_id TEXT,
        prolific_participant_group_name TEXT,
        prolific_participant_group_id TEXT,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_RUNS_TABLE = """
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY UNIQUE,
        arn_id TEXT,
        prolific_workspace_id TEXT NOT NULL,
        prolific_project_id TEXT NOT NULL,
        prolific_study_id TEXT NOT NULL,
        prolific_study_config_path TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        frame_height INTEGER NOT NULL DEFAULT 650
    );
"""
