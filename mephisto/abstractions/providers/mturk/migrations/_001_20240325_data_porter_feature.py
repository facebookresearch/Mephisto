#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
List of changes:
1. Modify default value for `creation_date`
"""


MODIFICATIONS_FOR_DATA_PORTER = """
    /* Disable FK constraints */
    PRAGMA foreign_keys = off;


    /* Hits */
    CREATE TABLE IF NOT EXISTS _hits (
        hit_id TEXT PRIMARY KEY UNIQUE,
        unit_id TEXT,
        assignment_id TEXT,
        link TEXT,
        assignment_time_in_seconds INTEGER NOT NULL,
        creation_date DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
    );
    INSERT INTO _hits SELECT * FROM hits;
    DROP TABLE hits;
    ALTER TABLE _hits RENAME TO hits;


    /* Run mappings */
    CREATE TABLE IF NOT EXISTS _run_mappings (
        hit_id TEXT,
        run_id TEXT
    );
    INSERT INTO _run_mappings SELECT * FROM run_mappings;
    DROP TABLE run_mappings;
    ALTER TABLE _run_mappings RENAME TO run_mappings;


    /* Runs */
    CREATE TABLE IF NOT EXISTS _runs (
        run_id TEXT PRIMARY KEY UNIQUE,
        arn_id TEXT,
        hit_type_id TEXT NOT NULL,
        hit_config_path TEXT NOT NULL,
        creation_date DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
        frame_height INTEGER NOT NULL DEFAULT 650
    );
    INSERT INTO _runs SELECT * FROM runs;
    DROP TABLE runs;
    ALTER TABLE _runs RENAME TO runs;


    /* Qualifications */
    CREATE TABLE IF NOT EXISTS _qualifications (
        qualification_name TEXT PRIMARY KEY UNIQUE,
        requester_id TEXT,
        mturk_qualification_name TEXT,
        mturk_qualification_id TEXT,
        creation_date DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
    );
    INSERT INTO _qualifications SELECT * FROM qualifications;
    DROP TABLE qualifications;
    ALTER TABLE _qualifications RENAME TO qualifications;


    /* Enable FK constraints back */
    PRAGMA foreign_keys = on;
"""
