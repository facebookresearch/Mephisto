#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import List

from mephisto.abstractions.database import MephistoDB
from mephisto.data_model.task_run import TaskRun
from mephisto.tools.db_data_porter.constants import AGENTS_TABLE_NAME
from mephisto.tools.db_data_porter.constants import ASSIGNMENTS_TABLE_NAME
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import TASK_RUNS_TABLE_NAME
from mephisto.tools.db_data_porter.randomize_ids import get_old_pk_from_substitutions
from mephisto.utils import db as db_utils
from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.dirs import get_data_dir
from mephisto.utils.dirs import get_mephisto_tmp_dir

DEFAULT_ARCHIVE_FORMAT = "zip"

logger = ConsoleWriter()


def _rename_dirs_with_new_pks(task_run_dirs: List[str], pk_substitutions: dict):
    def rename_dir_with_new_pk(dir_path: str, substitutions: dict) -> str:
        dump_id = substitutions.get(os.path.basename(dir_path))
        renamed_dir_path = os.path.join(os.path.dirname(dir_path), dump_id)
        os.rename(dir_path, renamed_dir_path)
        return renamed_dir_path

    task_runs_subs = pk_substitutions.get(MEPHISTO_DUMP_KEY, {}).get(TASK_RUNS_TABLE_NAME, {})
    if not task_runs_subs:
        # Nothing to rename
        return

    assignment_subs = pk_substitutions.get(MEPHISTO_DUMP_KEY, {}).get(ASSIGNMENTS_TABLE_NAME, {})
    agent_subs = pk_substitutions.get(MEPHISTO_DUMP_KEY, {}).get(AGENTS_TABLE_NAME, {})

    task_run_dirs = [
        d for d in task_run_dirs if os.path.basename(d) in task_runs_subs.keys()
    ]
    for task_run_dir in task_run_dirs:
        # Rename TaskRun dir
        renamed_task_run_dir = rename_dir_with_new_pk(task_run_dir, task_runs_subs)

        # Rename Assignments dirs
        assignments_dirs = [
            os.path.join(renamed_task_run_dir, d) for d in os.listdir(renamed_task_run_dir)
            if d in assignment_subs.keys()
        ]
        for assignment_dir in assignments_dirs:
            renamed_assignment_dir = rename_dir_with_new_pk(assignment_dir, assignment_subs)

            # Rename Agents dirs
            agents_dirs = [
                os.path.join(renamed_assignment_dir, d) for d in os.listdir(renamed_assignment_dir)
                if d in agent_subs.keys()
            ]
            for agent_dir in agents_dirs:
                rename_dir_with_new_pk(agent_dir, agent_subs)


def _export_data_dir_for_task_runs(
    input_dir_path: str,
    archive_file_path_without_ext: str,
    task_runs: List[TaskRun],
    pk_substitutions: dict,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
    verbosity: int = 0,
) -> bool:
    tmp_dir = get_mephisto_tmp_dir()
    tmp_export_dir = os.path.join(tmp_dir, "export")

    task_run_data_dirs = [i.get_run_dir() for i in task_runs]
    if not task_run_data_dirs:
        return False

    try:
        tmp_task_run_dirs = []

        # Copy all files for passed TaskRuns into tmp dir
        for task_run_data_dir in task_run_data_dirs:
            relative_dir = Path(task_run_data_dir).relative_to(input_dir_path)
            tmp_task_run_dir = os.path.join(tmp_export_dir, relative_dir)

            tmp_task_run_dirs.append(tmp_task_run_dir)

            os.makedirs(tmp_task_run_dir, exist_ok=True)
            copy_tree(task_run_data_dir, tmp_task_run_dir, verbose=verbosity)

        _rename_dirs_with_new_pks(tmp_task_run_dirs, pk_substitutions)

        # Create archive in export dir
        shutil.make_archive(
            base_name=archive_file_path_without_ext,
            format="zip",
            root_dir=tmp_export_dir,
        )
    finally:
        # Remove tmp dir
        if os.path.exists(tmp_export_dir):
            shutil.rmtree(tmp_export_dir)

    return True


def make_backup_file_path_by_timestamp(
    backup_dir: str, timestamp: str, _format: str = DEFAULT_ARCHIVE_FORMAT,
) -> str:
    return os.path.join(backup_dir, f"{timestamp}_mephisto_backup.{_format}")


def make_full_data_dir_backup(
    backup_dir: str, timestamp: str, _format: str = DEFAULT_ARCHIVE_FORMAT,
) -> str:
    mephisto_data_dir = get_data_dir()
    file_name_without_ext = f"{timestamp}_mephisto_backup"
    archive_file_path_without_ext = os.path.join(backup_dir, file_name_without_ext)

    shutil.make_archive(
        base_name=archive_file_path_without_ext,
        format=_format,
        root_dir=mephisto_data_dir,
    )

    return make_backup_file_path_by_timestamp(backup_dir, file_name_without_ext, _format)


def archive_and_copy_data_files(
    db: "MephistoDB",
    export_dir: str,
    dump_name: str,
    dump_data: dict,
    pk_substitutions: dict,
    verbosity: int = 0,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
) -> bool:
    mephisto_data_files_path = os.path.join(get_data_dir(), "data")
    output_zip_file_base_name = os.path.join(export_dir, dump_name)  # name without extension

    # Get TaskRuns for PKs in dump
    task_runs: List[TaskRun] = []
    for dump_task_run in dump_data[MEPHISTO_DUMP_KEY][TASK_RUNS_TABLE_NAME]:
        task_runs_pk_field_name = db_utils.get_table_pk_field_name(db, TASK_RUNS_TABLE_NAME)
        dump_pk = dump_task_run[task_runs_pk_field_name]
        db_pk = get_old_pk_from_substitutions(dump_pk, pk_substitutions, TASK_RUNS_TABLE_NAME)
        db_pk = db_pk or dump_pk
        task_run: TaskRun = TaskRun.get(db, db_pk)
        task_runs.append(task_run)

    # Export archived related data files to TaskRuns from dump
    exported = _export_data_dir_for_task_runs(
        input_dir_path=mephisto_data_files_path,
        archive_file_path_without_ext=output_zip_file_base_name,
        task_runs=task_runs,
        pk_substitutions=pk_substitutions,
        _format=_format,
        verbosity=verbosity,
    )

    return exported


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
        raise
