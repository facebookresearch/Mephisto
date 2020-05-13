import click
from click_default_group import DefaultGroup


@click.group(cls=DefaultGroup, default="web", default_if_no_args=True)
def cli():
    pass


@cli.command("web")
def web():
    """Launch a local webserver with the Mephisto UI"""
    from mephisto.client.server import app
    app.run(debug=False)


@cli.command("requesters")
def list_requesters():
    from mephisto.core.local_database import LocalMephistoDB
    from tabulate import tabulate

    db = LocalMephistoDB()
    requesters = db.find_requesters()
    dict_requesters = [r.to_dict() for r in requesters]
    click.echo(tabulate(dict_requesters, headers="keys"))

@cli.command("register", context_settings={"ignore_unknown_options": True})
@click.argument('args', nargs=-1)
def register_provider(args):

    if len(args) == 0:
        click.echo("Usage: mephisto register <provider_type> --arg1:value --arg2:value")
        return

    from mephisto.core.local_database import LocalMephistoDB
    from mephisto.core.registry import (
        get_crowd_provider_from_type,
    )
    from mephisto.core.argparse_parser import parse_arg_dict, get_extra_argument_dicts

    provider_type, requester_args = args[0], args[1:]
    args_dict = dict(arg.split(':') for arg in requester_args)
    transformed = dict( (key, {'option_string': key, 'value': value}) for (key, value) in args_dict.items())

    crowd_provider = get_crowd_provider_from_type(provider_type)
    RequesterClass = crowd_provider.RequesterClass

    if len(requester_args) == 0:
        from tabulate import tabulate
        params = get_extra_argument_dicts(RequesterClass)
        for param in params:
            click.echo(param['desc'])
            click.echo(tabulate(param['args'].values(), headers='keys'))
        return

    try:
        parsed_options = parse_arg_dict(RequesterClass, transformed)
    except Exception as e:
        click.echo(str(e))

    if "name" not in parsed_options:
        click.echo("No name was specified for the requester.")
    
    db = LocalMephistoDB()
    requesters = db.find_requesters(requester_name=parsed_options["name"])
    if len(requesters) == 0:
        requester = RequesterClass.new(db, parsed_options["name"])
    else:
        requester = requesters[0]
    try:
        requester.register(parsed_options)
        click.echo("Registered successfully.")
    except Exception as e:
        click.echo(str(e))


if __name__ == "__main__":
    cli()
