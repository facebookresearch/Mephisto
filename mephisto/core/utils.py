#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import functools
from mephisto.data_model.constants import NO_PROJECT_NAME

from typing import Optional, Any, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.crowd_provider import CrowdProvider
    from mephisto.data_model.task_runner import TaskRunner


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


def get_gallery_dir() -> str:
    """
    Return the path to the mephisto task gallery
    """
    return os.path.expanduser("~/mephisto/gallery/")


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
    # TODO be able to configure this kind of thing
    return os.path.expanduser("~/mephisto/mephisto/tasks/")


def get_data_dir() -> str:
    """
    Return the directory where the mephisto data is expected to go
    """
    # TODO be able to configure this kind of thing
    return os.path.expanduser("~/mephisto/data")

def get_mephisto_tmp_dir() -> str:
    """
    Return the directory where the mephisto temporary build files go
    """
    # TODO be able to configure this kind of thing
    return os.path.expanduser("~/mephisto/tmp")


def get_dir_for_run(run_id: str, project_name: str = NO_PROJECT_NAME) -> str:
    """
    Return the directory where the mephisto run data is expected to go
    """
    return os.path.join(get_data_dir(), "runs", project_name, run_id)


def get_crowd_provider_from_type(provider_type: str) -> Type["CrowdProvider"]:
    """
    Return the crowd provider class for the given string
    """
    # TODO pull these from the files, then cache the results?
    if provider_type == "mock":
        from mephisto.providers.mock.mock_provider import MockProvider

        return MockProvider
    if provider_type == "mturk":
        from mephisto.providers.mturk.mturk_provider import MTurkProvider

        return MTurkProvider
    if provider_type == "mturk_sandbox":
        from mephisto.providers.mturk_sandbox.sandbox_mturk_provider import (
            SandboxMTurkProvider,
        )

        return SandboxMTurkProvider
    raise NotImplementedError()


def get_blueprint_from_type(task_type: str) -> Type["TaskRunner"]:
    """
    Return the task runner class for the given string
    """
    # TODO construct this map automatically
    if task_type == "mock":
        from mephisto.server.blueprints.mock.mock_blueprint import MockBlueprint

        return MockBlueprint
    if task_type == "static":
        from mephisto.server.blueprints.static_task.static_blueprint import StaticBlueprint

        return StaticBlueprint
    raise NotImplementedError()


@functools.lru_cache(maxsize=1)
def get_valid_provider_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    # TODO query this from the providers folder
    return ["mock", "mturk", "mturk_sandbox"]
