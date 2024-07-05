#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time

from mephisto.utils.console_writer import ConsoleWriter
from mephisto.utils.logger_core import set_mephisto_log_level
from mephisto.utils.metrics import get_default_dashboard_url
from mephisto.utils.metrics import launch_grafana_server
from mephisto.utils.metrics import launch_prometheus_server

logger = ConsoleWriter()


def launch_servers():
    """
    Launches a prometheus and grafana server instances and print the address
    as well as shutdown instructions
    """
    logger.info("Launching servers")

    set_mephisto_log_level(level="info")

    if not launch_grafana_server():
        logger.info("Issue launching grafana, see above")
        return

    if not launch_prometheus_server():
        logger.info("Issue launching prometheus, see above")
        return

    logger.info(f"Waiting for grafana server to come up.")

    time.sleep(3)

    default_dashboard_url = get_default_dashboard_url()
    logger.info(f"Dashboard is now running, you can access it at {default_dashboard_url}")
    logger.info(
        f"Once you're no longer using it, and no jobs need it anymore, "
        f"you can shutdown with `shutdown_metrics.py`"
    )


if __name__ == "__main__":
    launch_servers()
