#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import datetime
from typing import Optional

from rich import print as rich_print

from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import MOCK_PROVIDER_TYPE
from mephisto.tools.db_data_porter.constants import MTURK_PROVIDER_TYPE
from mephisto.tools.db_data_porter.constants import PROLIFIC_PROVIDER_TYPE
from .base_merge_conflict_resolver import BaseMergeConflictResolver


class ExampleMergeConflictResolver(BaseMergeConflictResolver):
    """
    Example how to write your own conflict resolver.

    NOTE: do not accidentally use this example resolver on your real data.
    """

    default_strategy_name = "pick_row_from_db_and_set_creation_date_to_y2k"

    def pick_row_from_db_and_set_creation_date_to_y2k(
        self,
        db_row: dict,
        dump_row: dict,
        row_field_name: Optional[str] = None,
    ) -> dict:
        if "creation_date" in db_row:
            db_row["creation_date"] = datetime(2000, 1, 1)
            rich_print(f"\tSet `creation_date` to y2k for row {db_row}")

        return db_row

    def concatenate_values(
        self,
        db_row: dict,
        dump_row: dict,
        row_field_name: str,
        separator: str,
    ) -> dict:
        resulting_row = self.pick_row_from_db_and_set_creation_date_to_y2k(db_row, dump_row)

        db_value = db_row[row_field_name] or ""
        dump_value = dump_row[row_field_name] or ""

        if dump_value and db_value:
            resulting_row[row_field_name] = db_value + separator + dump_value
            rich_print(f"\tConcatenated `{row_field_name}` values for row {resulting_row}")

        return resulting_row

    strategies_config = {
        MEPHISTO_DUMP_KEY: {
            "tasks": {
                # Concatenate names
                "method": "concatenate_values",
                "kwargs": {
                    "row_field_name": "task_name",
                    "separator": " + ",
                },
            },
        },
        PROLIFIC_PROVIDER_TYPE: {},
        MOCK_PROVIDER_TYPE: {},
        MTURK_PROVIDER_TYPE: {},
    }
