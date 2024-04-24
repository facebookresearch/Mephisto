---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 3
---

# Custom conflict resolver

When importing dump data into local DB, some rows may refer to the same object
(e.g. two Task rows with hte same value of "name" column). This class contains default logic
to resolve such merging conflicts (implemented for all currently present DBs).

To change this default behavior, you can write your own coflict resolver class:
1. Add a new Python module next to this module (e.g. `my_conflict_resolver`)

2. This module must contain a class (e.g. `MyMergeConflictResolver`)
    that inherits from either `BaseMergeConflictResolver`
    or default resolver `DefaultMergeConflictResolver` (also in this directory)
    ```python
    from .base_merge_conflict_resolver import BaseMergeConflictResolver

    class CustomMergeConflictResolver(BaseMergeConflictResolver):
        default_strategy_name = "..."
        strategies_config = {...}
    ```

3. To use this newly created class, specify its name in import command:
    `mephisto db import ... --conflict-resolver MyMergeConflictResolver`

The easiest place to start customization is to modify `strategies_config` property,
and perhaps `default_strategy_name` value (see `DefaultMergeConflictResolver` as an example).

NOTE: All available providers must be present in `strategies_config`.
Table names (under each provider key) are optional, and if missing, `default_strategy_name`
will be used for all conflicts related to this table.
