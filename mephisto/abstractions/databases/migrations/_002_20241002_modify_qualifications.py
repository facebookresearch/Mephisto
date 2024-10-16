#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
List of changes:
1. Add `description` field into `qualifications` table
2. Rename `unit_review` table into `worker_review` and
    make unit-related fields nullable in table `unit_review`
"""


MODIFY_QUALIFICATIONS = """
    /* 1. Add `description` field into `qualifications` table */
    ALTER TABLE qualifications ADD COLUMN description CHAR(500);

    /* Disable FK constraints */
    PRAGMA foreign_keys = off;

    /* 2. Rename `unit_review` table into `worker_review` and
        make unit-related fields nullable in table `unit_review` */
    CREATE TABLE IF NOT EXISTS worker_review (
        id INTEGER PRIMARY KEY,
        unit_id INTEGER,
        worker_id INTEGER NOT NULL,
        task_id INTEGER,
        status TEXT,
        review_note TEXT,
        bonus INTEGER,
        blocked_worker BOOLEAN DEFAULT false,
        /* ID of `db.qualifications` (not `db.granted_qualifications`) */
        updated_qualification_id INTEGER,
        updated_qualification_value INTEGER,
        /* ID of `db.qualifications` (not `db.granted_qualifications`) */
        revoked_qualification_id INTEGER,
        creation_date DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),

        FOREIGN KEY (unit_id) REFERENCES units (unit_id),
        FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
        FOREIGN KEY (task_id) REFERENCES tasks (task_id)
    );
    INSERT INTO worker_review SELECT * FROM unit_review;
    DROP INDEX IF EXISTS unit_review_by_unit_index;
    DROP TABLE IF EXISTS unit_review;

    /* Enable FK constraints back */
    PRAGMA foreign_keys = on;
"""
