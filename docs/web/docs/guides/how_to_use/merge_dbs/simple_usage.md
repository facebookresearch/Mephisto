---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 1
---

# Simple usage


## Introduction

We realized that caompanies can be big, and they can run many tasks on different computers/servers, 
or even one task in several departments or school classes.
But later it is much easier to review all tasks together.

And here is the solution - merging tasks data into simple one.


## How it works

1. You create full backup to save all your data to have the ability to roll all changes back if somthing went wrong
2. Export tasks into JSON dump file with related files in ZIP archive
3. Send or collect all dumps together
4. Use your main project or new Mehisto project to import all these dumps into it
5. Restore from backup if changed your mind or start from scratch


## Most common scenario of usage

### Backup your main project

If you already have some kind of main Mephisto project where all your tasks were processed, 
you may want to merge a dump into this exact project.
We strongly recommend to make a backup of all your data manually and save it somewhere you can easily find.

The command is:

```shell
mephisto db backup
```

And you will see text like this

```
Started making backup
Finished successfully! File: '/<MEPHISTO_PATH>/outputs/backup/2024_01_01_00_00_01_mephisto_backup.zip
```

Find and copy this file.

### Export data in dump

To make a dump with all you data, use simple command:

```shell
mephisto db export
```

if you want to export just 2 tasks from 10, you need to add an option:

```shell
mephisto db export --export-tasks-by-names "My first Task" --export-tasks-by-names "My second Task" 
```

If you run tasks before June 2024 you should use parameter `--randomize-legacy-ids`.
Why do you need this? We modified our Primary Keys in our databases. 
They were autoincremented and in all you projects start from 1.
It will bring us into conflicts in all databases. 
So, this parameter will regenerate randomly all Primary Keys and replace Foreign Keys with them as well.
Note that it will not affect databases, Primary Keys will be new only in dump.

```shell
mephisto db export --randomize-legacy-ids
```

And you will see text like this

```
Started exporting
Run command for all TaskRuns.
Finished successfully! 
Files created:
        - Database dump - /<MEPHISTO_PATH>/outputs/export/2024_01_01_00_00_01_mephisto_dump.json
        - Data files dump - /<MEPHISTO_PATH>/outputs/export/2024_01_01_00_00_01_mephisto_dump.zip
```

### Import just created dump into main project

Put your dump into export directory `/mephisto/outputs/export/` and you can use just a dump name in the command,
or use a full path to the file. 
Let's just imagine, you put file in export directory:

```shell
mephisto db import --dump-file 2024_01_01_00_00_01_mephisto_dump.json
```

And you will see text like this

```
Started importing from dump '2024_01_01_00_00_01_mephisto_dump.json'
Are you sure? It will affect your databases and related files. Type 'yes' and press Enter if you want to proceed: yes
Just in case, we are making a backup of all your local data. If something went wrong during import, we will restore all your data from this backup
Backup was created successfully! File: '/mephisto/outputs/backup/2024_01_01_00_10_01_mephisto_backup.zip'
Finished successfully
```

Note that the progress will stop and will be waiting for your answer __yes__. 
Also, we create a backup automatically just in case too, just before all changes. 

### Restoring from backup

"OMG! I imported wrong dump! What have I done!" - you may cry.

No worries, just restore everything from your or our backup:

```shell
mephisto db restore --backup-file 2024_01_01_00_10_01.zip
```

And you will see text like this

```
Started restoring from backup '2024_01_01_00_10_01.zip'
Are you sure? It will affect your databases and related files. Type 'yes' and press Enter if you want to proceed: yes
Finished successfully
```

Note that the progress will stop and will be waiting for your answer __yes__. 

### Conclusion

Now, after you merged your two projects, you can easily start
[reviewing your tasks](/docs/guides/how_to_use/review_app/overview/).
