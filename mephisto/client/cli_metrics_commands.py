#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import click
from rich_click import RichCommand

from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.metrics import cleanup_metrics
from mephisto.utils.metrics import launch_servers_and_wait
from mephisto.utils.metrics import metrics_are_installed
from mephisto.utils.metrics import METRICS_DIR
from mephisto.utils.metrics import remove_metrics_files
from mephisto.utils.metrics import run_install_script

VERBOSITY_HELP = "write more informative messages about progress (Default 0. Values: 0, 1)"
VERBOSITY_DEFAULT_VALUE = 0

logger = ConsoleWriter()


@click.group(name="metrics", context_settings=dict(help_option_names=["-h", "--help"]))
def metrics_cli():
    """View task health and status with Mephisto Metrics"""
    pass


# --- INSTALL ---
@metrics_cli.command("install", cls=RichCommand)
@click.pass_context
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def install(ctx: click.Context, **options: dict):
    """Installs Prometheus and Grafana to `METRICS_DIR`"""

    if metrics_are_installed():
        click.echo(f"Metrics are already installed! See {METRICS_DIR}")
        return

    run_install_script()


# --- REINSTALL ---
@metrics_cli.command("reinstall", cls=RichCommand)
@click.pass_context
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def reinstall(ctx: click.Context, **options: dict):
    """Cleanup, remove and install Prometheus and Grafana from scratch"""

    cleanup_metrics()

    if metrics_are_installed():
        remove_metrics_files()

    run_install_script()


# --- VIEW ---
@metrics_cli.command("view", cls=RichCommand)
@click.pass_context
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def view(ctx: click.Context, **options: dict):
    """Launches a Prometheus and Grafana server, and shuts down on exit"""

    if not metrics_are_installed():
        click.echo(f"Metrics aren't installed! Use `mephisto metrics install` first.")
        return

    click.echo(f"Servers launching - use CTRL-C to shutdown")
    launch_servers_and_wait()


# --- CLEANUP ---
@metrics_cli.command("cleanup", cls=RichCommand)
@click.pass_context
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def cleanup(ctx: click.Context, **options: dict):
    """Shuts down Prometheus and Grafana resources that may have persisted"""

    if not metrics_are_installed():
        click.echo(f"Metrics aren't installed! Use `mephisto metrics install` first.")
        return

    cleanup_metrics()


# --- REMOVE ---
@metrics_cli.command("remove", cls=RichCommand)
@click.pass_context
@click.option("-v", "--verbosity", type=int, default=VERBOSITY_DEFAULT_VALUE, help=VERBOSITY_HELP)
def remove(ctx: click.Context, **options: dict):
    """Remove Prometheus and Grafana files"""

    if not metrics_are_installed():
        click.echo(f"Metrics aren't installed. Nothing to remove")
        return

    cleanup_metrics()
    remove_metrics_files()
