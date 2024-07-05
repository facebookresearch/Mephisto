#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import subprocess
from typing import Optional

import click

from mephisto.generators.form_composer.config_validation.separate_token_values_config import (
    update_separate_token_values_config_with_file_urls,
)
from mephisto.generators.form_composer.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.generators.form_composer.config_validation.task_data_config import (
    verify_form_composer_configs,
)
from mephisto.generators.form_composer.config_validation.token_sets_values_config import (
    update_token_sets_values_config_with_premutated_data,
)
from mephisto.generators.form_composer.config_validation.utils import is_s3_url
from mephisto.generators.form_composer.config_validation.utils import set_custom_triggers_js_env_var
from mephisto.generators.form_composer.config_validation.utils import (
    set_custom_validators_js_env_var,
)
from mephisto.utils.console_writer import ConsoleWriter

FORM_COMPOSER__DATA_DIR_NAME = "data"
FORM_COMPOSER__DATA_CONFIG_NAME = "task_data.json"
FORM_COMPOSER__FORM_CONFIG_NAME = "form_config.json"
FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME = "token_sets_values_config.json"
FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME = "separate_token_values_config.json"

logger = ConsoleWriter()


def _get_form_composer_app_path() -> str:
    app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "generators",
        "form_composer",
    )
    return app_path


@click.option("-o", "--task-data-config-only", type=bool, default=True, is_flag=True)
def form_composer(task_data_config_only: bool = True):
    """
    Generator of form-based Tasks with clean cross-platform Bootstrap forms
    with client-side form validation.
    """

    # Get app path to run Python script from there (instead of the current file's directory).
    # This is necessary, because the whole infrastructure is built relative to the location
    # of the called command-line script.
    # The other parts of the logic are inside `form_composer/run***.py` script
    app_path = _get_form_composer_app_path()
    app_data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME)

    task_data_config_path = os.path.join(app_data_path, FORM_COMPOSER__DATA_CONFIG_NAME)

    # Change dir to app dir
    os.chdir(app_path)

    # Set env var for `custom_validators.js`
    set_custom_validators_js_env_var(app_data_path)
    # Set env var for `custom_triggers.js`
    set_custom_triggers_js_env_var(app_data_path)

    verify_form_composer_configs(
        task_data_config_path=task_data_config_path,
        task_data_config_only=task_data_config_only,
    )

    # Start the process
    process = subprocess.Popen("python ./run.py", shell=True, cwd=app_path)

    # Kill subprocess when we interrupt the main process
    try:
        process.wait()
    except (KeyboardInterrupt, Exception):
        try:
            process.terminate()
        except OSError:
            pass
        process.wait()


@click.option("-v", "--verify", type=bool, default=False, is_flag=True)
@click.option("-f", "--update-file-location-values", type=str, default=None)
@click.option("-e", "--extrapolate-token-sets", type=bool, default=False, is_flag=True)
@click.option("-p", "--permutate-separate-tokens", type=bool, default=False, is_flag=True)
@click.option("-d", "--directory", type=str, default=None)
@click.option("-u", "--use-presigned-urls", type=bool, default=False, is_flag=True)
def form_composer_config(
    verify: Optional[bool] = False,
    update_file_location_values: Optional[str] = None,
    extrapolate_token_sets: Optional[bool] = False,
    permutate_separate_tokens: Optional[bool] = False,
    directory: Optional[str] = None,
    use_presigned_urls: Optional[bool] = False,
):
    """
    Prepare (parts of) config for the `form_composer` command.
    Note that each parameter is essentially a separate command, and they cannot be mixed.

    :param verify: Validate all JSON configs currently present in the form builder config directory
    :param update_file_location_values: Update existing separate-token values config
        with file URLs automatically taken from a location (e.g. an S3 folder)
    :param extrapolate_token_sets: Generate form versions based on extrapolated values of token sets
    :param permutate_separate_tokens: Create tokens sets as all possible permutations of
        values lists defined in separate-token values config
    :param directory: Path to the directory where form and token configs are located.
        By default, it's the `data` directory of `form_composer` generator
    :param use_presigned_urls: a modifier for `--update_file_location_values` parameter.
        Wraps every S3 URL with a standard handler that presigns these URLs during form rendering
        when we use `--update_file_location_values` command
    """

    # Substitute defaults for missing param values
    if directory:
        app_data_path = directory
    else:
        app_path = _get_form_composer_app_path()
        app_data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME)
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
    task_data_config_path = full_path(FORM_COMPOSER__DATA_CONFIG_NAME)
    form_config_path = full_path(FORM_COMPOSER__FORM_CONFIG_NAME)
    token_sets_values_config_path = full_path(FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME)
    separate_token_values_config_path = full_path(FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME)

    # Run the command
    if verify:
        logger.info(f"Started configs verification")
        verify_form_composer_configs(
            task_data_config_path=task_data_config_path,
            form_config_path=form_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            separate_token_values_config_path=separate_token_values_config_path,
            task_data_config_only=False,
            data_path=app_data_path,
        )
        logger.info(f"Finished configs verification")

    elif update_file_location_values:
        logger.info(
            f"[green]Started updating '{FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME}' "
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
            f"[green]Started updating '{FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME}' "
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
            f"from '{FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME}' [/green]"
        )
        create_extrapolated_config(
            form_config_path=form_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            task_data_config_path=task_data_config_path,
            data_path=app_data_path,
        )
        logger.info(f"[green]Finished successfully[/green]")

    else:
        logger.error(
            f"[red]"
            f"This command must have one of following parameters:"
            f"\n-v/--verify"
            f"\n-f/--update-file-location-value"
            f"\n-e/--extrapolate-token-set"
            f"\n-p/--permutate-separate-tokens"
            f"[/red]"
        )
