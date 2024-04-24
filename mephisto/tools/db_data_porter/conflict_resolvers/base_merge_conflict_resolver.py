#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from copy import deepcopy
from types import MethodType
from typing import Optional
from typing import Tuple

from mephisto.abstractions.database import MephistoDB
from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.misc import serialize_date_to_python

logger = ConsoleWriter()


class BaseMergeConflictResolver:
    """
    When importing dump data into local DB, some rows may refer to the same object
    (e.g. two Task rows with hte same value of "name" column). This class contains default logic
    to resolve such merging conflicts (implemented for all currently present DBs).

    To change this default behavior, you can write your own coflict resolver class:
        1. Add a new Python module next to this module (e.g. `my_conflict_resolver`)
        2. This module must contain a class (e.g. `MyMergeConflictResolver`)
            that inherits from either `BaseMergeConflictResolver`
            or default resolver `DefaultMergeConflictResolver` (also in this directory)
        3. To use this newly created class, specify its name in import command:
          `mephisto db import ... --conflict-resolver MyMergeConflictResolver`

    The easiest place to start customization is to modify `strategies_config` property,
    and perhaps `default_strategy_name` value (see `DefaultMergeConflictResolver` as an example).

    NOTE: All available providers must be present in `strategies_config`.
    Table names (under each provider key) are optional, and if missing, `default_strategy_name`
    will be used for all conflicts related to this table.
    """

    default_strategy_name = "pick_row_from_db"
    strategies_config = {}

    def __init__(self, db: "MephistoDB", provider_type: str):
        self.db = db
        self.provider_type = provider_type

    @staticmethod
    def _merge_rows_after_resolving(
        table_pk_field_name: str, db_row: dict, dump_row: dict, resolved_row: dict,
    ) -> dict:
        """
        After we've resolved merging conflicts with rows fields,
        we also need to select resulting value for some standard fields:
            1. Primary Key (choose DB row)
            2. Creation date (choose the earliest)
            3. Update date (choose the latest)
        """

        # 1. Save original PK from current DB
        merged_row = deepcopy(resolved_row)
        merged_row[table_pk_field_name] = db_row[table_pk_field_name]

        # 2. Choose the earliest creation date if table has this field
        if "creation_date" in resolved_row:
            min_creation_date = min(
                serialize_date_to_python(db_row["creation_date"]),
                serialize_date_to_python(dump_row["creation_date"]),
            )
            merged_row["creation_date"] = min_creation_date

        # 3. Choose the latest updating date if table has this field
        if "update_date" in resolved_row:
            min_update_date = max(
                serialize_date_to_python(db_row["update_date"]),
                serialize_date_to_python(dump_row["update_date"]),
            )
            merged_row["update_date"] = min_update_date

        return merged_row

    @staticmethod
    def _serialize_compared_fields_in_rows(
        db_row: dict, dump_row: dict, compared_field_name: str,
    ) -> Tuple[dict, dict]:
        db_value = db_row[compared_field_name]
        dump_value = dump_row[compared_field_name]

        # Date fields
        if compared_field_name.endswith("_at") or compared_field_name.endswith("_date"):
            db_row[compared_field_name] = serialize_date_to_python(db_value)
            dump_row[compared_field_name] = serialize_date_to_python(dump_value)

        # Numeric fields (integer or float)
        # Note: We cast both compared values to a numeric type
        # ONLY when one value is numeric, and another one is a string
        # (to avoid, for example, casting float to integer)
        for _type in [int, float]:
            if (
                (isinstance(db_value, _type) and isinstance(dump_value, str)) or
                (isinstance(db_value, str) and isinstance(dump_value, _type))
            ):
                db_row[compared_field_name] = _type(db_value)
                dump_row[compared_field_name] = _type(dump_value)

        return db_row, dump_row

    def resolve(
        self, table_name: str, table_pk_field_name: str, db_row: dict, dump_row: dict,
    ) -> dict:
        """
        Default logic of validating `strategies_config`,
        and resolving conflicts between database/datastore and dump rows
        """
        # Validate strategies

        # 1. Providers must be set
        provider_strategies = self.strategies_config.get(self.provider_type)
        if not provider_strategies:
            error_message = f"Could not find strategies for provider '{self.provider_type}'"
            logger.error(f"[red]{error_message}[/red]")
            raise ValueError(error_message)

        # 2. If no tables, use default strategy - `pick_row_from_db`
        table_strategy = provider_strategies.get(table_name)
        strategy_method_name = self.default_strategy_name
        # Custom strategy
        if table_strategy:
            strategy_method_name = table_strategy.get("method")
            strategy_method: MethodType = getattr(self, strategy_method_name, None)
            strategy_method_kwargs = table_strategy.get("kwargs", {})
        # Default strategy
        else:
            strategy_method: MethodType = getattr(self, strategy_method_name, None)
            strategy_method_kwargs = {}

        if not strategy_method:
            error_message = f"Could not find method for strategy with name '{strategy_method_name}'"
            logger.error(f"[red]{error_message}[/red]")
            raise ValueError(error_message)

        # 3. Resolve conflicts
        resolved_row = strategy_method(db_row, dump_row, **strategy_method_kwargs)

        # 4. Merge data
        merged_row = self._merge_rows_after_resolving(
            table_pk_field_name, db_row, dump_row, resolved_row,
        )

        # 4. Return merged row
        return merged_row

    # --- Prepared most cummon strategies ---
    def pick_row_with_smaller_value(
        self, db_row: dict, dump_row: dict, compared_field_name: str,
    ) -> dict:
        db_row, dump_row = self._serialize_compared_fields_in_rows(
            db_row, dump_row, compared_field_name,
        )
        db_value = db_row[compared_field_name]
        dump_value = dump_row[compared_field_name]

        # None cannot be compared with anything
        if db_value is None:
            return dump_row
        if dump_value is None:
            return db_value

        min_value = min(db_value, dump_value)
        if min_value == db_value:
            return db_row
        return dump_row

    def pick_row_with_larger_value(
        self, db_row: dict, dump_row: dict, compared_field_name: str,
    ) -> dict:
        db_row, dump_row = self._serialize_compared_fields_in_rows(
            db_row, dump_row, compared_field_name,
        )
        db_value = db_row[compared_field_name]
        dump_value = dump_row[compared_field_name]

        # None cannot be compared with anything
        if db_value is None:
            return dump_row
        if dump_value is None:
            return db_value

        max_value = max(db_value, dump_value)
        if max_value == db_value:
            return db_row
        return dump_row

    def pick_row_from_db(
        self, db_row: dict, dump_row: dict, compared_field_name: Optional[str] = None,
    ) -> dict:
        return db_row

    def pick_row_from_dump(
        self, db_row: dict, dump_row: dict, compared_field_name: Optional[str] = None,
    ) -> dict:
        return dump_row

    def pick_row_with_earlier_value(
        self, db_row: dict, dump_row: dict, compared_field_name: str = "creation_date",
    ) -> dict:
        db_row, dump_row = self._serialize_compared_fields_in_rows(
            db_row, dump_row, compared_field_name,
        )
        db_value = db_row[compared_field_name]
        dump_value = dump_row[compared_field_name]

        # None cannot be compared with anything
        if db_value is None:
            return dump_row
        if dump_value is None:
            return db_value

        if dump_value > db_value:
            return db_row
        return dump_row

    def pick_row_with_later_value(
        self, db_row: dict, dump_row: dict, compared_field_name: str = "creation_date",
    ) -> dict:
        db_row, dump_row = self._serialize_compared_fields_in_rows(
            db_row, dump_row, compared_field_name,
        )
        db_value = db_row[compared_field_name]
        dump_value = dump_row[compared_field_name]

        # None cannot be compared with anything
        if db_value is None:
            return dump_row
        if dump_value is None:
            return db_value

        if dump_value < db_value:
            return db_row
        return dump_row
