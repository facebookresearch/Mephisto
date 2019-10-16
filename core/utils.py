#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

def ensure_user_confirm(display_text, skip_input=False) -> None:
    """
    Helper to provide the flow for having a user confirm a specific occurrence
    before it happens. skip_input will make this method return without
    checking, which is useful for automated scripts
    """
    if skip_input:
        return
    res = input(f'{display_text}\nEnter "n" to exit and anything else to continue:')
    if res == 'n':
        raise SystemExit(0)
    return


def get_gallery_dir() -> str:
    """
    Return the path to the mephisto task gallery
    """
    return os.path.expanduser('~/mephisto/gallery/')


def get_dir_for_task(task_name: str, not_exists_ok: bool = False) -> Optional[str]:
    """
    Return the directory for the given task, if it exists. Check the user's task
    dir first and then the gallery second.
    """
    dir_path = os.path.join(get_task_dir(), task_name)
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
    return os.path.expanduser('~/mephisto/tasks/')
