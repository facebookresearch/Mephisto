#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
from pathlib import Path

from mephisto.tools.db_data_porter.constants import DEFAULT_ARCHIVE_FORMAT
from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.dirs import get_data_dir

logger = ConsoleWriter()


def make_backup_file_path_by_timestamp(
    backup_dir: str,
    timestamp: str,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
) -> str:
    return os.path.join(backup_dir, f"{timestamp}_mephisto_backup.{_format}")


def make_full_data_dir_backup(backup_file_path: str, _format: str = DEFAULT_ARCHIVE_FORMAT) -> str:
    mephisto_data_dir = get_data_dir()
    shutil.make_archive(
        base_name=os.path.splitext(backup_file_path)[0],
        format=_format,
        root_dir=mephisto_data_dir,
    )
    return backup_file_path


def restore_from_backup(
    backup_file_path: str,
    extract_dir: str,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
    remove_backup: bool = False,
):
    try:
        shutil.unpack_archive(filename=backup_file_path, extract_dir=extract_dir, format=_format)

        if remove_backup:
            Path(backup_file_path).unlink(missing_ok=True)
    except Exception as e:
        logger.exception(f"[red]Could not restore backup '{backup_file_path}'. Error: {e}[/red]")
        exit()
