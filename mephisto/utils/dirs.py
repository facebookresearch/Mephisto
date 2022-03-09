#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Contains centralized accessors for default Mephisto directories
"""

import os
import sys

from distutils.dir_util import copy_tree
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.operations.config_handler import (
    add_config_arg,
    get_config_arg,
    CORE_SECTION,
    DATA_STORAGE_KEY,
    DEFAULT_CONFIG_FILE,
)
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun


loaded_data_dir = None


def get_root_dir() -> str:
    """Return the currently configured root mephisto directory"""
    # This file is at ROOT/mephisto/utils/dirs.py
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_provider_dir() -> str:
    """
    Return the path to the mephisto providers diroctory
    """
    return os.path.join(get_root_dir(), "mephisto/abstractions/providers")


def get_tasks_dir() -> str:
    """
    Return the directory where the mephisto user has configured their personal tasks
    to exist in
    """
    return os.path.join(get_root_dir(), "mephisto/tasks")


def get_dir_for_task(task_name: str, not_exists_ok: bool = False) -> Optional[str]:
    """
    Return the directory for the given task, if it exists. Check the user's task
    dir first and then the gallery second.
    """
    dir_path = os.path.join(get_tasks_dir(), task_name)
    if os.path.exists(dir_path) or not_exists_ok:
        return dir_path
    return None


def get_root_data_dir() -> str:
    """
    Return the directory where the mephisto data is expected to go
    """
    global loaded_data_dir
    if loaded_data_dir is None:
        default_data_dir = os.path.join(get_root_dir(), "data")
        actual_data_dir = get_config_arg(CORE_SECTION, DATA_STORAGE_KEY)
        if actual_data_dir is None:
            data_dir_location = input(
                "Please enter the full path to a location to store Mephisto run data. By default this "
                f"would be at '{default_data_dir}'. This dir should NOT be on a distributed file "
                "store. Press enter to use the default: "
            ).strip()
            if len(data_dir_location) == 0:
                data_dir_location = default_data_dir
            data_dir_location = os.path.expanduser(data_dir_location)
            os.makedirs(data_dir_location, exist_ok=True)
            # Check to see if there is existing data to possibly move to the data dir:
            database_loc = os.path.join(default_data_dir, "database.db")
            if os.path.exists(database_loc) and data_dir_location != default_data_dir:
                should_migrate = (
                    input(
                        "We have found an existing database in the default data directory, do you want to "
                        f"copy any existing data from the default location to {data_dir_location}? (y)es/no: "
                    )
                    .lower()
                    .strip()
                )
                if len(should_migrate) == 0 or should_migrate[0] == "y":
                    copy_tree(default_data_dir, data_dir_location)
                    print(
                        "Mephisto data successfully copied, once you've confirmed the migration worked, "
                        "feel free to remove all of the contents in "
                        f"{default_data_dir} EXCEPT for `README.md`."
                    )
            add_config_arg(CORE_SECTION, DATA_STORAGE_KEY, data_dir_location)

        loaded_data_dir = get_config_arg(CORE_SECTION, DATA_STORAGE_KEY)

        if not os.path.isdir(loaded_data_dir):
            raise NotADirectoryError(
                f"The provided Mephisto data directory {loaded_data_dir} as set in "
                f"{DEFAULT_CONFIG_FILE} is not a directory! Please locate your Mephisto "
                f"data directory and update {DEFAULT_CONFIG_FILE} to point to it."
            )

    return loaded_data_dir


def get_data_dir(root_dir: Optional[str] = None) -> str:
    """
    Return the directory where the mephisto data is expected to go
    """
    if root_dir is None:
        return get_root_data_dir()
    return os.path.join(root_dir, "data")


def get_mephisto_tmp_dir() -> str:
    """
    Return the directory where the mephisto temporary build files go
    """
    return os.path.join(get_root_dir(), "tmp")


def get_dir_for_run(task_run: "TaskRun", project_name: str = NO_PROJECT_NAME) -> str:
    """
    Return the directory where the mephisto run data is expected to go
    """
    run_id = task_run.db_id
    root_dir = task_run.db.db_root
    return os.path.join(get_data_dir(root_dir), "runs", project_name, run_id)


def get_run_file_dir() -> str:
    """
    Utility function to get the directory that a particular
    python run file is contained in, even when run from
    a different directory.

    Useful as configuration information for a task is generally
    kept within the same directory as the run script
    """
    if len(sys.argv) == 0:
        return os.getcwd()
    ran_file = sys.argv[0]
    return os.path.abspath(os.path.dirname(ran_file))
