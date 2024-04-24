#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from mephisto.abstractions.database import MephistoDB
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.generators.form_composer.config_validation.utils import make_error_message
from mephisto.tools.db_data_porter import backups
from mephisto.tools.db_data_porter import dumps
from mephisto.tools.db_data_porter import import_dump
from mephisto.tools.db_data_porter.constants import BACKUP_OUTPUT_DIR
from mephisto.tools.db_data_porter.constants import EXPORT_OUTPUT_DIR
from mephisto.tools.db_data_porter.constants import IMPORTED_DATA_TABLE_NAME
from mephisto.tools.db_data_porter.constants import MEPHISTO_DUMP_KEY
from mephisto.tools.db_data_porter.constants import METADATA_DUMP_KEY
from mephisto.tools.db_data_porter.constants import MIGRATIONS_TABLE_NAME
from mephisto.tools.db_data_porter.randomize_ids import randomize_ids
from mephisto.tools.db_data_porter.validation import validate_dump_data
from mephisto.utils import db as db_utils
from mephisto.utils.dirs import get_data_dir
from mephisto.utils.misc import serialize_date_to_python
from mephisto.utils.console_writer import ConsoleWriter

logger = ConsoleWriter()


class DBDataPorter:
    """
    Import, export, backup and restore DB data.

    This class contains the main logic of commands `mephisto db ...`.
    """

    def __init__(self, db=None):
        # Load Mephisto DB and providers' datastores
        if db is None:
            db = LocalMephistoDB()
        self.db = db
        self.provider_datastores: Dict[str, "MephistoDB"] = db_utils.get_providers_datastores(
            self.db,
        )

        # Cached Primary Keys
        self._pk_substitutions = {}

    @staticmethod
    def _get_root_mephisto_repo_dir() -> str:
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)
        ))))

    def _get_export_dir(self) -> str:
        root_dir = self._get_root_mephisto_repo_dir()
        export_path = os.path.join(root_dir, EXPORT_OUTPUT_DIR)
        # Create dirs if needed
        os.makedirs(export_path, exist_ok=True)
        return export_path

    def _get_backup_dir(self) -> str:
        root_dir = self._get_root_mephisto_repo_dir()
        backup_path = os.path.join(root_dir, BACKUP_OUTPUT_DIR)
        # Create dirs if needed
        os.makedirs(backup_path, exist_ok=True)
        return backup_path

    @staticmethod
    def _make_export_timestamp() -> str:
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    @staticmethod
    def _make_dump_name(timestamp: str) -> str:
        return f"{timestamp}_mephisto_dump"

    @staticmethod
    def _make_export_dump_file_path(export_path: str, dump_name: str) -> str:
        file_name = f"{dump_name}.json"
        file_path = os.path.join(export_path, file_name)
        return file_path

    def _prepare_dump_data(
        self,
        task_names: Optional[List[str]] = None,
        task_ids: Optional[List[str]] = None,
        task_run_ids: Optional[List[str]] = None,
        task_runs_labels: Optional[List[str]] = None,
        since_datetime: Optional[datetime] = None,
        randomize_legacy_ids: Optional[bool] = False,
    ) -> dict:
        partial = bool(task_names or task_ids or task_run_ids or task_runs_labels or since_datetime)
        if not partial:
            dump_data = dumps.prepare_full_dump_data(self.db, self.provider_datastores)
        else:
            dump_data = dumps.prepare_partial_dump_data(
                self.db,
                task_names=task_names,
                task_ids=task_ids,
                task_run_ids=task_run_ids,
                task_runs_labels=task_runs_labels,
                since_datetime=since_datetime,
            )

        if randomize_legacy_ids:
            randomize_ids_results = randomize_ids(self.db, dump_data, legacy_only=True)
            dump_data = randomize_ids_results["updated_dump"]
            self._pk_substitutions = randomize_ids_results["pk_substitutions"]

        return dump_data

    def _get_latest_migrations(self) -> Dict[str, Union[None, str]]:
        db_and_datastores = {
            MEPHISTO_DUMP_KEY: self.db,
            **self.provider_datastores,
        }
        latest_migrations = {}
        for db_name, db in db_and_datastores.items():
            try:
                latest_migration = db_utils.get_latest_row_from_table(db, MIGRATIONS_TABLE_NAME)
            except Exception as e:
                # This is almost unreal scenario, but it should be covered anyway.
                # If somebody runs this code, it must create this table in all DB and datastores,
                # right in the beginning, far away from this part of the code
                logger.warning(f"[yellow]No 'migrations' table found. {e}[/yellow]")
                latest_migration = None

            migration_name = latest_migration["name"] if latest_migration else None
            latest_migrations[db_name] = migration_name

        return latest_migrations

    @staticmethod
    def _ask_user_if_they_are_sure() -> bool:
        question = input(
            "Are you sure? "
            "It will affect your databases and related files. "
            "Type 'yes' and press Enter if you want to proceed: "
        )
        if question != "yes":
            logger.info("Ok. Bye")
            exit()

        return True

    @staticmethod
    def _get_label_from_file_path(file_path: str) -> str:
        base_name = os.path.basename(file_path)
        name_without_ext = base_name.split(".")[0]
        return name_without_ext

    def export_dump(
        self,
        json_indent: Optional[int] = None,
        task_names: Optional[List[str]] = None,
        task_ids: Optional[List[str]] = None,
        task_run_ids: Optional[List[str]] = None,
        task_runs_since_date: Optional[str] = None,
        task_runs_labels: Optional[List[str]] = None,
        delete_exported_data: bool = False,
        randomize_legacy_ids: bool = False,
        verbosity: int = 0,
    ) -> dict:
        # 1. Protect from accidental launches
        if delete_exported_data:
            self._ask_user_if_they_are_sure()

        # 2. Prepare dump data with Mephisto DB and provider datastores
        since_datetime = None
        if task_runs_since_date:
            try:
                since_datetime = serialize_date_to_python(task_runs_since_date)
            except Exception:
                error_message = f"Could not parse date '{task_runs_since_date}'."
                logger.exception(f"[red]{error_message}[/red]")
                exit()

        dump_data_to_export = self._prepare_dump_data(
            task_names=task_names,
            task_ids=task_ids,
            task_run_ids=task_run_ids,
            task_runs_labels=task_runs_labels,
            since_datetime=since_datetime,
            randomize_legacy_ids=randomize_legacy_ids,
        )

        # 3. Prepare export dirs and get dump file path
        export_dir = self._get_export_dir()
        dump_timestamp = self._make_export_timestamp()
        dump_name = self._make_dump_name(dump_timestamp)
        file_path = self._make_export_dump_file_path(export_dir, dump_name)

        # 4. Prepare metadata
        metadata = {
            "migrations": self._get_latest_migrations(),
            "export_parameters": {
                "--export-indent": json_indent,
                "--export-tasks-by-names": task_names,
                "--export-tasks-by-ids": task_ids,
                "--export-task-runs-by-ids": task_run_ids,
                "--export-task-runs-since-date": task_runs_since_date,
                "--verbosity": verbosity,
            },
            "timestamp": dump_timestamp,
            "pk_substitutions": self._pk_substitutions,
        }
        dump_data_to_export[METADATA_DUMP_KEY] = metadata

        # 5. Save JSON file
        try:
            with open(file_path, "w") as f:
                f.write(json.dumps(dump_data_to_export, indent=json_indent))
        except Exception as e:
            # Remove file to not make a mess in export directory
            error_message = f"Could not create dump file {dump_data_to_export}. Reason: {str(e)}."

            if verbosity:
                logger.exception(f"[red]{error_message}[/red]")
            os.remove(file_path)
            exit()

        # 6. Archive files in file system
        exported = backups.archive_and_copy_data_files(
            self.db,
            export_dir,
            dump_name,
            dump_data_to_export,
            pk_substitutions=self._pk_substitutions,
            verbosity=verbosity,
        )

        # 7. Delete exported data if needed after backing data up
        backup_path = None
        if delete_exported_data:
            backup_dir = self._get_backup_dir()
            backup_path = backups.make_full_data_dir_backup(backup_dir, dump_timestamp)
            delete_tasks = bool(task_names or task_ids)
            is_partial_dump = bool(task_names or task_ids or task_run_ids or task_runs_since_date)
            dumps.delete_exported_data(
                db=self.db,
                dump_data_to_export=dump_data_to_export,
                pk_substitutions=self._pk_substitutions,
                partial=is_partial_dump,
                delete_tasks=delete_tasks,
            )

        data_path = None
        if exported:
            data_path = os.path.join(
                export_dir, f"{dump_name}.{backups.DEFAULT_ARCHIVE_FORMAT}",
            )

        return {
            "db_path": file_path,
            "data_path": data_path,
            "backup_path": backup_path,
        }

    def import_dump(
        self,
        dump_file_name_or_path: str,
        conflict_resolver_name: str,
        label: Optional[str] = None,
        keep_import_metadata: Optional[bool] = None,
        verbosity: int = 0,
    ):
        # 1. Check dump file path
        is_dump_path_full = os.path.isabs(dump_file_name_or_path)
        if not is_dump_path_full:
            root_dir = self._get_root_mephisto_repo_dir()
            dump_file_name_or_path = os.path.join(
                root_dir, EXPORT_OUTPUT_DIR, dump_file_name_or_path,
            )

        if not os.path.exists(dump_file_name_or_path):
            error_message = (
                f"Could not find dump file '{dump_file_name_or_path}'. "
                f"Please, specify full path to existing file or "
                f"just file name that is located in `<mephisto>/{EXPORT_OUTPUT_DIR}`."
            )

            if verbosity:
                logger.exception(f"[red]{error_message}[/red]")
            exit()

        # 2. Read dump file
        with open(dump_file_name_or_path, "r") as f:
            try:
                dump_file_data: dict = json.loads(f.read())
            except Exception as e:
                error_message = (
                    f"Could not read JSON from dump file '{dump_file_name_or_path}'. "
                    f"Please, check if it has the correct format. Reason: {str(e)}"
                )
                logger.exception(f"[red]{error_message}[/red]")
                exit()

        # 3. Validate dump
        dump_data_errors = validate_dump_data(self.db, dump_file_data)
        if dump_data_errors:
            error_message = make_error_message(
                "Your dump file has incorrect format", dump_data_errors, indent=4,
            )
            logger.error(f"[red]{error_message}[/red]")
            exit()

        # 4. Protect from accidental launches
        self._ask_user_if_they_are_sure()

        # 5. Extract metadata (we do not use it for now, but it is needed to be popped)
        metadata = dump_file_data.pop(METADATA_DUMP_KEY, {})

        # 6. Make a backup of full local `data` path with databases and files.
        # This is for simulating transactional writing into several database and if sth went wrong,
        # have the ability to rollback everything we've just done
        logger.info(
            "Just in case, we are making a backup of all your local data. "
            "If something went wrong during import, we will restore all your data from this backup"
        )
        backup_dir = self._get_backup_dir()
        dump_timestamp = self._make_export_timestamp()
        backup_path = backups.make_full_data_dir_backup(backup_dir, dump_timestamp)
        logger.info(f"Backup was created successfully! File: '{backup_path}'")

        # 7. Write dump data into local DBs
        for db_or_datastore_name, db_or_datastore_data in dump_file_data.items():
            imported_data_from_dump = []

            if db_or_datastore_name == MEPHISTO_DUMP_KEY:
                # Main Mephisto database
                db = self.db
                imported_data_from_dump = dump_file_data.get(MEPHISTO_DUMP_KEY, {}).pop(
                    IMPORTED_DATA_TABLE_NAME, [],
                )
            else:
                # Provider's datastore.
                # NOTE: It is being created if it does not exist (yes, here, magically)
                datastore = self.provider_datastores.get(db_or_datastore_name)

                if not datastore:
                    logger.error(
                        f"Current version of Mephisto does not support "
                        f"'{db_or_datastore_name}' providers."
                    )
                    exit()

                db = datastore

            if verbosity:
                logger.info(f"Start importing into `{db_or_datastore_name}` database")

            label = label or self._get_label_from_file_path(dump_file_name_or_path)
            import_single_db_results = import_dump.import_single_db(
                db=db,
                provider_type=db_or_datastore_name,
                dump_data=db_or_datastore_data,
                conflict_resolver_name=conflict_resolver_name,
                label=label,
                verbosity=verbosity,
            )

            errors = import_single_db_results["errors"]

            if errors:
                error_message = make_error_message("Import was not processed", errors, indent=4)
                logger.error(f"[red]{error_message}[/red]")

                # Simulating rollback for all databases/datastores and related data files
                mephisto_data_path = get_data_dir()
                backup_path = backups.make_backup_file_path_by_timestamp(backup_dir, dump_timestamp)

                if verbosity:
                    logger.info(f"Rolling back all changed from backup '{backup_path}'")

                backups.restore_from_backup(backup_path, mephisto_data_path)

                exit()

            # Write imformation in `imported_data`
            if db_or_datastore_name == MEPHISTO_DUMP_KEY:
                # Fill `imported_data` table with imported dump
                import_dump.fill_imported_data_with_imported_dump(
                    db=db,
                    imported_data=import_single_db_results["imported_data"],
                    source_file_name=os.path.basename(dump_file_name_or_path),
                )

                # Fill `imported_data` with information from `imported_data` from dump
                if keep_import_metadata and imported_data_from_dump:
                    import_dump.import_table_imported_data_from_dump(db, imported_data_from_dump)

            if verbosity:
                logger.info(
                    f"Finished importing into `{db_or_datastore_name}` database successfully!"
                )

    def make_backup(self) -> str:
        backup_dir = self._get_backup_dir()
        dump_timestamp = self._make_export_timestamp()
        backup_path = backups.make_full_data_dir_backup(backup_dir, dump_timestamp)
        return backup_path

    def restore_from_backup(self, backup_file_name_or_path: str, verbosity: int = 0):
        # 1. Protect from accidental launches
        self._ask_user_if_they_are_sure()

        # 2. Check backup file path
        is_backup_path_full = os.path.isabs(backup_file_name_or_path)
        if not is_backup_path_full:
            root_dir = self._get_root_mephisto_repo_dir()
            backup_file_name_or_path = os.path.join(
                root_dir, BACKUP_OUTPUT_DIR, backup_file_name_or_path,
            )

        if not os.path.exists(backup_file_name_or_path):
            error_message = (
                f"Could not find backup file '{backup_file_name_or_path}'. "
                f"Please, specify full path to existing file or "
                f"just file name that is located in `<mephisto>/{BACKUP_OUTPUT_DIR}`."
            )
            logger.exception(f"[red]{error_message}[/red]")
            exit()

        if verbosity and not is_backup_path_full:
            logger.info(f"Found backup file '{backup_file_name_or_path}'")

        # 3. Restore
        mephisto_data_path = get_data_dir()
        backups.restore_from_backup(backup_file_name_or_path, mephisto_data_path)
