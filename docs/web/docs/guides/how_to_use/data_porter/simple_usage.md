---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 1
---

# Simple usage


## Introduction

Sometimes you may want to run Mephisto remotely on remote server(s) for data collection, since that stage takes a while.
The Data Porter feature allows to move around data collected by different Mephisto instances, for ease of review and record keeping.

Data Porter can do the following for you:

- Backing up your local data
- Restoring your local data
- Exporting part of your local data (into a data dump)
- Importing data from a data dump (into your local data)

Before making any changes to data, we recommend creating a backup of your local data
(so you can roll back the changes if anything goes wrong).

---

## Common use scenarios

### Backing up data

The below backup command will create an archived version of your local `data` directory
(that contains all data for the project), and place it in `outputs/backup/` directory:

```shell
mephisto db backup
```

### Restoring a backup

You can restore a snapshot of your local data from a backup data dump (created with `mephisto db backup` command):

```shell
mephisto db restore --file <FILE_PATH>
```

where `<FILE_PATH>` can be either full path to a file, or just the filename (if it's located in the `outputs/backup/` directory)

Important notes:

- Your current local data will be erased (to make room for the restored data)
- If DB schema of the data dump is outdated, Mephisto when launched will automatically try to apply all existing migrations


### Exporting data

To export all local data (and make it importable later), run

```shell
mephisto db export
```

To export partial data only partially (i.e. from a few selected Task Runs), you have a few options of identifying the imported data. The simplest method is by using Task name(s):

```shell
mephisto db export --export-tasks-by-names "My first Task" --export-tasks-by-names "My second Task"
```

This will generate an archive file in the `outputs/export/` directory.

#### Legacy PKs note

If you're exporting "legacy" data entries (i.e. created before May 2024), you should add parameter `--randomize-legacy-ids` to your export command. This will ensure lack of conflicts when importing this dump into a "legacy" dated database.
All this parameter does is change (within the dump) sequential integer PKs to random integer PKs, while preserving all object relations.


### Importing data

You can restore data dump content (created with `mephisto db export` command) into your local data like so:

```shell
mephisto db import --file <FILE_PATH>
```

where `<FILE_PATH>` can be either full path to a file, or just the filename (if it's located in the `outputs/export/` directory)

Note that before the import starts, a full backup of your local data will be automatically created and saved to `outputs/backup/` directory.
