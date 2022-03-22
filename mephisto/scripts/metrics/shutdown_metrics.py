#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.utils.metrics import shutdown_grafana_server, shutdown_prometheus_server
from mephisto.utils.logger_core import set_mephisto_log_level


def shutdown_servers():
    """
    Launches a prometheus and grafana server instances and print the address as well as shutdown instructions
    """
    print("Using stored PIDs to shutdown metrics servers")
    set_mephisto_log_level(level="info")
    shutdown_prometheus_server()
    shutdown_grafana_server()
    print("Servers shut down!")


if __name__ == "__main__":
    shutdown_servers()
