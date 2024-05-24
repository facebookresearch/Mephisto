#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from mephisto.abstractions.database import MephistoDB
from mephisto.generators.form_composer.config_validation.utils import make_error_message
from mephisto.tools.db_data_porter.constants import AVAILABLE_PROVIDER_TYPES
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import METADATA_DUMP_KEY
from mephisto.utils import db as db_utils


def validate_dump_data(db: "MephistoDB", dump_data: dict) -> Optional[List[str]]:
    errors = []

    db_dumps = {k: v for k, v in dump_data.items() if k != METADATA_DUMP_KEY}

    # 1. Check provider names
    incorrect_db_names = list(filter(lambda i: i not in AVAILABLE_PROVIDER_TYPES, db_dumps.keys()))
    if incorrect_db_names:
        errors.append(
            f"Dump file cannot contain these database names: {', '.join(incorrect_db_names)}."
        )

    # 2. Check if dump file contains JSON-object
    db_values_are_not_dicts = list(filter(lambda i: not isinstance(i, dict), dump_data.values()))
    if db_values_are_not_dicts:
        errors.append(
            f"We found {len(db_values_are_not_dicts)} values in the dump "
            f"that are not JSON-objects."
        )

    # 3. Check dumps of DBs
    _db_dumps = [(n, d) for n, d in db_dumps.items() if n not in incorrect_db_names]
    for db_name, db_dump_data in _db_dumps:
        # Get ot create DB/Datastore to request for available tables
        if db_name == MEPHISTO_DUMP_KEY:
            db_or_datastore = db
        else:
            # Use this method here as it creates an empty datastore if it does not exist
            db_or_datastore = db.get_datastore_for_provider(db_name)

        available_table_names = db_utils.get_list_of_db_table_names(db_or_datastore)

        # Check tables
        if not isinstance(db_dump_data, dict):
            continue

        for table_name, table_data in db_dump_data.items():
            # Table name must be string
            if not isinstance(table_name, str):
                errors.append(f"Expecting table name to be a string, not `{table_name}`.")

            # Table data is a list or rows
            if not isinstance(table_data, list):
                errors.append(f"Expecting table data to be a JSON-array, not `{table_data}`.")

            # Local DB/Datastore has same tables as a dump
            if table_name not in available_table_names:
                error_message = make_error_message(
                    f"Your local `{db_name}` database does not have table '{table_name}'.",
                    [
                        "local database has unapplied migrations",
                        "dump is too old and not compatible to your local database",
                    ],
                    indent=8,
                    list_title="Possible issues",
                )
                errors.append(error_message)

            # Check table rows
            for i, table_row in enumerate(table_data):
                if not isinstance(table_row, dict):
                    errors.append(
                        f"Table `{table_name}`, row {i}: "
                        f"expecting it to be a JSON-object, not `{table_row}`."
                    )
                    continue

                incorrect_field_names = list(
                    filter(lambda fn: not isinstance(fn, str), table_row.keys())
                )
                if incorrect_field_names:
                    errors.append(
                        f"Table `{table_name}`, row {i+1}: "
                        f"names of these fields must be strings: "
                        f"{', '.join([str(i) for i in incorrect_field_names])}."
                    )

    return errors
