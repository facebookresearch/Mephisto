#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import MOCK_PROVIDER_TYPE
from mephisto.tools.db_data_porter.constants import MTURK_PROVIDER_TYPE
from mephisto.tools.db_data_porter.constants import PROLIFIC_PROVIDER_TYPE
from .base_merge_conflict_resolver import BaseMergeConflictResolver


class DefaultMergeConflictResolver(BaseMergeConflictResolver):
    """
    Default conflict resolver for importing JSON DB dumps.
    If table name is not specified, default resolver strategy will be used
    on all of its conflicting fields.

    For more detailed information, see docstring in `BaseMergeConflictResolver`.
    """

    strategies_config = {
        MEPHISTO_DUMP_KEY: {
            "granted_qualifications": {
                # Go with more restrictive value
                "method": "pick_row_with_smaller_value",
                "kwargs": {
                    "row_field_name": "value",
                },
            },
        },
        PROLIFIC_PROVIDER_TYPE: {
            "workers": {
                # Go with more restrictive value
                # Note that `is_blocked` is SQLite-boolean, which is an integer in Python
                "method": "pick_row_with_larger_value",
                "kwargs": {
                    "row_field_name": "is_blocked",
                },
            },
        },
        MOCK_PROVIDER_TYPE: {},
        MTURK_PROVIDER_TYPE: {},
    }
