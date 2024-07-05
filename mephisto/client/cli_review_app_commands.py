#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import subprocess
from typing import Optional

import click
from flask.cli import pass_script_info
from flask.cli import ScriptInfo

from mephisto.tools.scripts import build_custom_bundle
from mephisto.utils.console_writer import ConsoleWriter

logger = ConsoleWriter()


@click.option("-h", "--host", type=str, default="127.0.0.1")
@click.option("-p", "--port", type=int, default=5000)
@click.option("-d", "--debug", type=bool, default=False, is_flag=True)
@click.option("-f", "--force-rebuild", type=bool, default=False, is_flag=True)
@click.option("-s", "--skip-build", type=bool, default=False, is_flag=True)
@pass_script_info
def review_app(
    info: ScriptInfo,
    host: Optional[str],
    port: Optional[int],
    debug: bool = False,
    force_rebuild: bool = False,
    skip_build: bool = False,
):
    """
    Launch a local review server.
    Custom implementation of `flask run <app_name>` command (`flask.cli.run_command`)
    """
    from flask.cli import show_server_banner
    from flask.helpers import get_debug_flag
    from mephisto.review_app.server import create_app
    from werkzeug.serving import run_simple

    # Set env variables for Review App
    app_url = f"http://{host}:{port}"
    os.environ["HOST"] = host
    os.environ["PORT"] = str(port)

    logger.info(f'[green]Review APP will start on "{app_url}" address.[/green]')

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
            logger.info(f"[blue]JS requirements are already installed.[/blue]")
        else:
            logger.info(f"[blue]Installing JS requirements started.[/blue]")
            app_started = subprocess.call(["npm", "install"], cwd=client_path)
            if app_started != 0:
                raise Exception(
                    "Please make sure npm is installed, "
                    "otherwise view the above error for more info."
                )
            logger.info(f"[blue]Installing JS requirements finished.[/blue]")

        if os.path.exists(os.path.join(client_path, "build", "index.html")) and not force_rebuild:
            logger.info(f"[blue]React bundle is already built.[/blue]")
        else:
            logger.info(f"[blue]Building React bundle started.[/blue]")
            build_custom_bundle(
                review_app_path,
                force_rebuild=force_rebuild,
                webapp_name=client_dir,
                build_command="build",
            )
            logger.info(f"[blue]Building React bundle finished.[/blue]")

    # Set debug
    debug = debug if debug is not None else get_debug_flag()
    reload = debug
    debugger = debug

    # Show Flask banner
    show_server_banner(debug, info.app_import_path)

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
