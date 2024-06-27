#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

import click

from mephisto.data_model.task_run import TaskRun
from mephisto.tools.db_data_porter.constants import AGENTS_TABLE_NAME
from mephisto.tools.db_data_porter.constants import ASSIGNMENTS_TABLE_NAME
from mephisto.tools.db_data_porter.constants import DEFAULT_ARCHIVE_FORMAT
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import TASK_RUNS_TABLE_NAME
from mephisto.tools.db_data_porter.randomize_ids import get_old_pk_from_substitutions
from mephisto.utils import db as db_utils
from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.dirs import get_data_dir
from mephisto.utils.dirs import get_mephisto_tmp_dir

logger = ConsoleWriter()


def make_tmp_export_dir() -> str:
    tmp_dir = get_mephisto_tmp_dir()
    tmp_export_dir = os.path.join(tmp_dir, "export")
    os.makedirs(tmp_export_dir, exist_ok=True)
    return tmp_export_dir


def _rename_single_dir_with_new_pk(dir_path: str, substitutions: dict) -> str:
    dump_id = substitutions.get(os.path.basename(dir_path))
    renamed_dir_path = os.path.join(os.path.dirname(dir_path), dump_id)
    os.rename(dir_path, renamed_dir_path)
    return renamed_dir_path


def _rename_dirs_with_new_pks(task_run_dirs: List[str], pk_substitutions: dict) -> bool:
    task_runs_subs = pk_substitutions.get(MEPHISTO_DUMP_KEY, {}).get(TASK_RUNS_TABLE_NAME, {})
    if not task_runs_subs:
        # Nothing to rename
        return False

    assignment_subs = pk_substitutions.get(MEPHISTO_DUMP_KEY, {}).get(ASSIGNMENTS_TABLE_NAME, {})
    agent_subs = pk_substitutions.get(MEPHISTO_DUMP_KEY, {}).get(AGENTS_TABLE_NAME, {})

    task_run_dirs = [d for d in task_run_dirs if os.path.basename(d) in task_runs_subs.keys()]
    for task_run_dir in task_run_dirs:
        # Rename TaskRun dir
        renamed_task_run_dir = _rename_single_dir_with_new_pk(task_run_dir, task_runs_subs)

        # Rename Assignments dirs
        assignments_dirs = [
            os.path.join(renamed_task_run_dir, d)
            for d in os.listdir(renamed_task_run_dir)
            if d in assignment_subs.keys()
        ]
        for assignment_dir in assignments_dirs:
            renamed_assignment_dir = _rename_single_dir_with_new_pk(assignment_dir, assignment_subs)

            # Rename Agents dirs
            agents_dirs = [
                os.path.join(renamed_assignment_dir, d)
                for d in os.listdir(renamed_assignment_dir)
                if d in agent_subs.keys()
            ]
            for agent_dir in agents_dirs:
                _rename_single_dir_with_new_pk(agent_dir, agent_subs)

    return True


def _export_data_dir_for_task_runs(
    input_dir_path: str,
    archive_file_path_without_ext: str,
    task_runs: List[TaskRun],
    pk_substitutions: dict,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
    verbosity: int = 0,
) -> bool:
    tmp_export_dir = make_tmp_export_dir()

    task_run_data_dirs = [i.get_run_dir() for i in task_runs]

    try:
        tmp_task_run_dirs = []

        # Copy all files for passed TaskRuns into tmp dir
        for task_run_data_dir in task_run_data_dirs:
            relative_dir = Path(task_run_data_dir).relative_to(input_dir_path)
            tmp_task_run_dir = os.path.join(tmp_export_dir, relative_dir)

            tmp_task_run_dirs.append(tmp_task_run_dir)

            os.makedirs(tmp_task_run_dir, exist_ok=True)
            copy_tree(task_run_data_dir, tmp_task_run_dir, verbose=0)

        if pk_substitutions:
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


def archive_and_copy_data_files(
    db: "MephistoDB",
    export_dir: str,
    dump_name: str,
    dump_data: dict,
    pk_substitutions: dict,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
    verbosity: int = 0,
) -> bool:
    mephisto_data_files_path = os.path.join(get_data_dir(), "data")
    output_zip_file_base_name = os.path.join(export_dir, dump_name)  # name without extension

    if verbosity:
        logger.debug(f"Archiving data files started ...")

    mephisto_dump_data = dump_data.get(MEPHISTO_DUMP_KEY, {})
    task_runs_dump_data = mephisto_dump_data.get(TASK_RUNS_TABLE_NAME, [])

    # Get TaskRuns for PKs in dump
    task_runs: List[TaskRun] = []
    task_runs_ids: List[str] = []

    if task_runs_dump_data:
        for dump_task_run in task_runs_dump_data:
            task_runs_pk_field_name = db_utils.get_table_pk_field_name(db, TASK_RUNS_TABLE_NAME)
            dump_pk = dump_task_run[task_runs_pk_field_name]
            db_pk = get_old_pk_from_substitutions(dump_pk, pk_substitutions, TASK_RUNS_TABLE_NAME)
            db_pk = db_pk or dump_pk
            task_run: TaskRun = TaskRun.get(db, db_pk)
            task_runs.append(task_run)
            task_runs_ids.append(db_pk)

    if verbosity:
        logger.debug(f"Archiving data files for TaskRuns: {', '.join(task_runs_ids)}")

    # Export archived related data files to TaskRuns from dump
    exported = _export_data_dir_for_task_runs(
        input_dir_path=mephisto_data_files_path,
        archive_file_path_without_ext=output_zip_file_base_name,
        task_runs=task_runs,
        pk_substitutions=pk_substitutions,
        _format=_format,
        verbosity=verbosity,
    )

    if verbosity:
        logger.debug(f"Archiving data files finished")

    return exported


def unarchive_data_files(
    dump_file_path: str,
    _format: str = DEFAULT_ARCHIVE_FORMAT,
    verbosity: int = 0,
):
    # Local directory with data files for TaskRuns
    mephisto_data_files_path = os.path.join(get_data_dir(), "data")
    mephisto_data_runs_path = os.path.join(mephisto_data_files_path, "runs")

    # Tmp directory where data files for TaskRuns will be unarchived from dump to
    tmp_dir = get_mephisto_tmp_dir()
    tmp_unarchive_dir = os.path.join(tmp_dir, "unarchive")
    tmp_unarchive_task_runs_dir = os.path.join(tmp_unarchive_dir, "runs")

    try:
        # Unarchive into tmp directory
        if verbosity:
            logger.debug("Unpacking TaskRuns files ...")

        shutil.unpack_archive(
            filename=dump_file_path,
            extract_dir=tmp_unarchive_dir,
            format=_format,
        )

        if verbosity:
            logger.debug("Unpacking TaskRuns files finished")

        # Copy files
        if verbosity:
            logger.debug("Copying TaskRuns files into {mephisto_data_runs_path} ...")

        if os.path.exists(tmp_unarchive_task_runs_dir):
            copy_tree(tmp_unarchive_task_runs_dir, mephisto_data_runs_path, verbose=0)
        else:
            if verbosity:
                logger.debug("No files for TaskRuns in archive found, nothing to copy")

        if verbosity:
            logger.debug("Copying TaskRuns files finished")
    except Exception as e:
        logger.exception("Could not unpack TaskRuns files from dump")
        exit()
    finally:
        # Remove tmp dir with dump data files
        if verbosity:
            logger.debug("Removing unpacked TaskRuns files ...")

        if os.path.exists(tmp_unarchive_dir):
            shutil.rmtree(tmp_unarchive_dir)

        if verbosity:
            logger.debug("Removing unpacked TaskRuns files finished")


def get_export_options_for_metadata(ctx: click.Context, options: dict) -> Dict[str, Any]:
    export_options_for_metadata = {}

    for param in ctx.command.params:
        option_name = "/".join(param.opts)  # Concatenated option name variants (short/full)
        values = options[param.name]
        export_options_for_metadata[option_name] = values

    return export_options_for_metadata
