#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from mephisto.utils.metrics import (
    launch_grafana_server,
    launch_prometheus_server,
    get_dash_url,
)
from mephisto.utils.logger_core import set_mephisto_log_level


def launch_servers():
    """
    Launches a prometheus and grafana server instances and print the address as well as shutdown instructions
    """
    print("Launching servers")
    set_mephisto_log_level(level="info")
    if not launch_grafana_server():
        print("Issue launching grafana, see above")
        return
    if not launch_prometheus_server():
        print("Issue launching prometheus, see above")
        return
    print(f"Waiting for grafana server to come up.")
    time.sleep(3)
    dash_url = get_dash_url()
    print(f"Dashboard is now running, you can access it at {dash_url}")
    print(
        f"Once you're no longer using it, and no jobs need it anymore, you can shutdown with `shutdown_metrics.py`"
    )


if __name__ == "__main__":
    launch_servers()
