#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict

from mephisto.abstractions.database import MephistoDB
from mephisto.tools.db_data_porter import conflict_resolvers
from mephisto.tools.db_data_porter.constants import IMPORTED_DATA_TABLE_NAME
from mephisto.tools.db_data_porter.constants import IMPORTED_DATA_TABLE_NAMES
from mephisto.tools.db_data_porter.constants import LOCAL_DB_LABEL
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import TABLES_UNIQUE_LOOKUP_FIELDS
from mephisto.utils import db as db_utils
from mephisto.utils.console_writer import ConsoleWriter

UNIQUE_FIELD_NAMES = "unique_field_names"
UNIQUE_FIELD_VALUES = "unique_field_values"

logger = ConsoleWriter()

TableNameType = str
PKSubstitutionsType = Dict[
    str,  # Importing PK
    str,  # Existing PK in local DB
]
MappingResolvingsType = Dict[TableNameType, PKSubstitutionsType]


class ImportSingleDBsType(TypedDict):
    errors: Optional[List[str]]
    imported_data: Optional[dict]


def _update_row_with_pks_from_resolvings_mappings(
    db: "MephistoDB",
    table_name: str,
    row: dict,
    resolvings_mapping: MappingResolvingsType,
) -> dict:
    table_fks = db_utils.select_fk_mappings_for_table(db, table_name)

    # Update FK fields from resolving mappings if needed
    for fk_table, fk_table_fields in table_fks.items():
        relating_table_mapping = resolvings_mapping.get(fk_table)
        if not relating_table_mapping:
            continue

        relating_table_row_pk_mapping = relating_table_mapping.get(row[fk_table_fields["from"]])
        if not relating_table_row_pk_mapping:
            continue

        row[fk_table_fields["from"]] = relating_table_row_pk_mapping

    return row


def import_single_db(
    db: "MephistoDB",
    provider_type: str,
    dump_data: dict,
    conflict_resolver_name: str,
    label: str,
    verbosity: int = 0,
) -> ImportSingleDBsType:
    # Results of the function
    imported_data = {}
    errors = []

    # Variables to save current (intermediate) working values in case of exceptions
    # to make a comprehensive error message, because SQLite has a lack of it
    in_progress_table_name = None
    in_progress_dump_row = None
    in_progress_table_pk_field_name = None

    # Mappings between conflicted and chosen after resolving a conflict PKs
    resolvings_mapping: MappingResolvingsType = {}

    # --- HACK (#UNIT.AGENT_ID) START #1:
    # In Mephisto DB we have a problem with inserting `units` and `agents` tables.
    # Both tables have the relation (FK `units.agent_id` and `agents.unit_id`) to each other and
    # if both fields are filled in, we catch an FK constraint error.
    # Changing the order of importing tables will not help us in this case.
    # The solution is to create all rows in `units` table `agent_id = NULL` and
    # save these IDs in following dict.
    # As soon as we complete all `units` and `agents`,
    # we will update all rows in `units` with saved `agent_id` values.
    units_agents = {}
    # --- HACK (#UNIT.AGENT_ID) END #1:

    # Import conflict resolver class and initiate it
    conflict_resolver_class = getattr(conflict_resolvers, conflict_resolver_name, None)
    if not conflict_resolver_class:
        error_message = f"Conflict resolver with name '{conflict_resolver_name}' has not found"
        logger.error(f"[red]{error_message}[/red]")
        raise ImportError(error_message)
    conflict_resolver_name = conflict_resolver_class(db, provider_type)

    try:
        # Independent tables with their not PK unigue field names where can be conflicts.
        # They must be imported before other tables
        tables_with_special_unique_field = TABLES_UNIQUE_LOOKUP_FIELDS.get(provider_type)
        for table_name, unique_field_names in tables_with_special_unique_field.items():
            dump_table_rows = dump_data[table_name]
            table_pk_field_name = db_utils.get_table_pk_field_name(db, table_name)
            is_table_with_special_unique_field = unique_field_names is not None

            # Save data that in progress for better logging
            in_progress_table_name = table_name
            in_progress_table_pk_field_name = table_pk_field_name

            # Imported data vars
            imported_data_needs_to_be_updated = (
                provider_type == MEPHISTO_DUMP_KEY and
                table_name in IMPORTED_DATA_TABLE_NAMES
            )

            newly_imported_labels = json.dumps([label])
            conflicted_labels = json.dumps([LOCAL_DB_LABEL, label])
            imported_data_for_table = {
                newly_imported_labels: [],
                conflicted_labels: [],
            }

            for dump_row in dump_table_rows:
                # Save data that in progress for better logging
                in_progress_dump_row = dump_row

                # --- HACK (#UNIT.AGENT_ID) START #2:
                # We save pairs `unit_id: agent_id` in case if `agent_id is not None` and
                # replace `agent_id` with `None`
                if provider_type == MEPHISTO_DUMP_KEY:
                    if table_name == "units" and (unit_agent_id := dump_row.get("agent_id")):
                        unit_id = dump_row[table_pk_field_name]
                        units_agents[unit_id] = unit_agent_id
                        dump_row["agent_id"] = None
                # --- HACK (#UNIT.AGENT_ID) END #2:

                imported_data_row_unique_field_values = [dump_row[table_pk_field_name]]
                imported_data_conflicted_row = False

                _update_row_with_pks_from_resolvings_mappings(
                    db, table_name, dump_row, resolvings_mapping,
                )

                # Table with non-PK unique field
                if is_table_with_special_unique_field:
                    imported_data_row_unique_field_values = [
                        dump_row[fn] for fn in unique_field_names
                    ]

                    unique_field_values: List[List[str]] = [
                        [dump_row[fn]] for fn in unique_field_names
                    ]
                    existing_rows = db_utils.select_rows_by_list_of_field_values(
                        db=db,
                        table_name=table_name,
                        field_names=unique_field_names,
                        field_values=unique_field_values,
                        order_by="creation_date",
                    )

                    # If local DB does not have this row
                    if not existing_rows:
                        if verbosity:
                            logger.info(f"Inserting new row into table '{table_name}': {dump_row}")

                        db_utils.insert_new_row_in_table(db, table_name, dump_row)

                    # If local DB already has row with specified unique field name
                    else:
                        imported_data_conflicted_row = True

                        existing_db_row = existing_rows[-1]

                        if verbosity:
                            logger.info(
                                f"Conflicts during inserting row in table '{table_name}': "
                                f"{dump_row}. "
                                f"Existing row in your database: {existing_db_row}"
                            )

                        resolved_conflicting_row = conflict_resolver_name.resolve(
                            table_name, table_pk_field_name, existing_db_row, dump_row,
                        )
                        db_utils.update_row_in_table(
                            db, table_name, resolved_conflicting_row, table_pk_field_name,
                        )

                        # Saving resolved a pair of PKs
                        existing_row_pk_value = resolved_conflicting_row[table_pk_field_name]
                        importing_row_pk_value = dump_row[table_pk_field_name]

                        mappings_prev_value = resolvings_mapping.get(table_name, {})
                        resolvings_mapping[table_name] = {
                            **mappings_prev_value,
                            **{importing_row_pk_value: existing_row_pk_value},
                        }

                # Regular table. Create new row as is
                else:
                    db_utils.insert_new_row_in_table(db, table_name, dump_row)

                # Update table lists of Imported data
                if imported_data_needs_to_be_updated:
                    if imported_data_conflicted_row:
                        _label = conflicted_labels
                    else:
                        _label = newly_imported_labels

                    imported_data_for_table[_label].append({
                        UNIQUE_FIELD_NAMES: unique_field_names or [table_pk_field_name],
                        UNIQUE_FIELD_VALUES: imported_data_row_unique_field_values,
                    })

            # Add table into Imported data
            if imported_data_needs_to_be_updated:
                imported_data[table_name] = imported_data_for_table

        # --- HACK (#UNIT.AGENT_ID) START #3:
        # Update all created `units` rows in #2 with presaved `agent_id` values
        if provider_type == MEPHISTO_DUMP_KEY:
            for unit_id, agent_id in units_agents.items():
                db_utils.update_row_in_table(
                    db, "units", {"unit_id": unit_id, "agent_id": agent_id}, "unit_id",
                )
        # --- HACK (#UNIT.AGENT_ID) END #3:

    except Exception as e:
        # Custom error message in cases when we can guess what happens
        # using small info SQLite gives us
        possible_issue = ""
        if in_progress_table_pk_field_name in str(e) and "UNIQUE constraint" in str(e):
            pk_value = in_progress_dump_row[in_progress_table_pk_field_name]
            possible_issue = (
                f"\nPossible issue: "
                f"Local database already have Primary Key '{pk_value}' "
                f"in table '{in_progress_table_name}'. "
                f"Maybe you are trying to run already merged dump file. "
                f"Or if you have old databases, you may bump into same Primary Keys. "
                f"If you are sure that all data from this dump is unique and "
                f"still have access to the dumped project, "
                f"try to create dump with parameter `--randomize-legacy-ids` "
                f"and start importing again."
            )

        default_error_message_beginning = ""
        if not possible_issue:
            default_error_message_beginning = "Unexpected error happened: "

        errors.append(
            f"{default_error_message_beginning}{e}."
            f"{possible_issue}"
            f"\nProvider: {provider_type}."
            f"\nTable: {in_progress_table_name}."
            f"\nRow: {json.dumps(in_progress_dump_row, indent=2)}."
        )

    return {
        "errors": errors,
        "imported_data": imported_data,
    }


def fill_imported_data_with_imported_dump(
    db: "MephistoDB", imported_data: dict, source_file_name: str,
):
    for table_name, table_info in imported_data.items():
        for labels, labels_rows in table_info.items():
            for row in labels_rows:
                if not row["unique_field_values"]:
                    continue

                unique_field_names = json.dumps(row["unique_field_names"])
                unique_field_values = json.dumps(row["unique_field_values"])
                db_utils.insert_new_row_in_table(
                    db=db,
                    table_name=IMPORTED_DATA_TABLE_NAME,
                    row={
                        "source_file_name": source_file_name,
                        "data_labels": labels,
                        "table_name": table_name,
                        "unique_field_names": unique_field_names,
                        "unique_field_values": unique_field_values,
                    },
                )


def import_table_imported_data_from_dump(db: "MephistoDB", imported_data_rows: List[dict]):
    for row in imported_data_rows:
        table_name = row["table_name"]
        unique_field_names = row["unique_field_names"]
        unique_field_values = row["unique_field_values"]

        # Check if item from row was already imported before from other dumps
        existing_rows = db_utils.select_rows_by_list_of_field_values(
            db=db,
            table_name="imported_data",
            field_names=["table_name", "unique_field_names", "unique_field_values"],
            field_values=[[table_name], [unique_field_names], [unique_field_values]],
            order_by="-creation_date",
        )
        existing_row = existing_rows[0] if existing_rows else None

        # As we add this imported data from dump, new lines cannot have label for local DB.
        # Current local DB is not that one that was local for dumped data.
        # We save only labels from imported dumps
        importing_data_labels = json.loads(row["data_labels"])
        data_labels_without_local = [l for l in importing_data_labels if l != LOCAL_DB_LABEL]

        # Update existing row
        if existing_row:
            # Merge existing labels with from imported row
            existing_data_labels = json.loads(existing_row["data_labels"])
            existing_data_labels += importing_data_labels
            existing_row["data_labels"] = json.dumps(list(set(existing_data_labels)))

            db_utils.update_row_in_table(
                db=db, table_name="imported_data", row=existing_row, pk_field_name="id",
            )

        # Create new row
        else:
            # Set labels and remove PK field from importing row
            row.pop("id", None)
            row["data_labels"] = json.dumps(data_labels_without_local)

            db_utils.insert_new_row_in_table(db=db, table_name="imported_data", row=row)
