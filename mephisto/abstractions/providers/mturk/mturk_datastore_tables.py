#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
WARNING: In this module you can find initial table structures, but not final.
There are can be changes in migrations. To see actual fields, constraints, etc.,
see information in databases or look through all migrations for current database
"""

from mephisto.abstractions.databases import local_database_tables


CREATE_IF_NOT_EXISTS_HITS_TABLE = """
    CREATE TABLE IF NOT EXISTS hits (
        hit_id TEXT PRIMARY KEY UNIQUE,
        unit_id TEXT,
        assignment_id TEXT,
        link TEXT,
        assignment_time_in_seconds INTEGER NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_IF_NOT_EXISTS_RUN_MAP_TABLE = """
    CREATE TABLE IF NOT EXISTS run_mappings (
        hit_id TEXT,
        run_id TEXT
    );
"""

CREATE_IF_NOT_EXISTS_RUNS_TABLE = """
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY UNIQUE,
        arn_id TEXT,
        hit_type_id TEXT NOT NULL,
        hit_config_path TEXT NOT NULL,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        frame_height INTEGER NOT NULL DEFAULT 650
    );
"""

CREATE_IF_NOT_EXISTS_QUALIFICATIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS qualifications (
        qualification_name TEXT PRIMARY KEY UNIQUE,
        requester_id TEXT,
        mturk_qualification_name TEXT,
        mturk_qualification_id TEXT,
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE = local_database_tables.CREATE_IF_NOT_EXISTS_MIGRATIONS_TABLE


# Migrations
# TODO: Refactor it as it was done for other databases

UPDATE_RUNS_TABLE_1 = """
    ALTER TABLE runs ADD COLUMN frame_height INTEGER NOT NULL DEFAULT 650;
"""
