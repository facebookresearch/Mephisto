#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.mock.provider_type import PROVIDER_TYPE as MOCK_PROVIDER_TYPE
from mephisto.abstractions.providers.mturk.provider_type import PROVIDER_TYPE as MTURK_PROVIDER_TYPE
from mephisto.abstractions.providers.prolific.provider_type import (
    PROVIDER_TYPE as PROLIFIC_PROVIDER_TYPE,
)


BACKUP_OUTPUT_DIR = "outputs/backup"
EXPORT_OUTPUT_DIR = "outputs/export"

MEPHISTO_DUMP_KEY = "mephisto"

METADATA_DUMP_KEY = "dump_metadata"
METADATA_MIGRATIONS_KEY = "migrations"
METADATA_EXPORT_OPTIONS_KEY = "export_options"
METADATA_TIMESTAMP_KEY = "timestamp"
METADATA_PK_SUBSTITUTIONS_KEY = "pk_substitutions"

AVAILABLE_PROVIDER_TYPES = [
    MEPHISTO_DUMP_KEY,
    MOCK_PROVIDER_TYPE,
    MTURK_PROVIDER_TYPE,
    PROLIFIC_PROVIDER_TYPE,
]
DATASTORE_EXPORT_METHOD_NAME = "get_export_data"
DEFAULT_CONFLICT_RESOLVER = "DefaultMergeConflictResolver"
EXAMPLE_CONFLICT_RESOLVER = "ExampleMergeConflictResolver"
IMPORTED_DATA_TABLE_NAME = "imported_data"
MIGRATIONS_TABLE_NAME = "migrations"
TASK_RUNS_TABLE_NAME = "task_runs"
UNITS_TABLE_NAME = "units"
ASSIGNMENTS_TABLE_NAME = "assignments"
AGENTS_TABLE_NAME = "agents"

# Format of mappings:
#     {
#         <source_table_name>: {
#             <relation_table_name>: {
#                 "from": <name_of_source_table_field>,
#                 "to": <name_of_relation_table_field>,
#             },
#             ... # Table can have several FKs
#         },
#         ...
#     }
#
# If FK is related to Mephisto DB table, use `FK_MEPHISTO_TABLE_PREFIX` before table name.
# If FK is related to the same DB, simply use table name without any prefixes.
FK_MEPHISTO_TABLE_PREFIX = "mephisto."
PROVIDER_DATASTORES__MEPHISTO_FK__MAPPINGS = {
    PROLIFIC_PROVIDER_TYPE: {
        "studies": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "task_run_id",
                "to": "task_run_id",
            },
        },
        "run_mappings": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "task_run_id",
                "to": "task_run_id",
            },
        },
        "units": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "task_run_id",
                "to": "task_run_id",
            },
            f"{FK_MEPHISTO_TABLE_PREFIX}{UNITS_TABLE_NAME}": {
                "from": "unit_id",
                "to": "unit_id",
            },
        },
        "runs": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "task_run_id",
                "to": "task_run_id",
            },
        },
        "participant_groups": {
            f"{FK_MEPHISTO_TABLE_PREFIX}requesters": {
                "from": "requester_id",
                "to": "requester_id",
            },
        },
        "qualifications": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "task_run_id",
                "to": "task_run_id",
            },
        },
    },
    MOCK_PROVIDER_TYPE: {
        "requesters": {
            f"{FK_MEPHISTO_TABLE_PREFIX}requesters": {
                "from": "requester_id",
                "to": "requester_id",
            },
        },
        "units": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{UNITS_TABLE_NAME}": {
                "from": "unit_id",
                "to": "unit_id",
            },
        },
        "workers": {
            f"{FK_MEPHISTO_TABLE_PREFIX}workers": {
                "from": "worker_id",
                "to": "worker_id",
            },
        },
    },
    MTURK_PROVIDER_TYPE: {
        "hits": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{UNITS_TABLE_NAME}": {
                "from": "unit_id",
                "to": "unit_id",
            },
            f"{FK_MEPHISTO_TABLE_PREFIX}{ASSIGNMENTS_TABLE_NAME}": {
                "from": "assignment_id",
                "to": "assignment_id",
            },
        },
        "run_mappings": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "run_id",
                "to": "task_run_id",
            },
        },
        "runs": {
            f"{FK_MEPHISTO_TABLE_PREFIX}{TASK_RUNS_TABLE_NAME}": {
                "from": "run_id",
                "to": "task_run_id",
            },
        },
        "qualifications": {
            f"{FK_MEPHISTO_TABLE_PREFIX}requesters": {
                "from": "requester_id",
                "to": "requester_id",
            },
        },
    },
}

# As Mock or MTurk do not have real PKs (they use Mephisto PKs as provider tables' PKs),
# we cannot rely on auto getting PKs from db.
# Map tables with their PKs manually
PROVIDER_DATASTORES__RANDOMIZABLE_PK__MAPPINGS = {
    PROLIFIC_PROVIDER_TYPE: {
        "participant_groups": "id",
        "qualifications": "id",
        "run_mappings": "id",
        "runs": "id",
        "studies": "id",
        "submissions": "id",
        "units": "id",
        "workers": "id",
    },
}

# Tables must be in specific order to satisfy constraints of Foreign Keys.
# NOTE: field names are lists, because fields can be UNIQUE TOGETHER
TABLES_UNIQUE_LOOKUP_FIELDS = {
    MEPHISTO_DUMP_KEY: {
        "projects": ["project_name"],
        "requesters": ["requester_name"],
        "tasks": ["task_name"],
        "qualifications": ["qualification_name"],
        "workers": ["worker_name"],
        TASK_RUNS_TABLE_NAME: None,
        ASSIGNMENTS_TABLE_NAME: None,
        UNITS_TABLE_NAME: None,
        AGENTS_TABLE_NAME: None,
        "onboarding_agents": None,
        "granted_qualifications": ["worker_id", "qualification_id"],
        "unit_review": None,
    },
    PROLIFIC_PROVIDER_TYPE: {
        "workers": ["worker_id"],
        "participant_groups": ["qualification_name"],
        "qualifications": None,
        "studies": None,
        "runs": ["task_run_id"],
        "run_mappings": None,
        "submissions": None,
        "units": ["unit_id"],
    },
    MOCK_PROVIDER_TYPE: {
        "requesters": None,
        "workers": None,
        "units": None,
    },
    MTURK_PROVIDER_TYPE: {
        "hits": None,
        "run_mappings": None,
        "runs": None,
        "qualifications": None,
    },
}

# Tables that we need to write into `imported_data` during importing from dump file
IMPORTED_DATA_TABLE_NAMES = [
    "projects",
    "requesters",
    "tasks",
    "qualifications",
    "granted_qualifications",
    "workers",
    # TaskRuns cannot conflict,
    # but we write them into `imported_data` to know which TaskRuns were imported and
    # have fast access to export by labels
    TASK_RUNS_TABLE_NAME,
]

# We mark rows in `imported_data` with labels and this label is used
# if conflicted row was already presented in local DB
LOCAL_DB_LABEL = "_"

DEFAULT_ARCHIVE_FORMAT = "zip"

TABLE_NAMES_RELATED_TO_QUALIFICATIONS = [
    "granted_qualifications",
    "qualifications",
    "workers",
]
