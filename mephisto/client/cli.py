#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from typing import List
from rich import print
from mephisto.client.cli_commands import get_wut_arguments
from mephisto.operations.registry import get_valid_provider_types
from mephisto.utils.rich import console, create_table
import rich_click as click  # type: ignore
import os
from rich_click import RichCommand, RichGroup
from rich.markdown import Markdown
import mephisto.scripts.local_db.review_tips_for_task as review_tips_local_db
import mephisto.scripts.local_db.remove_accepted_tip as remove_accepted_tip_local_db
import mephisto.scripts.local_db.review_feedback_for_task as review_feedback_local_db
import mephisto.scripts.local_db.load_data_to_mephisto_db as load_data_local_db
import mephisto.scripts.local_db.clear_worker_onboarding as clear_worker_onboarding_local_db
import mephisto.scripts.heroku.initialize_heroku as initialize_heroku
import mephisto.scripts.metrics.view_metrics as view_metrics
import mephisto.scripts.metrics.shutdown_metrics as shutdown_metrics
import mephisto.scripts.mturk.cleanup as cleanup_mturk
import mephisto.scripts.mturk.identify_broken_units as identify_broken_units_mturk
import mephisto.scripts.mturk.launch_makeup_hits as launch_makeup_hits_mturk
import mephisto.scripts.mturk.print_outstanding_hit_status as print_outstanding_hit_status_mturk
import mephisto.scripts.mturk.print_outstanding_hit_status as soft_block_workers_by_mturk_id_mturk


@click.group(cls=RichGroup)
def cli():
    """[deep_sky_blue4]Bring your research ideas to life
    with powerful crowdsourcing tooling[/]
    """


click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.ERRORS_SUGGESTION = (
    "\nTry running the '--help' flag for more information."
)
click.rich_click.ERRORS_EPILOGUE = (
    "To find out more, visit https://mephisto.ai/docs/guides/quickstart/\n"
)


@cli.command("web", cls=RichCommand)
def web():
    """Launch a local webserver with the Mephisto UI"""
    from mephisto.client.full.server import get_app

    get_app().run(debug=False)


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


@cli.command(
    "review",
    cls=RichCommand,
)
@click.argument(
    "review_app_dir",
    type=click.Path(exists=True),
    default=os.path.join(os.path.dirname(__file__), "review/default-ui"),
)
@click.option("-p", "--port", type=(int), default=5000)
@click.option("-o", "--output", type=(str), default="")
@click.option("-a", "--assets", "assets_dir", type=(str), default=None)
@click.option("--stdout", "output_method", flag_value="stdout")
@click.option("--file", "output_method", flag_value="file", default=True)
@click.option("--csv-headers/--no-csv-headers", default=False)
@click.option("--json/--csv", default=False)
@click.option("--db", "database_task_name", type=(str), default=None)
@click.option("--all/--one-by-one", "all_data", default=False)
@click.option("-d", "--debug", type=(bool), default=False)
def review(
    review_app_dir,
    port,
    output,
    output_method,
    csv_headers,
    json,
    database_task_name,
    all_data,
    debug,
    assets_dir,
):
    """Launch a local review UI server. Reads in rows froms stdin and outputs to either a file or stdout."""
    from mephisto.client.review.review_server import run

    if output == "" and output_method == "file":
        raise click.UsageError(
            "You must specify an output file via --output=<filename>, unless the --stdout flag is set."
        )
    if database_task_name is not None:
        from mephisto.abstractions.databases.local_database import LocalMephistoDB
        from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser

        db = LocalMephistoDB()
        mephisto_data_browser = MephistoDataBrowser(db=db)
        name_list = mephisto_data_browser.get_task_name_list()
        if database_task_name not in name_list:
            raise click.BadParameter(
                f'The task name "{database_task_name}" did not exist in MephistoDB.\n\nPerhaps you meant one of these? {", ".join(name_list)}\n\nFlag usage: mephisto review --db [task_name]\n'
            )

    run(
        review_app_dir,
        port,
        output,
        csv_headers,
        json,
        database_task_name,
        all_data,
        debug,
        assets_dir,
    )


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


@cli.command(
    "register", cls=RichCommand, context_settings={"ignore_unknown_options": True}
)
@click.argument("args", nargs=-1)
def register_provider(args):
    """Register a requester with a crowd provider"""
    if len(args) == 0:
        print(
            "\n[red]Usage: mephisto register <provider_type> arg1=value arg2=value[/red]"
        )
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


@cli.command(
    "scripts", cls=RichCommand, context_settings={"ignore_unknown_options": True}
)
@click.argument("script_type", required=False, nargs=1)
@click.argument("script_name", required=False, nargs=1)
def run_script(script_type, script_name):
    """Run one of the many mephisto scripts."""

    def print_non_markdown_list(items: List[str]):
        res = ""
        for item in items:
            res += "\n  * " + item
        return res

    VALID_SCRIPT_TYPES = ["local_db", "heroku", "metrics", "mturk"]
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
                MTURK_VALID_SCRIPTS_NAMES[3]: print_outstanding_hit_status_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[4]: soft_block_workers_by_mturk_id_mturk.main,
            },
        },
    }

    if script_name is None or (
        script_name
        not in script_type_to_scripts_data[script_type]["valid_script_names"]
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


@cli.command(
    "metrics", cls=RichCommand, context_settings={"ignore_unknown_options": True}
)
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
        metrics_table.add_row(
            "install", f"Installs Prometheus and Grafana to {METRICS_DIR}"
        )
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
            click.echo(
                f"Metrics aren't installed! Use `mephisto metrics install` first."
            )
            return
        click.echo(f"Servers launching - use ctrl-C to shutdown")
        launch_servers_and_wait()
    else:  # command == 'cleanup':
        if not metrics_are_installed():
            click.echo(
                f"Metrics aren't installed! Use `mephisto metrics install` first."
            )
            return
        click.echo(f"Cleaning up existing servers if they exist")
        shutdown_prometheus_server()
        shutdown_grafana_server()


if __name__ == "__main__":
    cli()
