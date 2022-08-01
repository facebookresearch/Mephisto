#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Note, all of the functions in this file take an `args` option which currently
# goes unused, but is planned for making the system more configurable in 1.1

import os
import errno
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import time

from mephisto.utils.dirs import get_mephisto_tmp_dir, get_root_dir
from mephisto.utils.logger_core import get_logger, warn_once
from prometheus_client import start_http_server
from omegaconf import DictConfig
from typing import Optional


logger = get_logger(name=__name__)


PROMETHEUS_PID_FILE = os.path.join(get_mephisto_tmp_dir(), "PROMETHEUS_PID.txt")
GRAFANA_PID_FILE = os.path.join(get_mephisto_tmp_dir(), "GRAFANA_PID.txt")
METRICS_DIR = os.path.join(get_root_dir(), "mephisto", "scripts", "metrics")
PROMETHEUS_DIR = os.path.join(METRICS_DIR, "prometheus")
PROMETHEUS_EXECUTABLE = os.path.join(PROMETHEUS_DIR, "prometheus")
PROMETHEUS_CONFIG = os.path.join(PROMETHEUS_DIR, "prometheus.yml")
GRAFANA_DIR = os.path.join(METRICS_DIR, "grafana")
GRAFANA_EXECUTABLE = os.path.join(GRAFANA_DIR, "bin", "grafana-server")


def _server_process_running(pid):
    """Check on the existing process id"""
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif err.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            return False
    else:
        return True


def _get_pid_from_file(fn):
    """Get the PID from the given file"""
    with open(fn) as pid_file:
        pid = int(pid_file.read().strip())
    return pid


def run_install_script() -> bool:
    """Run the install script from METRICS_DIR"""
    res = subprocess.check_call(
        [
            "sh",
            f"./install_metrics.sh",
        ],
        cwd=f"{METRICS_DIR}",
    )
    return res == 0


def metrics_are_installed():
    """Return whether metrics are installed"""
    return os.path.exists(PROMETHEUS_EXECUTABLE) and os.path.exists(GRAFANA_EXECUTABLE)


def launch_servers_and_wait():
    """
    Run a prometheus and grafana server, then suspend the thread
    (ensuring prometheus remains up in case a task shuts it down).
    Closes resources on Ctrl-C
    """
    try:
        print("Servers launching...")
        if not launch_grafana_server():
            print("Issue launching grafana, see above")
            return
        if not launch_prometheus_server():
            print("Issue launching prometheus, see above")
            return
        print(f"Waiting for grafana server to come up.")
        time.sleep(3)
        dash_url = get_dash_url()
        print(f"Dashboard is now running, you can access it at http://{dash_url}")
        print(f"===========================")
        print(f"| Default username: admin |")
        print(f"| Default password: admin |")
        print(f"===========================")

        while True:
            # Relaunch the server in case it's shut down by a
            # task thread
            time.sleep(5)
            if not os.path.exists(PROMETHEUS_PID_FILE):
                launch_prometheus_server()
    except KeyboardInterrupt:
        print("Caught Ctrl-C, shutting down servers")
    finally:
        shutdown_grafana_server()
        shutdown_prometheus_server()


def start_metrics_server(args: Optional["DictConfig"] = None):
    """
    Launch a metrics server for the current job. At the moment, defaults to launching on port 3031.

    Unfortunately this means we are only able to check metrics on one job at a time for now.
    Future work will extend our metrics logging configuration.
    """
    try:
        start_http_server(3031)
    except Exception as e:
        logger.exception(
            "Could not launch prometheus metrics client, perhaps a process is already running on 3031? "
            "Mephisto metrics currently only supports one Operator class at a time at the moment",
            exc_info=True,
        )


def launch_prometheus_server(args: Optional["DictConfig"] = None) -> bool:
    """
    Launch a prometheus server if one is not already running (based on having an expected PID)

    Returns success or failure
    """
    if os.path.exists(PROMETHEUS_PID_FILE):
        try:
            r = requests.get("http://localhost:9090/")
            is_ok = r.ok
        except requests.exceptions.ConnectionError:
            is_ok = False
        if not is_ok:
            logger.warning(
                "Prometheus PID existed, but server doesn't appear to be up."
            )
            if _server_process_running(_get_pid_from_file(PROMETHEUS_PID_FILE)):
                logger.warning(
                    "Prometheus server appears to be running though! exiting as unsure what to do..."
                )
                raise Exception("Prometheus server running but inaccessible")
            else:
                logger.warning(
                    "Clearing prometheus pid as the server isn't running. "
                    "Use `shutdown_prometheus_server` in the future for proper cleanup."
                )
        else:
            logger.debug("Prometheus server appears to be running at 9090")
            return True
    if not os.path.exists(PROMETHEUS_EXECUTABLE):
        warn_once(
            f"Mephisto supports rich run-time metrics visualization through Prometheus and Grafana. "
            f"If you'd like to use this feature, use `mephisto metrics install` to install."
            f"(Current install dir is '{METRICS_DIR}')'"
        )
        return False
    proc = subprocess.Popen(
        [
            f"./prometheus",
            f"--config.file={PROMETHEUS_CONFIG}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=f"{PROMETHEUS_DIR}",
    )
    with open(PROMETHEUS_PID_FILE, "w+") as pid_file:
        pid_file.write(str(proc.pid))

    logger.info(f"Prometheus server launched at process {proc.pid}")
    return True


def launch_grafana_server(args: Optional["DictConfig"] = None) -> bool:
    """
    Launch a grafana server if one is not already running (based on having an expected PID)
    """
    if os.path.exists(GRAFANA_PID_FILE):
        try:
            r = requests.get("http://localhost:3032/")
            is_ok = r.ok
        except requests.exceptions.ConnectionError:
            is_ok = False
        if not is_ok:
            logger.warning("Grafana PID existed, but server doesn't appear to be up.")
            if _server_process_running(_get_pid_from_file(GRAFANA_PID_FILE)):
                logger.warning(
                    "Grafana server appears to be running though! exiting as unsure what to do..."
                )
                raise Exception("Grafana server running but inaccessible")
            else:
                logger.warning(
                    "Clearing grafana pid as the server isn't running. "
                    "Use `shutdown_grafana_server` in the future for proper cleanup."
                )
        else:
            logger.debug("Grafana server appears to be running at 3032")
            return True
    if not os.path.exists(GRAFANA_EXECUTABLE):
        warn_once(
            f"Mephisto supports rich run-time metrics visualization through Prometheus and Grafana. "
            f"If you'd like to use this feature, use `mephisto metrics install` to install."
            f"(Current install dir is '{METRICS_DIR}')'"
        )
        return False
    proc = subprocess.Popen(
        [f"./bin/grafana-server"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=f"{GRAFANA_DIR}",
    )
    with open(GRAFANA_PID_FILE, "w+") as pid_file:
        pid_file.write(str(proc.pid))

    logger.info(f"Grafana server launched at process {proc.pid}")
    return True


def get_dash_url(args: Optional["DictConfig"] = None):
    """
    Return the url to the default Mephisto dashboard. Requires a running grafana server
    """
    headers_dict = {"Accept": "application/json"}
    r = requests.get(
        "http://localhost:3032/api/search?query=Default%20Mephisto%20Monitoring",
        headers=headers_dict,
        auth=HTTPBasicAuth("admin", "admin"),
    )
    output = r.json()
    return f"localhost:3032{output[0]['url']}"


def shutdown_prometheus_server(
    args: Optional["DictConfig"] = None, expect_exists=False
):
    """
    Shutdown the prometheus server
    """
    if os.path.exists(PROMETHEUS_PID_FILE):
        os.kill(_get_pid_from_file(PROMETHEUS_PID_FILE), 9)
        logger.info("Prometheus server shut down")
        os.unlink(PROMETHEUS_PID_FILE)
    elif expect_exists:
        logger.warning(
            f"No PID file at {PROMETHEUS_PID_FILE}... Check lsof -i :9090 to find the "
            "process if it still exists and interrupt it yourself."
        )


def shutdown_grafana_server(args: Optional["DictConfig"] = None, expect_exists=False):
    """
    Shutdown the grafana server
    """
    if os.path.exists(GRAFANA_PID_FILE):
        os.kill(_get_pid_from_file(GRAFANA_PID_FILE), 9)
        logger.info("grafana server shut down")
        os.unlink(GRAFANA_PID_FILE)
    elif expect_exists:
        logger.warning(
            f"No PID file at {GRAFANA_PID_FILE}... Check lsof -i :3032 to find the "
            "process if it still exists and interrupt it yourself."
        )
