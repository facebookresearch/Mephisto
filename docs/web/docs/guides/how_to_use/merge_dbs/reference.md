---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Reference

This is a reference describing set of commands under the `mephisto db` command group.

## Export

This command exports data from Mephisto DB and provider-specific datastores
as an archived combination of (i) a JSON file, and (ii) a `data` catalog with related files.

If no parameter passed, full data dump (i.e. backup) will be created.

To pass a list of values for one command option, simply repeat that option name before each value.

Examples:
```
mephisto db export
mephisto db export --verbosity
mephisto db export --export-tasks-by-names "My first Task"
mephisto db export --export-tasks-by-ids 1 --export-tasks-by-ids 2
mephisto db export --export-task-runs-by-ids 3 --export-task-runs-by-ids 4
mephisto db export --export-task-runs-since-date 2024-01-01
mephisto db export --export-task-runs-since-date 2023-01-01T00:00:00
mephisto db export --labels first_dump --labels second_dump
mephisto db export --export-tasks-by-ids 1 --delete-exported-data --randomize-legacy-ids --export-indent 4
```

Options (all optional):

- `-tn/--export-tasks-by-names` - names of Tasks that will be exported
- `-ti/--export-tasks-by-ids` - ids of Tasks that will be exported
- `-tri/--export-task-runs-by-ids` - ids of TaskRuns that will be exported
- `-trs/--export-task-runs-since-date` - only objects created after this ISO8601 datetime will be exported
- `-l/--labels` - only data imported under these labels will be exported
- `-del/--delete-exported-data` - after exporting data, delete it from local DB
- `-r/--randomize-legacy-ids` - replace legacy autoincremented ids with
        new pseudo-random ids to avoid conflicts during data merging
- `-i/--export-indent` - make dump easy to read via formatting JSON with indentations (Default 2)
- `-v/--verbosity` - write more informative messages about progress (Default 0. Values: 0, 1)

Note that the following options cannot be used together:
`--export-tasks-by-names`, `--export-tasks-by-ids`,  `--export-task-runs-by-ids`, `--export-task-runs-since-date`, `--labels`.


## Import

This command imports data from a dump file created by `mephisto db export` command.

Examples:
```
mephisto db import --file <dump_file_name_or_path>

mephisto db import --file 2024_01_01_00_00_01_mephisto_dump.json --verbosity
mephisto db import --file 2024_01_01_00_00_01_mephisto_dump.json --labels my_first_dump
mephisto db import --file 2024_01_01_00_00_01_mephisto_dump.json --conflict-resolver MyCustomMergeConflictResolver
mephisto db import --file 2024_01_01_00_00_01_mephisto_dump.json --keep-import-metadata
```

Options:
- `-f/--file` - location of the `***.zip` dump file (filename if created in
    `<MEPHISTO_REPO>/outputs/export` folder, or absolute filepath)
- `-cr/--conflict-resolver` (Optional) - name of Python class to be used for resolving merging conflicts
    (when your local DB already has a row with same unique field value as a DB row in the dump data)
- `-l/--labels` - one or more short strings serving as a reference for the ported data (stored in `imported_data` table),
    so later you can export the imported data with `--labels` export option
- `-k/--keep-import-metadata` - write data from `imported_data` table of the dump (by default it's not imported)
- `-v/--verbosity` - level of logging (default: 0; values: 0, 1)

Note that before every import we create a full snapshot copy of your local data, by
archiving content of your `data` directory. If any data gets corrupte during the import,
you can always return to the original state by replacing your `data` folder with the snaphot.

## Backup

Creates full backup of all current data (Mephisto DB, provider-specific datastores, and related files) on local machine.

```
mephisto db backup
```


## Restore

Restores all data (Mephisto DB, provider-specific datastores, and related files) from a backup archive.

Note that it will erase all current data, and you may want to run command `mephisto db backup` beforehand.

Examples:
```
mephisto db restore --file <backup_file_name_or_path>

mephisto db restore --file 2024_01_01_00_10_01.zip
```

Options:
- `-f/--file` - location of the `***.zip` backup file (filename if created in
    `<MEPHISTO_REPO>/outputs/backup` folder, or absolute filepath)
- `-v/--verbosity` - level of logging (default: 0; values: 0, 1)


## Note on legacy PKs

Prior to release `v1.4` of Mephisto, its DB schemas used auto-incremented integer primary keys. While convenient for debugging, it causes problems during data import/export.

As of `v1.4` we have replaced these "legacy" PKs with quazi-random integers (for backward compatibility their values are designed to be above 1,000,000).

If you do wish to use import/export commands with your "legacy" data, include the `--randomize-legacy-ids` option. It prevents data corruption when merging 2 sets of "legacy" data (because they will contain same integer PKs `1, 2, 3,...` for completely unrelated objects).
