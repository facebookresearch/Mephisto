#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
from typing import Optional

import click
from rich_click import RichCommand
from rich_click import RichGroup

from mephisto.client.cli_form_composer_commands import start_generator_process
from mephisto.generators.generators_utils.config_validation.separate_token_values_config import (
    update_separate_token_values_config_with_file_urls,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.generators.generators_utils.config_validation.token_sets_values_config import (
    update_token_sets_values_config_with_premutated_data,
)
from mephisto.generators.generators_utils.config_validation.utils import is_s3_url
from mephisto.generators.generators_utils.config_validation.utils import (
    set_custom_triggers_js_env_var,
)
from mephisto.generators.generators_utils.config_validation.utils import (
    set_custom_validators_js_env_var,
)
from mephisto.generators.video_annotator.config_validation.task_data_config import (
    verify_video_annotator_configs,
)
from mephisto.utils.console_writer import ConsoleWriter

VIDEO_ANNOTATOR__DATA_DIR_NAME = "data"
VIDEO_ANNOTATOR__DATA_CONFIG_NAME = "task_data.json"
VIDEO_ANNOTATOR__UNIT_CONFIG_NAME = "unit_config.json"
VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME = "token_sets_values_config.json"
VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME = "separate_token_values_config.json"

logger = ConsoleWriter()


def set_video_annotator_env_vars(use_validation_mapping_cache: bool = True):
    os.environ["VALIDATION_MAPPING"] = (
        "mephisto.generators.video_annotator.config_validation.config_validation_constants."
        "VALIDATION_MAPPING"
    )

    if use_validation_mapping_cache:
        os.environ["VALIDATION_MAPPING_USE_CACHE"] = "true"
    else:
        os.environ["VALIDATION_MAPPING_USE_CACHE"] = "false"


def _get_video_annotator_app_path() -> str:
    app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "generators",
        "video_annotator",
    )
    return app_path


@click.group(name="video_annotator", cls=RichGroup, invoke_without_command=True)
@click.pass_context
@click.option(
    "-o",
    "--task-data-config-only",
    type=bool,
    default=True,
    is_flag=True,
    help="Validate only final data config",
)
@click.option(
    "-c",
    "--conf",
    type=str,
    default=None,
    help="YAML config name (analog of `conf` option in raw python run script)",
)
def video_annotator_cli(
    ctx: click.Context,
    task_data_config_only: bool = True,
    conf: Optional[str] = None,
):
    """Generator of Tasks to annotate videos."""

    set_video_annotator_env_vars()

    if ctx.invoked_subcommand is not None:
        # It's needed to add the ability to run `config` command,
        # run default code only if there's no other command after `form_composer`
        return

    # Get app path to run Python script from there (instead of the current file's directory).
    # This is necessary, because the whole infrastructure is built relative to the location
    # of the called command-line script.
    # The other parts of the logic are inside `form_composer/run***.py` script
    app_path = _get_video_annotator_app_path()
    app_data_path = os.path.join(app_path, VIDEO_ANNOTATOR__DATA_DIR_NAME)

    task_data_config_path = os.path.join(app_data_path, VIDEO_ANNOTATOR__DATA_CONFIG_NAME)

    # Change dir to app dir
    os.chdir(app_path)

    # Set env var for `custom_validators.js`
    set_custom_validators_js_env_var(app_data_path)
    # Set env var for `custom_triggers.js`
    set_custom_triggers_js_env_var(app_data_path)

    verify_video_annotator_configs(
        task_data_config_path=task_data_config_path,
        task_data_config_only=task_data_config_only,
        force_exit=True,
    )

    # Start the process
    start_generator_process(app_path, conf)


@video_annotator_cli.command("config", cls=RichCommand)
@click.pass_context
@click.option(
    "-v",
    "--verify",
    type=bool,
    default=False,
    is_flag=True,
    help="Validate all JSON configs currently present in the video annotator config directory",
)
@click.option(
    "-f",
    "--update-file-location-values",
    type=str,
    default=None,
    help=(
        "Update existing separate-token values config "
        "with file URLs automatically taken from a location (e.g. an S3 folder)"
    ),
)
@click.option(
    "-e",
    "--extrapolate-token-sets",
    type=bool,
    default=False,
    is_flag=True,
    help="Generate assignment versions based on extrapolated values of token sets",
)
@click.option(
    "-p",
    "--permutate-separate-tokens",
    type=bool,
    default=False,
    is_flag=True,
    help=(
        "Create tokens sets as all possible permutations of "
        "values lists defined in separate-token values config"
    ),
)
@click.option(
    "-d",
    "--directory",
    type=str,
    default=None,
    help=(
        "Path to the directory where assignment and token configs are located. "
        "By default, it's the `data` directory of `video_annotator` generator"
    ),
)
@click.option(
    "-u",
    "--use-presigned-urls",
    type=bool,
    default=False,
    is_flag=True,
    help=(
        "A modifier for `--update_file_location_values` parameter. "
        "Wraps every S3 URL with a standard handler that presigns these URLs during assignment "
        "rendering when we use `--update_file_location_values` command"
    ),
)
def config(
    ctx: click.Context,
    verify: Optional[bool] = False,
    update_file_location_values: Optional[str] = None,
    extrapolate_token_sets: Optional[bool] = False,
    permutate_separate_tokens: Optional[bool] = False,
    directory: Optional[str] = None,
    use_presigned_urls: Optional[bool] = False,
):
    """
    Prepare (parts of) config for the `video_annotator` command.
    Note that each parameter is essentially a separate command, and they cannot be mixed.
    """

    app_path = _get_video_annotator_app_path()
    default_app_data_path = os.path.join(app_path, VIDEO_ANNOTATOR__DATA_DIR_NAME)

    # Substitute defaults for missing param values
    if directory:
        app_data_path = directory
    else:
        app_data_path = default_app_data_path
    logger.info(f"[blue]Using config directory: {app_data_path}[/blue]")

    # Validate param values
    if not os.path.exists(app_data_path):
        logger.error(f"[red]Directory '{app_data_path}' does not exist[/red]")
        return None

    if use_presigned_urls and not update_file_location_values:
        logger.error(
            f"[red]Parameter `--use-presigned-urls` can be used "
            f"only with `--update-file-location-values` option[/red]"
        )
        return None

    # Check files and create `data.json` config with tokens data before running a task
    full_path = lambda data_file: os.path.join(app_data_path, data_file)
    task_data_config_path = full_path(VIDEO_ANNOTATOR__DATA_CONFIG_NAME)
    unit_config_path = full_path(VIDEO_ANNOTATOR__UNIT_CONFIG_NAME)
    token_sets_values_config_path = full_path(VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME)
    separate_token_values_config_path = full_path(
        VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME
    )

    # Run the command
    if verify:
        logger.info(f"Started configs verification")
        verify_video_annotator_configs(
            task_data_config_path=task_data_config_path,
            unit_config_path=unit_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            separate_token_values_config_path=separate_token_values_config_path,
            task_data_config_only=False,
            data_path=app_data_path,
        )
        logger.info(f"Finished configs verification")

    elif update_file_location_values:
        logger.info(
            f"[green]Started updating '{VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME}' "
            f"with file URLs from '{update_file_location_values}'[/green]"
        )
        if is_s3_url(update_file_location_values):
            update_separate_token_values_config_with_file_urls(
                url=update_file_location_values,
                separate_token_values_config_path=separate_token_values_config_path,
                use_presigned_urls=use_presigned_urls,
            )
            logger.info(f"[green]Finished successfully[/green]")
        else:
            logger.info("`--update-file-location-values` must be a valid S3 URL")

    elif permutate_separate_tokens:
        logger.info(
            f"[green]Started updating '{VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME}' "
            f"with permutated separate-token values[/green]"
        )
        update_token_sets_values_config_with_premutated_data(
            separate_token_values_config_path=separate_token_values_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
        )
        logger.info(f"[green]Finished successfully[/green]")

    elif extrapolate_token_sets:
        logger.info(
            f"[green]Started extrapolating token sets values "
            f"from '{VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME}' [/green]"
        )
        create_extrapolated_config(
            unit_config_path=unit_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            task_data_config_path=task_data_config_path,
            data_path=app_data_path,
        )
        logger.info(f"[green]Finished successfully[/green]")

    else:
        logger.info(f"[green]Started configuring all steps[/green]")

        logger.info(f"[green]1. Started permutating separate-token values[/green]")
        if os.path.exists(separate_token_values_config_path):
            update_token_sets_values_config_with_premutated_data(
                separate_token_values_config_path=separate_token_values_config_path,
                token_sets_values_config_path=token_sets_values_config_path,
            )
            logger.info(f"[green]Finished permutating separate-token values[/green]")
        else:
            logger.info(
                f"[green]"
                f"Nothing to permutate. File {separate_token_values_config_path} does not exist"
                f"[/green]"
            )

        logger.info(f"[green]2. Started extrapolating token sets values[/green]")
        if os.path.exists(separate_token_values_config_path) and os.path.exists(
            token_sets_values_config_path
        ):
            create_extrapolated_config(
                unit_config_path=unit_config_path,
                token_sets_values_config_path=token_sets_values_config_path,
                task_data_config_path=task_data_config_path,
                data_path=app_data_path,
            )
            logger.info(f"[green]Finished extrapolating token sets values[/green]")
        else:
            logger.info(
                f"[green]"
                f"Nothing to extrapolate. "
                f"Files {separate_token_values_config_path} and {token_sets_values_config_path} "
                f"do not exist"
                f"[/green]"
            )

        logger.info(f"[green]3. Started verification[/green]")
        verify_video_annotator_configs(
            task_data_config_path=task_data_config_path,
            unit_config_path=unit_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            separate_token_values_config_path=separate_token_values_config_path,
            task_data_config_only=False,
            data_path=app_data_path,
        )
        logger.info(f"[green]Finished verification[/green]")

        logger.info(f"[green]Finished configuring all steps[/green]")

    # Move generated configs to default configs dir if user specified `--directory` option.
    # This is needed to start a generator with these new configs
    if directory:
        shutil.copytree(app_data_path, default_app_data_path, dirs_exist_ok=True)
