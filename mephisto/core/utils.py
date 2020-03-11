#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys, glob, importlib

import functools
from mephisto.data_model.constants import NO_PROJECT_NAME

from typing import Optional, Any, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.crowd_provider import CrowdProvider
    from mephisto.data_model.task_runner import TaskRunner
    from mephisto.data_model.architect import Architect
    from mephisto.data_model.task import TaskRun


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
    # TODO be able to configure this kind of thing
    return os.path.expanduser("~/mephisto")


def get_provider_dir() -> str:
    """
    Return the path to the mephisto providers diroctory
    """
    return os.path.join(get_root_dir(), "mephisto/providers")


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
    return os.path.join(get_root_dir(), "data")


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


@functools.lru_cache(maxsize=30)
def get_crowd_provider_from_type(provider_type: str) -> Type["CrowdProvider"]:
    """
    Return the crowd provider class for the given string
    """
    from mephisto.data_model.crowd_provider import CrowdProvider

    # list the current providers directories
    providers_path = get_provider_dir()

    # check if the provider has a directory in the providers path
    providers_lst = get_valid_provider_types()
    is_valid_provider = provider_type in providers_lst

    if is_valid_provider:
        # full path of the current provider
        provider_dir = os.path.join(providers_path, provider_type)
        sys.path.append(provider_dir)

        # Iterate over all the files insider the provider directory
        file_paths = glob.glob(os.path.join(provider_dir, "*provider.py"))

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            module_name = os.path.splitext(file_name)[0]
            if module_name.startswith("__"):
                continue
            # -----------------------------
            # Import python file
            module = importlib.import_module(module_name)
            # -----------------------------
            # Iterate items inside imported python file
            # search for a class whose base class is CrowdProvider with the
            # defined PROVIDER_TYPE
            if not hasattr(module, "PROVIDER_TYPE"):
                # all valid crowdprovider modules should define a PROVIDER_TYPE
                continue
            found_provider_type = module.PROVIDER_TYPE  # type: ignore
            for item in dir(module):
                value = getattr(module, item)
                if "PROVIDER_TYPE" not in dir(value):
                    continue
                if value.PROVIDER_TYPE == found_provider_type:
                    if issubclass(value, CrowdProvider):
                        return value
    else:
        raise NotImplementedError(f"Missing provider type {provider_type}")
    raise NotImplementedError(f"Provider {provider_type} could not be loaded properly")


def get_blueprint_from_type(task_type: str) -> Type["TaskRunner"]:
    """
    Return the task runner class for the given string
    """
    # TODO construct this map automatically
    if task_type == "mock":
        from mephisto.server.blueprints.mock.mock_blueprint import MockBlueprint

        return MockBlueprint
    if task_type == "static":
        from mephisto.server.blueprints.static_task.static_blueprint import (
            StaticBlueprint,
        )

        return StaticBlueprint
    raise NotImplementedError(f"Missing task type {task_type}")


def get_architect_from_type(architect_type: str) -> Type["Architect"]:
    """
    Return the task runner class for the given string
    """
    # TODO construct this map automatically
    if architect_type == "mock":
        from mephisto.server.architects.mock_architect import MockArchitect

        return MockArchitect
    if architect_type == "local":
        from mephisto.server.architects.local_architect import LocalArchitect

        return LocalArchitect
    if architect_type == "heroku":
        from mephisto.server.architects.heroku_architect import HerokuArchitect

        return HerokuArchitect
    raise NotImplementedError(f"Missing task type {architect_type}")


@functools.lru_cache(maxsize=1)
def get_valid_provider_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    providers_path = get_provider_dir()
    available_providers = [
        f
        for f in os.listdir(providers_path)
        if os.path.isdir(os.path.join(providers_path, f))
    ]
    # TODO: Un-hardcode these providers. Right now we have false positives
    # flowing through, such as __pycache__.
    return ["mock", "mturk_sandbox", "mturk"]
    # return available_providers


@functools.lru_cache(maxsize=1)
def get_valid_blueprint_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    return ["mock", "static"]


@functools.lru_cache(maxsize=1)
def get_valid_architect_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    return ["mock", "heroku", "local"]
