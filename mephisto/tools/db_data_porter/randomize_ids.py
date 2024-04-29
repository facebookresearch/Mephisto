#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import TypedDict
from typing import Union

from mephisto.abstractions.database import MephistoDB
from mephisto.tools.db_data_porter.constants import FK_MEPHISTO_TABLE_PREFIX
from mephisto.tools.db_data_porter.constants import IMPORTED_DATA_TABLE_NAME
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import PROVIDER_DATASTORES__MEPHISTO_FK__MAPPINGS
from mephisto.tools.db_data_porter.constants import PROVIDER_DATASTORES__RANDOMIZABLE_PK__MAPPINGS
from mephisto.utils import db as db_utils
from mephisto.utils.console_writer import ConsoleWriter

logger = ConsoleWriter()

TablePKSubstitutionsType = Dict[str, str]  # One table
DBPKSubstitutionsType = Dict[str, TablePKSubstitutionsType]  # One DB
PKSubstitutionsType = Dict[str, DBPKSubstitutionsType]  # Multiple DBs


class RandomizedIDsType(TypedDict):
    pk_substitutions: PKSubstitutionsType
    updated_dump: dict


def _randomize_ids_for_mephisto(
    db: "MephistoDB",
    mephisto_dump: dict,
    legacy_only: bool = False,
) -> DBPKSubstitutionsType:
    table_names = [t for t in mephisto_dump.keys() if t not in [IMPORTED_DATA_TABLE_NAME]]

    # Find Foreign Keys' field names for all tables in Mephist DB
    tables_fks = db_utils.select_fk_mappings_for_all_tables(db, table_names)

    # Make new Primary Keys for all or legacy values
    mephisto_pk_substitutions = {}
    for table_name in table_names:
        pk_field_name = db_utils.get_table_pk_field_name(db, table_name)
        table_rows_from_mephisto_dump = mephisto_dump[table_name]

        table_pk_substitutions = {}
        for row in table_rows_from_mephisto_dump:
            old_pk = row[pk_field_name]

            is_legacy_value = int(old_pk) < db_utils.SQLITE_ID_MIN
            if not legacy_only or legacy_only and is_legacy_value:
                new_pk = str(db_utils.make_randomized_int_id())
                table_pk_substitutions.update({old_pk: new_pk})
                row[pk_field_name] = new_pk

        prev_value = mephisto_pk_substitutions.get(table_name, {})
        mephisto_pk_substitutions[table_name] = {**prev_value, **table_pk_substitutions}

    # Update Foreign Keys in related tables
    for table_name, fks in tables_fks.items():
        table_pk_substitutions = mephisto_pk_substitutions[table_name]
        # If nothing to update in related table, just skip it
        if not table_pk_substitutions:
            continue

        table_fks = tables_fks[table_name]
        # If table does not have any Foreign Keys, just skip it
        if not table_fks:
            continue

        # Change value in related tables rows
        table_rows_from_mephisto_dump = mephisto_dump[table_name]
        for row in table_rows_from_mephisto_dump:
            for fk_table_name, relation_data in table_fks.items():
                row_fk_value = row[relation_data["from"]]
                substitution = mephisto_pk_substitutions[fk_table_name].get(row_fk_value)

                if not substitution:
                    continue

                row[relation_data["from"]] = substitution

    return mephisto_pk_substitutions


def _randomize_ids_for_provider(
    provider_type: str,
    provider_dump: dict,
    mephisto_pk_substitutions: DBPKSubstitutionsType,
    legacy_only: bool = False,
) -> Union[DBPKSubstitutionsType, None]:
    # Nothing to process
    if not provider_dump:
        logger.warning(f"Dump for provider '{provider_type}' is empty, nothing to process")
        return

    provider_fks_mappings = PROVIDER_DATASTORES__MEPHISTO_FK__MAPPINGS.get(provider_type)
    # If a new provider and developer forgot to set FKs for export
    if not provider_fks_mappings:
        logger.warning(
            f"No configuration found in PROVIDER_DATASTORES__MEPHISTO_FK__MAPPINGS "
            f"for provider '{provider_type}'"
        )
        return

    # Make new Primary Keys for all or legacy values
    provider_pk_substitutions = {}
    provider_pks_mappings = PROVIDER_DATASTORES__RANDOMIZABLE_PK__MAPPINGS.get(provider_type, {})

    for table_name, pk_field_name in provider_pks_mappings.items():
        table_rows_from_mephisto_dump = provider_dump[table_name]
        table_pk_substitutions = {}
        for row in table_rows_from_mephisto_dump:
            old_pk = row[pk_field_name]

            is_legacy_value = int(old_pk) < db_utils.SQLITE_ID_MIN
            if not legacy_only or legacy_only and is_legacy_value:
                new_pk = str(db_utils.make_randomized_int_id())
                table_pk_substitutions.update({old_pk: new_pk})
                row[pk_field_name] = new_pk

        prev_value = provider_pk_substitutions.get(table_name, {})
        provider_pk_substitutions[table_name] = {**prev_value, **table_pk_substitutions}

    # Update Foreign Keys in related tables
    for table_name, fks in provider_fks_mappings.items():
        table_fks = provider_fks_mappings[table_name]
        # If table does not have any Foreign Keys, just skip it
        if not table_fks:
            continue

        table_rows_from_provider_dump = provider_dump.get(table_name, [])
        for row in table_rows_from_provider_dump:
            for fk_table_name, relation_data in table_fks.items():
                row_fk_value = row[relation_data["from"]]

                # FKs from Mephisto DB
                is_fk_to_mephisto_db = fk_table_name.startswith(FK_MEPHISTO_TABLE_PREFIX)
                if is_fk_to_mephisto_db:
                    fk_table_name = fk_table_name.split(FK_MEPHISTO_TABLE_PREFIX)[1]
                    substitution = mephisto_pk_substitutions[fk_table_name].get(row_fk_value)
                # FKs from provider DB
                else:
                    substitution = provider_pk_substitutions[fk_table_name].get(row_fk_value)

                if not substitution:
                    continue

                row[relation_data["from"]] = substitution

    return provider_pk_substitutions


def randomize_ids(
    db: "MephistoDB",
    full_dump: dict,
    legacy_only: bool = False,
) -> RandomizedIDsType:
    pk_substitutions: PKSubstitutionsType = {}

    # Mephisto DB
    mephisto_dump = full_dump[MEPHISTO_DUMP_KEY]
    mephisto_pk_substitutions = _randomize_ids_for_mephisto(db, mephisto_dump, legacy_only)
    pk_substitutions["mephisto"] = mephisto_pk_substitutions

    # Providers' DBs
    provider_types = [i["provider_type"] for i in mephisto_dump["requesters"]]
    for provider_type in provider_types:
        provider_dump = full_dump[provider_type]
        randomized_ids_for_provider = _randomize_ids_for_provider(
            provider_type,
            provider_dump,
            mephisto_pk_substitutions,
        )

        if randomized_ids_for_provider:
            pk_substitutions[provider_type] = randomized_ids_for_provider

    return {
        "pk_substitutions": pk_substitutions,
        "updated_dump": full_dump,
    }


def get_old_pk_from_substitutions(
    pk: str,
    substitutions: dict,
    table_name: str,
) -> str:
    # After we created a dump file, we already can have new randomized PKs.
    # But we still have old ones in Mephisto DB.
    # Find old PKs in reversed key-value pair
    pk_subs = substitutions.get(MEPHISTO_DUMP_KEY, {}).get(table_name, {})
    pk_subs_reversed = dict((v, k) for k, v in pk_subs.items())
    return pk_subs_reversed.get(pk)
