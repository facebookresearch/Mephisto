#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import rich_click as click  # type: ignore
from rich.markdown import Markdown
from rich_click import RichCommand
from rich_click import RichGroup

from mephisto.client.cli_db_commands import db_cli
from mephisto.client.cli_form_composer_commands import form_composer_cli
from mephisto.client.cli_metrics_commands import metrics_cli
from mephisto.client.cli_review_app_commands import review_app
from mephisto.client.cli_scripts_commands import run_script
from mephisto.client.cli_wut_commands import run_wut
from mephisto.operations.registry import get_valid_provider_types
from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.rich import console
from mephisto.utils.rich import create_table

logger = ConsoleWriter()


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
@click.argument("identifier", type=str, default=None, required=False)
@click.argument("value", type=str, default=None, required=False)
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
        logger.info(f"[green]{identifier} succesfully updated to: {value}[/green]")


@cli.command("check", cls=RichCommand)
def check():
    """Checks that mephisto is setup correctly"""
    from mephisto.abstractions.databases.local_database import LocalMephistoDB
    from mephisto.utils.testing import get_mock_requester

    try:
        db = LocalMephistoDB()
        get_mock_requester(db)
    except Exception as e:
        logger.exception("\n[red]Something went wrong.[/red]")
        click.echo(e)
        return
    logger.info("\n[green]Mephisto seems to be set up correctly.[/green]\n")


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
        logger.error("[red]No requesters found[/red]")


@cli.command("register", cls=RichCommand, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def register_provider(args):
    """Register a requester with a crowd provider"""
    if len(args) == 0:
        logger.error("\n[red]Usage: mephisto register <provider_type> arg1=value arg2=value[/red]")
        logger.info("\n[b]Valid Providers[/b]")
        provider_text = """"""
        for provider in get_valid_provider_types():
            provider_text += "\n* " + provider
        provider_text_markdown = Markdown(provider_text)
        console.print(provider_text_markdown)
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
                logger.error("[red]Requester has no args[/red]")
        return

    try:
        parsed_options = parse_arg_dict(RequesterClass, args_dict)
    except Exception as e:
        parsed_options = None
        click.echo(str(e))

    if parsed_options.name is None:
        logger.error("[red]No name was specified for the requester.[/red]")

    db = LocalMephistoDB()
    requesters = db.find_requesters(requester_name=parsed_options.name)
    if len(requesters) == 0:
        requester = RequesterClass.new(db, parsed_options.name)
    else:
        requester = requesters[0]
    try:
        requester.register(parsed_options)
        logger.info("[green]Registered successfully.[/green]")
    except Exception as e:
        click.echo(str(e))


cli.command("scripts", cls=RichCommand, context_settings={"ignore_unknown_options": True})(
    run_script
)
cli.command("wut", cls=RichCommand, context_settings={"ignore_unknown_options": True})(run_wut)
cli.command("review_app", cls=RichCommand)(review_app)
cli.add_command(form_composer_cli)
cli.add_command(metrics_cli)
cli.add_command(db_cli)


if __name__ == "__main__":
    cli()
