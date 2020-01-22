#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import signal
import subprocess
import sh
import shutil
import shlex
import time

from mephisto.data_model.architect import Architect
from typing import Any, Optional, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB
    from argparse import _ArgumentGroup as ArgumentGroup

from mephisto.server.architects.router.build_router import build_router
from mephisto.core.utils import get_mephisto_tmp_dir


class LocalArchitect(Architect):
    """
    Provides methods for setting up a server locally and deploying tasks
    onto that server.
    """

    def __init__(
        self,
        db: "MephistoDB",
        opts: Dict[str, str],
        task_run: "TaskRun",
        build_dir_root: str,
    ):
        """Create an architect for use in testing"""
        self.task_run = task_run
        self.build_dir = build_dir_root
        self.task_run_id = task_run.db_id
        # TODO move some of this into the db, server status
        # needs to be in order to restart
        self.server_process_pid: Optional[int] = None
        self.server_process: Optional[subprocess.Popen] = None
        self.server_dir: Optional[str] = None
        self.running_dir: Optional[str] = None
        self.hostname: Optional[str] = opts.get("hostname")
        self.port: Optional[str] = opts.get("port")
        self.cleanup_called = False

    def get_socket_urls(self) -> List[str]:
        """Return the path to the local server socket"""
        assert self.hostname is not None, "No hostname for socket"
        assert self.port is not None, "No ports for socket"
        if "https://" in self.hostname:
            basename = self.hostname.split("https://")[1]
            protocol = "wss"
        elif "http://" in self.hostname:
            basename = self.hostname.split("http://")[1]
            protocol = "ws"
        else:
            basename = self.hostname
            protocol = "ws"

        if basename in ["localhost", "127.0.0.1"]:
            protocol = "ws"

        return [f"{protocol}://{basename}:{self.port}/"]

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Adds LocalArchitect arguments to the group

        Local architects can set hostname and port appropriately
        """
        super(LocalArchitect, cls).add_args_to_group(group)

        group.description = """
            LocalArchitect: Local servers can configure the deploy
            location and port to run on.
        """
        group.add_argument(
            "--hostname",
            dest="hostname",
            help="Location of the server",
            default="localhost",
        )
        group.add_argument(
            "--port", dest="port", help="Port to launch the server on", default="3000"
        )
        # TODO be able to specify the public address location
        # separately from the hostname
        return

    def prepare(self) -> str:
        """Mark the preparation call"""
        self.server_dir = build_router(self.build_dir, self.task_run)
        return self.server_dir

    def deploy(self) -> str:
        """Deploy the server from a local folder for this task"""
        assert self.server_dir is not None, "Deploy called before prepare"
        self.running_dir = os.path.join(
            get_mephisto_tmp_dir(), f"local_server_{self.task_run_id}", "server"
        )

        shutil.copytree(self.server_dir, self.running_dir)

        return_dir = os.getcwd()
        os.chdir(self.running_dir)
        self.server_process = subprocess.Popen(
            ["node", "server.js"], preexec_fn=os.setpgrp
        )
        self.server_process_pid = self.server_process.pid
        os.chdir(return_dir)

        time.sleep(1)
        print("Server running locally with pid {}.".format(self.server_process_pid))
        host = self.hostname
        port = self.port
        if host is None:
            host = input(
                "Please enter the public server address, like https://hostname.com: "
            )
            self.hostname = host
        if port is None:
            port = input("Please enter the port given above, likely 3000: ")
            self.port = port
        return "{}:{}".format(host, port)

    def cleanup(self) -> None:
        """Cleanup the built directory"""
        assert self.server_dir is not None, "Cleanup called before prepare"
        sh.rm(shlex.split("-rf " + self.server_dir))

    def shutdown(self) -> None:
        """Find the server process, shut it down, then remove the build directory"""
        assert self.running_dir is not None, "shutdown called before deploy"
        if self.server_process is None:
            assert self.server_process_pid is not None, "No server id to kill"
            os.kill(self.server_process_pid, signal.SIGTERM)
        else:
            self.server_process.terminate()
            self.server_process.wait()
        sh.rm(shlex.split("-rf " + self.running_dir))
