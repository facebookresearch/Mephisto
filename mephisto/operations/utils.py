#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys, glob, importlib

import shlex
from distutils.dir_util import copy_tree
import functools
from mephisto.data_model.constants import NO_PROJECT_NAME
from mephisto.operations.config_handler import (
    add_config_arg,
    get_config_arg,
    CORE_SECTION,
    DATA_STORAGE_KEY,
    DEFAULT_CONFIG_FILE,
)
from omegaconf import OmegaConf, MISSING, DictConfig
from dataclasses import fields, Field
from typing import Optional, Dict, Any, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.data_model.task_runner import TaskRunner
    from mephisto.abstractions.architect import Architect
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.requester import Requester


loaded_data_dir = None


def ensure_user_confirm(display_text, skip_input=False) -> None:
    """
    Helper to provide the flow for having a user confirm a specific occurrence
    before it happens. skip_input will make this method return without
    checking, which is useful for automated scripts
    """
    if skip_input:
        return
    res = input(f'{display_text}\nEnter "n" to exit and anything else to continue:')
    if res == "n":
        raise SystemExit(0)
    return


def get_root_dir() -> str:
    """Return the currently configured root mephisto directory"""
    # This file is at ROOT/mephisto/core/utils.py
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_mock_requester(db) -> "Requester":
    """Get or create a mock requester to use for test tasks"""
    # TODO(#98) Need to split utils into those operating for the data model
    # and those operating on the data model, and those operating beyond
    mock_requesters = db.find_requesters(provider_type="mock")
    if len(mock_requesters) == 0:
        db.new_requester("MOCK_REQUESTER", "mock")
    mock_requesters = db.find_requesters(provider_type="mock")
    return mock_requesters[0]


def get_provider_dir() -> str:
    """
    Return the path to the mephisto providers diroctory
    """
    return os.path.join(get_root_dir(), "mephisto/abstractions/providers")


def get_gallery_dir() -> str:
    """
    Return the path to the mephisto task gallery
    """
    return os.path.join(get_root_dir(), "gallery")


def get_dir_for_task(task_name: str, not_exists_ok: bool = False) -> Optional[str]:
    """
    Return the directory for the given task, if it exists. Check the user's task
    dir first and then the gallery second.
    """
    dir_path = os.path.join(get_tasks_dir(), task_name)
    if os.path.exists(dir_path) or not_exists_ok:
        return dir_path
    dir_path = os.path.join(get_gallery_dir(), task_name)
    if os.path.exists(dir_path) or not_exists_ok:
        return dir_path
    return None


def get_tasks_dir() -> str:
    """
    Return the directory where the mephisto user has configured their personal tasks
    to exist in
    """
    return os.path.join(get_root_dir(), "mephisto/tasks")


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


def build_arg_list_from_dict(in_dict: Dict[str, Any]) -> List[str]:
    arg_list = []
    for key, val in in_dict.items():
        arg_list.append(f"--{key.replace('_', '-')}")
        arg_list.append(str(val))
    return arg_list


def find_or_create_qualification(db, qualification_name) -> None:
    """
    Ensure the given qualification exists in the db,
    creating it if it doesn't already
    """
    from mephisto.abstractions.database import EntryAlreadyExistsException

    try:
        db.make_qualification(qualification_name)
    except EntryAlreadyExistsException:
        pass  # qualification already exists


def get_dict_from_field(in_field: Field) -> Dict[str, Any]:
    """
    Extract all of the arguments from an argument group
    and return a dict mapping from argument dest to argument dict
    """
    found_type = "str"
    try:
        found_type = in_field.type.__name__
    except AttributeError:
        found_type = "unknown"
    return {
        "dest": in_field.name,
        "type": found_type,
        "default": in_field.default,
        "help": in_field.metadata.get("help"),
        "choices": in_field.metadata.get("choices"),
        "required": in_field.metadata.get("required", False),
    }


def get_extra_argument_dicts(customizable_class: Any) -> List[Dict[str, Any]]:
    """
    Produce the argument dicts for the given customizable class
    (Blueprint, Architect, etc)
    """
    dict_fields = fields(customizable_class.ArgsClass)
    usable_fields = []
    group_field = None
    for f in dict_fields:
        if not f.name.startswith("_"):
            usable_fields.append(f)
        elif f.name == "_group":
            group_field = f
    parsed_fields = [get_dict_from_field(f) for f in usable_fields]
    help_text = ""
    if group_field is not None:
        help_text = group_field.metadata.get("help", "")
    return [{"desc": help_text, "args": {f["dest"]: f for f in parsed_fields}}]


def parse_arg_dict(customizable_class: Any, args: Dict[str, Any]) -> DictConfig:
    """
    Get the ArgsClass for a class, then parse the given args using
    it. Return the DictConfig of the finalized namespace.
    """
    return OmegaConf.structured(customizable_class.ArgsClass(**args))
