#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import yaml
from typing import Dict, Any

CORE_SECTION = "core"
DATA_STORAGE_KEY = "main_data_directory"

DEFAULT_CONFIG_FOLDER = os.path.expanduser("~/.mephisto/")
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_FOLDER, "config.yml")
OLD_DATA_CONFIG_LOC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "DATA_LOC"
)


def get_raw_config() -> str:
    """Returns the raw string config as written in the YAML config file"""
    with open(DEFAULT_CONFIG_FILE, "r") as config_file:
        return config_file.read().strip()


def get_config() -> Dict[str, Any]:
    """Get the data out of the YAML config file"""
    return yaml.safe_load(get_raw_config())


def write_config(config_data: Dict[str, Any]):
    """Write the given dictionary to the config yaml"""
    with open(DEFAULT_CONFIG_FILE, "w") as config_file:
        config_file.write(yaml.dump(config_data))


def init_config() -> None:
    if not os.path.exists(DEFAULT_CONFIG_FOLDER):
        os.mkdir(DEFAULT_CONFIG_FOLDER)

    if os.path.exists(OLD_DATA_CONFIG_LOC):
        print(
            f"We are migrating Mephisto's configuration to a YAML file stored at {DEFAULT_CONFIG_FILE}"
        )
        with open(OLD_DATA_CONFIG_LOC, "r") as data_dir_file:
            loaded_data_dir = data_dir_file.read().strip()
        with open(DEFAULT_CONFIG_FILE, "w") as config_file:
            config_file.write(
                yaml.dump({CORE_SECTION: {DATA_STORAGE_KEY: loaded_data_dir}})
            )
        print(f"Removing DATA_LOC configuration file from {OLD_DATA_CONFIG_LOC}")
        os.unlink(OLD_DATA_CONFIG_LOC)
    elif not os.path.exists(DEFAULT_CONFIG_FILE):
        with open(DEFAULT_CONFIG_FILE, "w") as config_fp:
            config_fp.write(yaml.dump({CORE_SECTION: {}}))


def add_config_arg(section: str, key: str, value: Any) -> None:
    """Add an argument to the YAML config, overwriting existing"""
    config = get_config()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    write_config(config)


def get_config_arg(section: str, key: str) -> Any:
    """Get an argument from the YAML config. Return None if it doesn't exist"""
    config = get_config()
    return config.get(section, {}).get(key, None)
