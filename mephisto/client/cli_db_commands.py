#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

import click
from rich_click import RichCommand

from mephisto.tools.db_data_porter import DBDataPorter
from mephisto.tools.db_data_porter.constants import DEFAULT_CONFLICT_RESOLVER
from mephisto.tools.db_data_porter.export_dump import get_export_options_for_metadata
from mephisto.utils.console_writer import ConsoleWriter

VERBOSITY_HELP = "write more informative messages about progress (Default 0. Values: 0, 1)"
VERBOSITY_DEFAULT_VALUE = 0

logger = ConsoleWriter()


def _print_used_options_for_running_command_message(ctx: click.Context, options: dict):
    message = "Running command with the following options:\n"
    for p in ctx.command.params:
        values = options[p.name]

        if isinstance(values, tuple):
            values = list(values)
            if not values:
                values = None

        message += f"\t{'/'.join(p.opts)} = {values}\n"

    logger.debug(message)


@click.group(name="db", context_settings=dict(help_option_names=["-h", "--help"]))
def db_cli():
    """Operations with Mephisto DB and provider-specific datastores."""
    pass


# --- EXPORT ---
@db_cli.command("export", cls=RichCommand)
@click.pass_context
@click.option(
    "-i",
    "--export-indent",
    type=int,
    default=2,
    help="make dump easy to read via formatting JSON with indentations (Default 2)",
)
@click.option(
    "-tn",
    "--export-tasks-by-names",
    type=str,
    multiple=True,
    default=None,
    help="names of Tasks that will be exported",
)
@click.option(
    "-ti",
    "--export-tasks-by-ids",
    type=str,
    multiple=True,
    default=None,
    help="ids of Tasks that will be exported",
)
@click.option(
    "-tri",
    "--export-task-runs-by-ids",
    type=str,
    multiple=True,
    default=None,
    help="ids of TaskRuns that will be exported",
)
@click.option(
    "-trs",
    "--export-task-runs-since-date",
    type=str,
    default=None,
    help="only objects created after this ISO8601 datetime will be exported",
)
@click.option(
    "-l",
    "--labels",
    type=str,
    multiple=True,
    default=None,
    help="only data imported under these labels will be exported",
)
@click.option(
    "-del",
    "--delete-exported-data",
    type=bool,
    default=False,
    is_flag=True,
    help="after exporting data, delete it from local DB",
)
@click.option(
    "-r",
    "--randomize-legacy-ids",
    type=bool,
    default=False,
    is_flag=True,
    help=(
        "replace legacy autoincremented ids with new pseudo-random ids "
        "to avoid conflicts during data merging"
    ),
)
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def export(ctx: click.Context, **options: dict):
    """
    This command exports data from Mephisto DB and provider-specific datastores
    as an archived combination of (i) a JSON file, and (ii) a `data` catalog with related files.
    If no parameter passed, full data dump (i.e. backup) will be created.
    To pass a list of values for one command option,
    simply repeat that option name before each value.

    mephisto db export
    """
    _print_used_options_for_running_command_message(ctx, options)

    export_indent: Optional[int] = options.get("export_indent", 2)
    export_tasks_by_names: Optional[List[str]] = options.get("export_tasks_by_names")
    export_tasks_by_ids: Optional[List[str]] = options.get("export_tasks_by_ids")
    export_task_runs_by_ids: Optional[List[str]] = options.get("export_task_runs_by_ids")
    export_task_runs_since_date: Optional[str] = options.get("export_task_runs_since_date")
    export_labels: Optional[List[str]] = options.get("export_labels")
    delete_exported_data: bool = options.get("delete_exported_data", False)
    randomize_legacy_ids: bool = options.get("randomize_legacy_ids", False)
    verbosity: int = options.get("verbosity", VERBOSITY_DEFAULT_VALUE)

    porter = DBDataPorter()

    has_conflicting_task_runs_options = (
        len(
            list(
                filter(
                    bool,
                    [
                        export_tasks_by_names,
                        export_tasks_by_ids,
                        export_task_runs_by_ids,
                        export_task_runs_since_date,
                        export_labels,
                    ],
                )
            )
        )
        > 1
    )

    if has_conflicting_task_runs_options:
        logger.warning(
            "[yellow]"
            "You cannot use following options together:"
            "\n\t--export-tasks-by-names"
            "\n\t--export-tasks-by-ids"
            "\n\t--export-task-runs-by-ids"
            "\n\t--export-task-runs-since-date"
            "\n\t--labels"
            "\nUse one of them or none of them to export all data."
            "[/yellow]"
        )
        exit()

    export_results = porter.export_dump(
        json_indent=export_indent,
        task_names=export_tasks_by_names,
        task_ids=export_tasks_by_ids,
        task_run_ids=export_task_runs_by_ids,
        task_runs_since_date=export_task_runs_since_date,
        task_run_labels=export_labels,
        delete_exported_data=delete_exported_data,
        randomize_legacy_ids=randomize_legacy_ids,
        metadata_export_options=get_export_options_for_metadata(ctx, options),
        verbosity=verbosity,
    )

    backup_line = ""
    if export_results["backup_path"]:
        backup_line = f"\nCreated backup file (just in case): {export_results['backup_path']}"

    logger.info(
        f"[green]"
        f"Finished successfully, saved to file: {export_results['dump_path']}"
        f"{backup_line}"
        f"[/green]"
    )


# --- IMPORT ---
@db_cli.command("import", cls=RichCommand)
@click.pass_context
@click.option(
    "-f",
    "--file",
    type=str,
    default=None,
    help=(
        "location of the `***.zip` dump file "
        "(filename if created in `<MEPHISTO_REPO>/outputs/export` folder, or absolute filepath)"
    ),
)
@click.option(
    "-l",
    "--labels",
    type=str,
    multiple=True,
    default=None,
    help=(
        "a short strings serving as a reference for the ported data "
        "(stored in `imported_data` table), "
        "so later you can export the imported data with `--labels` export option"
    ),
)
@click.option(
    "-cr",
    "--conflict-resolver",
    type=str,
    default=DEFAULT_CONFLICT_RESOLVER,
    help=(
        "(Optional) name of Python class to be used for resolving merging conflicts "
        "(when your local DB already has a row with same unique field value "
        "as a DB row in the dump data)"
    ),
)
@click.option(
    "-k",
    "--keep-import-metadata",
    type=bool,
    default=False,
    is_flag=True,
    help="write data from `imported_data` table of the dump (by default it's not imported)",
)
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def _import(ctx: click.Context, **options: dict):
    """
    This command imports data from a dump file created by `mephisto db export` command.

    mephisto db import --file <dump_file_name_or_path>
    """
    _print_used_options_for_running_command_message(ctx, options)

    file: Optional[str] = options.get("file")
    labels: Optional[str] = options.get("labels")
    conflict_resolver: Optional[str] = options.get("conflict_resolver", DEFAULT_CONFLICT_RESOLVER)
    keep_import_metadata: Optional[bool] = options.get("keep_import_metadata", False)
    verbosity: int = options.get("verbosity", VERBOSITY_DEFAULT_VALUE)

    porter = DBDataPorter()
    results = porter.import_dump(
        dump_archive_file_name_or_path=file,
        conflict_resolver_name=conflict_resolver,
        labels=labels,
        keep_import_metadata=keep_import_metadata,
        verbosity=verbosity,
    )
    logger.info(
        f"[green]"
        f"Finished successfully. Imported {results['imported_task_runs_number']} TaskRuns"
        f"[/green]"
    )


# --- BACKUP ---
@db_cli.command("backup", cls=RichCommand)
@click.pass_context
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def backup(ctx: click.Context, **options: dict):
    """
    Creates full backup of all current data (Mephisto DB, provider-specific datastores,
    and related files) on local machine.

    mephisto db backup
    """
    _print_used_options_for_running_command_message(ctx, options)

    verbosity: int = options.get("verbosity", VERBOSITY_DEFAULT_VALUE)

    porter = DBDataPorter()
    backup_path = porter.create_backup(verbosity=verbosity)
    logger.info(f"[green]Finished successfully, saved to file: {backup_path}[/green]")


# --- RESTORE ---
@db_cli.command("restore", cls=RichCommand)
@click.pass_context
@click.option(
    "-f",
    "--file",
    type=str,
    default=None,
    help=(
        "location of the `***.zip` backup file (filename if created in "
        "`<MEPHISTO_REPO>/outputs/backup` folder, or absolute filepath)"
    ),
)
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def restore(ctx: click.Context, **options):
    """
    Restores all data (Mephisto DB, provider-specific datastores, and related files)
    from a backup archive.

    mephisto db restore --file <backup_file_name_or_path>
    """
    _print_used_options_for_running_command_message(ctx, options)

    file: str = options.get("file")
    verbosity: int = options.get("verbosity", VERBOSITY_DEFAULT_VALUE)

    porter = DBDataPorter()
    porter.restore_from_backup(backup_file_name_or_path=file, verbosity=verbosity)
    logger.info(f"[green]Finished successfully[/green]")
