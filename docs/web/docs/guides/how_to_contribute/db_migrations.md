---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 4
---

# Database migrations

## Overview

Currently we are not using any special framework for updating Mephisto database or provider-specific datastores.
This is how it's done:

1. Each database should have table `migrations` where we store all applied or failed migrations
2. Every run of any Mephisto command will automatically attempt to apply unapplied migrations
3. Each migration is a Python module that contains one constant (a raw SQL query string)
4. After adding a migration, its constant must be imported and added to the migrations dict
   under a readable name (dict key) that will be used in `migrations` table
5. Any database implementation, must call function `apply_migrations` in method `init_tables` (after creating all tables).
   NOTE: Migrations must be applied before creating DB indices, as migrations may erase them without restoring.
6. When migrations fail, you will see a console log message in console.
   The error will also be written to `migrations` table under `error_message` column with status `"errored"`

## Details

Let's see how exactly DB migrations should be created.

We'll use Mephisto DB as example; the same set of steps is used for provider-specific databases
.

### Add migration package

To add a new migration package, follow these steps:

1. Create Python-package `migrations` next to `mephisto/abstractions/databases/local_database.py`.
2. Create migration module in that package, e.g. `_001_20240101_add__column_name__in__table_name.py`.
   Note leading underscore - Python does not allow importing modeuls that start with a number.
3. Populate module with a SQL query constant:
    ```python
    # <copyright notice>

    """
    This migration introduces the following changes:
    - ...
    """

    MY_SQL_MIGRATION_QUERY_NAME = """
        <SQL query>
    """
    ```
4. Include this SQL query constant in `__init__.py` module (located next to the migration module):
    ```python
    # <copyright notice>
    from ._001_20240101_add__column_name__in__table_name import *


    migrations = {
        "20240101_add__column_name__in__table_name": MY_SQL_MIGRATION_QUERY_NAME,
    }
    ```

5. Note that for now we support only forward migrations.
If you do need a backward migration, simply add it as a forward migration that would undo the undesired changes.


### Call `apply_migrations` function

1. Import migrations in `mephisto/abstractions/databases/local_database.py`:
    ```python
    ...
    from .migrations import migrations
    ...
    ```
2. Apply migrations in `LocalMephistoDB`:
    ```python
    class LocalMephistoDB(MephistoDB):
        ...
        def init_tables(self) -> None:
            with self.table_access_condition:
                conn = self.get_connection()
                conn.execute("PRAGMA foreign_keys = on;")

                with conn:
                    c = conn.cursor()
                    c.execute(tables.CREATE_IF_NOT_EXISTS_PROJECTS_TABLE)
                    ...

                apply_migrations(self, migrations)
                ...

                with conn:
                    c.executescript(tables.CREATE_IF_NOT_EXISTS_CORE_INDICES)
                ...
    ```

## Maintenance of related code

Making changes in databases must be carefully thought through and tested.

This is a list of places that will most likely need to be synced with your DB change:

1. All queries (involving tables that you have updated) in database class, e.g. `LocalMephistoDB`
2. Module with common database queries `mephisto/utils/db.py`
3. Queries in __Review App__ (`mephisto/review_app/server`) - it has its own set of specific queries
4. Names/relationships for tables and columns in __DBDataPorter__ (they're hardcoded in many places there),
   within Mephisto DB and provider-specific databases. For instance:
      - `mephisto/tools/db_data_porter/constants.py`
      - `mephisto/tools/db_data_porter/import_dump.py`
      - ...
5. Data processing within Mephisto itself (obviously)

While we did our best to abstract away particular tables and fields structure,
they still have to be spelled out in some places.
Please run tests and check manually all Mephisto applications after performing database changes.
