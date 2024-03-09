#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import subprocess
from typing import List
from typing import Optional

import rich_click as click  # type: ignore
from flask.cli import pass_script_info
from rich import print
from rich.markdown import Markdown
from rich_click import RichCommand
from rich_click import RichGroup

import mephisto.scripts.heroku.initialize_heroku as initialize_heroku
import mephisto.scripts.local_db.clear_worker_onboarding as clear_worker_onboarding_local_db
import mephisto.scripts.local_db.load_data_to_mephisto_db as load_data_local_db
import mephisto.scripts.local_db.remove_accepted_tip as remove_accepted_tip_local_db
import mephisto.scripts.local_db.review_feedback_for_task as review_feedback_local_db
import mephisto.scripts.local_db.review_tips_for_task as review_tips_local_db
import mephisto.scripts.metrics.shutdown_metrics as shutdown_metrics
import mephisto.scripts.metrics.view_metrics as view_metrics
import mephisto.scripts.mturk.cleanup as cleanup_mturk
import mephisto.scripts.mturk.identify_broken_units as identify_broken_units_mturk
import mephisto.scripts.mturk.launch_makeup_hits as launch_makeup_hits_mturk
import mephisto.scripts.mturk.print_outstanding_hit_status as print_outstanding_hit_status_mturk
import mephisto.scripts.mturk.print_outstanding_hit_status as soft_block_workers_by_mturk_id_mturk
import mephisto.scripts.form_composer.rebuild_all_apps as rebuild_all_apps_form_composer
from mephisto.client.cli_commands import get_wut_arguments
from mephisto.generators.form_composer.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.generators.form_composer.config_validation.task_data_config import (
    verify_form_composer_configs,
)
from mephisto.generators.form_composer.config_validation.separate_token_values_config import (
    update_separate_token_values_config_with_file_urls,
)
from mephisto.generators.form_composer.config_validation.token_sets_values_config import (
    update_token_sets_values_config_with_premutated_data,
)
from mephisto.generators.form_composer.config_validation.utils import is_s3_url
from mephisto.operations.registry import get_valid_provider_types
from mephisto.tools.scripts import build_custom_bundle
from mephisto.utils.rich import console
from mephisto.utils.rich import create_table

FORM_COMPOSER__DATA_DIR_NAME = "data"
FORM_COMPOSER__DATA_CONFIG_NAME = "task_data.json"
FORM_COMPOSER__FORM_CONFIG_NAME = "form_config.json"
FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME = "token_sets_values_config.json"
FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME = "separate_token_values_config.json"


@click.group(cls=RichGroup)
def cli():
    """[deep_sky_blue4]Bring your research ideas to life
    with powerful crowdsourcing tooling[/]
    """


click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.ERRORS_SUGGESTION = "\nTry running the '--help' flag for more information."
click.rich_click.ERRORS_EPILOGUE = (
    "To find out more, visit https://mephisto.ai/docs/guides/quickstart/\n"
)


@cli.command("config", cls=RichCommand)
@click.argument("identifier", type=(str), default=None, required=False)
@click.argument("value", type=(str), default=None, required=False)
def config(identifier, value):
    from mephisto.operations.config_handler import (
        get_config_arg,
        add_config_arg,
        get_raw_config,
        DEFAULT_CONFIG_FILE,
    )

    if identifier is None and value is None:
        # If no args, show full config:
        click.echo(f"{DEFAULT_CONFIG_FILE}:\n")
        click.echo(get_raw_config())
        return

    if "." not in identifier:
        raise click.BadParameter(
            f"Identifier must be of format: <section>.<key>\nYou passed in: {identifier}"
        )
    [section, key] = identifier.split(".")

    if value is None:
        # Read mode:
        click.echo(get_config_arg(section, key))
    else:
        # Write mode:
        add_config_arg(section, key, value)
        print(f"[green]{identifier} succesfully updated to: {value}[/green]")


@cli.command("check", cls=RichCommand)
def check():
    """Checks that mephisto is setup correctly"""
    from mephisto.abstractions.databases.local_database import LocalMephistoDB
    from mephisto.utils.testing import get_mock_requester

    try:
        db = LocalMephistoDB()
        get_mock_requester(db)
    except Exception as e:
        print("\n[red]Something went wrong.[/red]")
        click.echo(e)
        return
    print("\n[green]Mephisto seems to be set up correctly.[/green]\n")


@cli.command("requesters", cls=RichCommand)
def list_requesters():
    """Lists all registered requesters"""
    from mephisto.abstractions.databases.local_database import LocalMephistoDB

    db = LocalMephistoDB()
    requesters = db.find_requesters()
    dict_requesters = [r.to_dict() for r in requesters]
    if len(dict_requesters) > 0:
        requester_keys = list(dict_requesters[0].keys())
        requester_table = create_table(requester_keys, "\n\n Requesters")
        for requester in dict_requesters:
            requester_vals = list(requester.values())
            requester_vals = [str(x) for x in requester_vals]
            requester_table.add_row(*requester_vals)
        console.print(requester_table)
    else:
        print("[red]No requesters found[/red]")


@cli.command("register", cls=RichCommand, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def register_provider(args):
    """Register a requester with a crowd provider"""
    if len(args) == 0:
        print("\n[red]Usage: mephisto register <provider_type> arg1=value arg2=value[/red]")
        print("\n[b]Valid Providers[/b]")
        provider_text = """"""
        for provider in get_valid_provider_types():
            provider_text += "\n* " + provider
        provider_text_markdown = Markdown(provider_text)
        console.print(provider_text_markdown)
        print("")
        return

    from mephisto.abstractions.databases.local_database import LocalMephistoDB
    from mephisto.operations.registry import get_crowd_provider_from_type
    from mephisto.operations.hydra_config import (
        parse_arg_dict,
        get_extra_argument_dicts,
    )

    provider_type, requester_args = args[0], args[1:]
    args_dict = dict(arg.split("=", 1) for arg in requester_args)

    crowd_provider = get_crowd_provider_from_type(provider_type)
    RequesterClass = crowd_provider.RequesterClass

    if len(requester_args) == 0:
        params = get_extra_argument_dicts(RequesterClass)
        for param in params:
            click.echo("\n" + param["desc"])
            param_keys = list(param["args"].keys())
            if len(param_keys) > 0:
                first_arg_key = param_keys[0]
                requester_headers = list(param["args"][first_arg_key].keys())
                requester_table = create_table(requester_headers, "[b]Arguments[/b]")
                for arg in param["args"]:
                    arg_values = list(param["args"][arg].values())
                    arg_values = [str(x) for x in arg_values]
                    requester_table.add_row(*arg_values)
                console.print(requester_table)
            else:
                print("[red]Requester has no args[/red]")
        return

    try:
        parsed_options = parse_arg_dict(RequesterClass, args_dict)
    except Exception as e:
        click.echo(str(e))

    if parsed_options.name is None:
        print("[red]No name was specified for the requester.[/red]")

    db = LocalMephistoDB()
    requesters = db.find_requesters(requester_name=parsed_options.name)
    if len(requesters) == 0:
        requester = RequesterClass.new(db, parsed_options.name)
    else:
        requester = requesters[0]
    try:
        requester.register(parsed_options)
        print("[green]Registered successfully.[/green]")
    except Exception as e:
        click.echo(str(e))


@cli.command("wut", cls=RichCommand, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def run_wut(args):
    """Discover the configuration arguments for different abstractions"""
    get_wut_arguments(args)


@cli.command("scripts", cls=RichCommand, context_settings={"ignore_unknown_options": True})
@click.argument("script_type", required=False, nargs=1)
@click.argument("script_name", required=False, nargs=1)
def run_script(script_type, script_name):
    """Run one of the many mephisto scripts."""

    def print_non_markdown_list(items: List[str]):
        res = ""
        for item in items:
            res += "\n  * " + item
        return res

    VALID_SCRIPT_TYPES = ["local_db", "heroku", "metrics", "mturk", "form_composer"]
    if script_type is None or script_type.strip() not in VALID_SCRIPT_TYPES:
        print("")
        raise click.UsageError(
            "You must specify a valid script_type from below. \n\nValid script types are:"
            + print_non_markdown_list(VALID_SCRIPT_TYPES)
        )
    script_type = script_type.strip()
    LOCAL_DB_VALID_SCRIPTS_NAMES = [
        "review_tips",
        "remove_tip",
        "review_feedback",
        "load_data",
        "clear_worker_onboarding",
    ]
    HEROKU_VALID_SCRIPTS_NAMES = ["initialize"]
    METRICS_VALID_SCRIPTS_NAMES = ["view", "shutdown"]
    MTURK_VALID_SCRIPTS_NAMES = [
        "cleanup",
        "identify_broken_units",
        "launch_makeup_hits",
        "print_outstanding_hit_status",
        "soft_block_workers_by_mturk_id",
    ]
    FORM_COMPOSER_VALID_SCRIPTS_NAMES = [
        "rebuild_all_apps",
    ]
    script_type_to_scripts_data = {
        "local_db": {
            "valid_script_names": LOCAL_DB_VALID_SCRIPTS_NAMES,
            "scripts": {
                LOCAL_DB_VALID_SCRIPTS_NAMES[0]: review_tips_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[1]: remove_accepted_tip_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[2]: review_feedback_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[3]: load_data_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[4]: clear_worker_onboarding_local_db.main,
            },
        },
        "heroku": {
            "valid_script_names": HEROKU_VALID_SCRIPTS_NAMES,
            "scripts": {HEROKU_VALID_SCRIPTS_NAMES[0]: initialize_heroku.main},
        },
        "metrics": {
            "valid_script_names": METRICS_VALID_SCRIPTS_NAMES,
            "scripts": {
                METRICS_VALID_SCRIPTS_NAMES[0]: view_metrics.launch_servers,
                METRICS_VALID_SCRIPTS_NAMES[1]: shutdown_metrics.shutdown_servers,
            },
        },
        "mturk": {
            "valid_script_names": MTURK_VALID_SCRIPTS_NAMES,
            "scripts": {
                MTURK_VALID_SCRIPTS_NAMES[0]: cleanup_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[1]: identify_broken_units_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[2]: launch_makeup_hits_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[3]: rebuild_all_apps_form_composer.main,
                MTURK_VALID_SCRIPTS_NAMES[4]: soft_block_workers_by_mturk_id_mturk.main,
            },
        },
        "form_composer": {
            "valid_script_names": FORM_COMPOSER_VALID_SCRIPTS_NAMES,
            "scripts": {
                FORM_COMPOSER_VALID_SCRIPTS_NAMES[0]: rebuild_all_apps_form_composer.main,
            },
        },
    }

    if script_name is None or (
        script_name not in script_type_to_scripts_data[script_type]["valid_script_names"]
    ):
        print("")
        raise click.UsageError(
            "You must specify a valid script_name from below. \n\nValid script names are:"
            + print_non_markdown_list(
                script_type_to_scripts_data[script_type]["valid_script_names"]
            )
        )
    # runs the script
    script_type_to_scripts_data[script_type]["scripts"][script_name]()


@cli.command("metrics", cls=RichCommand, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def metrics_cli(args):
    from mephisto.utils.metrics import (
        launch_servers_and_wait,
        metrics_are_installed,
        run_install_script,
        METRICS_DIR,
        shutdown_prometheus_server,
        shutdown_grafana_server,
    )

    if len(args) == 0 or args[0] not in ["install", "view", "cleanup"]:
        print("\n[red]Usage: mephisto metrics <install|view|cleanup>[/red]")
        metrics_table = create_table(["Property", "Value"], "Metrics Arguments")
        metrics_table.add_row("install", f"Installs Prometheus and Grafana to {METRICS_DIR}")
        metrics_table.add_row(
            "view",
            "Launches a Prometheus and Grafana server, and shuts down on exit",
        )
        metrics_table.add_row(
            "cleanup",
            "Shuts down Prometheus and Grafana resources that may have persisted",
        )
        console.print(metrics_table)
        return
    command = args[0]
    if command == "install":
        if metrics_are_installed():
            click.echo(f"Metrics are already installed! See {METRICS_DIR}")
            return
        run_install_script()
    elif command == "view":
        if not metrics_are_installed():
            click.echo(f"Metrics aren't installed! Use `mephisto metrics install` first.")
            return
        click.echo(f"Servers launching - use ctrl-C to shutdown")
        launch_servers_and_wait()
    else:  # command == 'cleanup':
        if not metrics_are_installed():
            click.echo(f"Metrics aren't installed! Use `mephisto metrics install` first.")
            return
        click.echo(f"Cleaning up existing servers if they exist")
        shutdown_prometheus_server()
        shutdown_grafana_server()


@cli.command("review_app", cls=RichCommand)
@click.option("-h", "--host", type=(str), default="127.0.0.1")
@click.option("-p", "--port", type=(int), default=5000)
@click.option("-d", "--debug", type=(bool), default=None)
@click.option("-f", "--force-rebuild", type=(bool), default=False)
@click.option("-s", "--skip-build", type=(bool), default=False)
@pass_script_info
def review_app(
    info,
    host,
    port,
    debug,
    force_rebuild,
    skip_build,
):
    """
    Launch a local review server.
    Custom implementation of `flask run <app_name>` command (`flask.cli.run_command`)
    """
    from flask.cli import show_server_banner
    from flask.helpers import get_debug_flag
    from flask.helpers import get_env
    from mephisto.review_app.server import create_app
    from werkzeug.serving import run_simple

    # Set env variables for Review App
    app_url = f"http://{host}:{port}"
    os.environ["HOST"] = host
    os.environ["PORT"] = str(port)

    print(f'[green]Review APP will start on "{app_url}" address.[/green]')

    # Set up Review App Client
    if not skip_build:
        review_app_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "review_app",
        )
        client_dir = "client"
        client_path = os.path.join(review_app_path, client_dir)

        # Install JS requirements
        if os.path.exists(os.path.join(client_path, "node_modules")):
            print(f"[blue]JS requirements are already installed.[/blue]")
        else:
            print(f"[blue]Installing JS requirements started.[/blue]")
            subprocess.call(["ls"], cwd=client_path)
            app_started = subprocess.call(["npm", "install"], cwd=client_path)
            if app_started != 0:
                raise Exception(
                    "Please make sure npm is installed, "
                    "otherwise view the above error for more info."
                )
            print(f"[blue]Installing JS requirements finished.[/blue]")

        if os.path.exists(os.path.join(client_path, "build", "index.html")) and not force_rebuild:
            print(f"[blue]React bundle is already built.[/blue]")
        else:
            print(f"[blue]Building React bundle started.[/blue]")
            build_custom_bundle(
                review_app_path,
                force_rebuild=force_rebuild,
                webapp_name=client_dir,
                build_command="build",
            )
            print(f"[blue]Building React bundle finished.[/blue]")

    # Set debug
    debug = debug if debug is not None else get_debug_flag()
    reload = debug
    debugger = debug

    # Show Flask banner
    eager_loading = not reload
    show_server_banner(get_env(), debug, info.app_import_path, eager_loading)

    # Init Flask App
    app = create_app(debug=debug)

    # Run Flask server
    run_simple(
        host,
        port,
        app,
        use_reloader=reload,
        use_debugger=debugger,
    )


def _get_form_composer_app_path() -> str:
    app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "generators",
        "form_composer",
    )
    return app_path


@cli.command("form_composer", cls=RichCommand)
@click.option("-o", "--task-data-config-only", type=(bool), default=True)
def form_composer(task_data_config_only: bool = True):
    # Get app path to run Python script from there (instead of the current file's directory).
    # This is necessary, because the whole infrastructure is built relative to the location
    # of the called command-line script.
    # The other parts of the logic are inside `form_composer/run***.py` script
    app_path = _get_form_composer_app_path()
    app_data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME)

    task_data_config_path = os.path.join(app_data_path, FORM_COMPOSER__DATA_CONFIG_NAME)

    # Change dir to app dir
    os.chdir(app_path)

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


@cli.command("form_composer_config", cls=RichCommand)
@click.option("-v", "--verify", type=(bool), default=False, is_flag=True)
@click.option("-f", "--update-file-location-values", type=(str), default=None)
@click.option("-e", "--extrapolate-token-sets", type=(bool), default=False, is_flag=True)
@click.option("-p", "--permutate-separate-tokens", type=(bool), default=False, is_flag=True)
@click.option("-d", "--directory", type=(str), default=None)
@click.option("-u", "--use-presigned-urls", type=(bool), default=False, is_flag=True)
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
    print(f"[blue]Using config directory: {app_data_path}[/blue]")

    # Validate param values
    if not os.path.exists(app_data_path):
        print(f"[red]Directory '{app_data_path}' does not exist[/red]")
        return None

    if use_presigned_urls and not update_file_location_values:
        print(
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
        print(f"Started configs verification")
        verify_form_composer_configs(
            task_data_config_path=task_data_config_path,
            form_config_path=form_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            separate_token_values_config_path=separate_token_values_config_path,
            task_data_config_only=False,
        )
        print(f"Finished configs verification")

    elif update_file_location_values:
        print(
            f"[green]Started updating '{FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME}' "
            f"with file URLs from '{update_file_location_values}'[/green]"
        )
        if is_s3_url(update_file_location_values):
            update_separate_token_values_config_with_file_urls(
                url=update_file_location_values,
                separate_token_values_config_path=separate_token_values_config_path,
                use_presigned_urls=use_presigned_urls,
            )
            print(f"[green]Finished successfully[/green]")
        else:
            print("`--update-file-location-values` must be a valid S3 URL")

    elif permutate_separate_tokens:
        print(
            f"[green]Started updating '{FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME}' "
            f"with permutated separate-token values[/green]"
        )
        update_token_sets_values_config_with_premutated_data(
            separate_token_values_config_path=separate_token_values_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
        )
        print(f"[green]Finished successfully[/green]")

    elif extrapolate_token_sets:
        print(
            f"[green]Started extrapolating token sets values "
            f"from '{FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME}' [/green]"
        )
        create_extrapolated_config(
            form_config_path=form_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            task_data_config_path=task_data_config_path,
        )
        print(f"[green]Finished successfully[/green]")

    else:
        print(
            f"[red]"
            f"This command must have one of following parameters:"
            f"\n-v/--verify"
            f"\n-f/--update-file-location-value"
            f"\n-e/--extrapolate-token-set"
            f"\n-p/--permutate-separate-tokens"
            f"[/red]"
        )


if __name__ == "__main__":
    cli()
