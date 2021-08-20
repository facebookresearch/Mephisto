#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import click
from click_default_group import DefaultGroup

from omegaconf import MISSING


# @click.group(cls=DefaultGroup, default="web", default_if_no_args=True)
@click.group(cls=DefaultGroup)
def cli():
    pass


@cli.command("web")
def web():
    """Launch a local webserver with the Mephisto UI"""
    from mephisto.client.full.server import app

    app.run(debug=False)


@cli.command("config")
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
        click.echo(f"{identifier} succesfully updated to: {value}")


@cli.command("review")
@click.argument("review_app_dir", type=click.Path(exists=True))
@click.option("-p", "--port", type=(int), default=5000)
@click.option("-o", "--output", type=(str), default="")
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
    )


@cli.command("check")
def check():
    """Checks that mephisto is setup correctly"""
    from mephisto.abstractions.databases.local_database import LocalMephistoDB
    from mephisto.operations.utils import get_mock_requester

    try:
        db = LocalMephistoDB()
        get_mock_requester(db)
    except Exception as e:
        click.echo("Something went wrong.")
        click.echo(e)
        return
    click.echo("Mephisto seems to be set up correctly.")


@cli.command("requesters")
def list_requesters():
    """Lists all registered requesters"""
    from mephisto.abstractions.databases.local_database import LocalMephistoDB
    from tabulate import tabulate

    db = LocalMephistoDB()
    requesters = db.find_requesters()
    dict_requesters = [r.to_dict() for r in requesters]
    click.echo(tabulate(dict_requesters, headers="keys"))


@cli.command("register", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def register_provider(args):
    """Register a requester with a crowd provider"""
    if len(args) == 0:
        click.echo("Usage: mephisto register <provider_type> arg1=value arg2=value")
        return

    from mephisto.abstractions.databases.local_database import LocalMephistoDB
    from mephisto.operations.registry import get_crowd_provider_from_type
    from mephisto.operations.utils import parse_arg_dict, get_extra_argument_dicts

    provider_type, requester_args = args[0], args[1:]
    args_dict = dict(arg.split("=", 1) for arg in requester_args)

    crowd_provider = get_crowd_provider_from_type(provider_type)
    RequesterClass = crowd_provider.RequesterClass

    if len(requester_args) == 0:
        from tabulate import tabulate

        params = get_extra_argument_dicts(RequesterClass)
        for param in params:
            click.echo(param["desc"])
            click.echo(tabulate(param["args"].values(), headers="keys"))
        return

    try:
        parsed_options = parse_arg_dict(RequesterClass, args_dict)
    except Exception as e:
        click.echo(str(e))

    if parsed_options.name is None:
        click.echo("No name was specified for the requester.")

    db = LocalMephistoDB()
    requesters = db.find_requesters(requester_name=parsed_options.name)
    if len(requesters) == 0:
        requester = RequesterClass.new(db, parsed_options.name)
    else:
        requester = requesters[0]
    try:
        requester.register(parsed_options)
        click.echo("Registered successfully.")
    except Exception as e:
        click.echo(str(e))


@cli.command("wut", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def get_help_arguments(args):
    if len(args) == 0:
        click.echo(
            "Usage: mephisto wut <abstraction>[=<type>] [...specific args to check]"
        )
        return

    from mephisto.operations.registry import (
        get_blueprint_from_type,
        get_crowd_provider_from_type,
        get_architect_from_type,
        get_valid_blueprint_types,
        get_valid_provider_types,
        get_valid_architect_types,
    )
    from mephisto.operations.utils import get_extra_argument_dicts

    VALID_ABSTRACTIONS = ["blueprint", "architect", "requester", "provider", "task"]

    abstraction_equal_split = args[0].split("=", 1)
    abstraction = abstraction_equal_split[0]

    if abstraction not in VALID_ABSTRACTIONS:
        click.echo(
            f"Given abstraction {abstraction} not in valid abstractions {VALID_ABSTRACTIONS}"
        )
        return

    if abstraction == "task":
        from mephisto.data_model.task_config import TaskConfig

        target_class = TaskConfig
    else:
        if len(abstraction_equal_split) == 1:
            # querying about the general abstraction
            if abstraction == "blueprint":
                click.echo(
                    f"The blueprint determines the task content. Valid blueprints are {get_valid_blueprint_types()}"
                )
                return
            elif abstraction == "architect":
                click.echo(
                    f"The architect determines the server where a task is hosted. Valid architects are {get_valid_architect_types()}"
                )
                return
            elif abstraction == "requester":
                click.echo(
                    f"The requester is an account for a crowd provider. Valid requester types are {get_valid_provider_types()}. \n"
                    "Use `mephisto requesters` to see registered requesters, and `mephisto register <requester type>` to register."
                )
                return
            elif abstraction == "provider":
                click.echo(
                    f"The crowd provider determines the source of the crowd workers. Valid provider are {get_valid_provider_types()}"
                )
                return

        # There's a specific abstraction to check
        abstract_value = abstraction_equal_split[1]
        target_class = None
        valid = None
        if abstraction == "blueprint":
            try:
                target_class = get_blueprint_from_type(abstract_value)
            except:
                valid = get_valid_blueprint_types()
        elif abstraction == "architect":
            try:
                target_class = get_architect_from_type(abstract_value)
            except:
                valid = get_valid_architect_types()
        elif abstraction == "provider":
            try:
                target_class = get_crowd_provider_from_type(abstract_value)
            except:
                valid = get_valid_provider_types()
        elif abstraction == "requester":
            try:
                target_class = get_crowd_provider_from_type(
                    abstract_value
                ).RequesterClass
            except:
                valid = get_valid_provider_types()
        if valid is not None:
            click.echo(
                f"The valid types for {abstraction} are {valid}. '{abstract_value}' not found."
            )
            return

    from tabulate import tabulate

    arg_dict = get_extra_argument_dicts(target_class)[0]
    click.echo(arg_dict["desc"])
    checking_args = arg_dict["args"]
    if len(args) > 1:
        checking_args = {k: v for k, v in checking_args.items() if k in args[1:]}
    click.echo(tabulate(checking_args.values(), headers="keys"))


if __name__ == "__main__":
    cli()
