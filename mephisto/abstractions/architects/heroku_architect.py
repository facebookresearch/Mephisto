#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import getpass
import glob
import hashlib
import netrc
import os
import platform
import sh  # type: ignore
import shlex
import shutil
import subprocess
import sys
import time
import requests
import re
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.utils.dirs import get_mephisto_tmp_dir
from mephisto.abstractions.architect import Architect, ArchitectArgs
from mephisto.abstractions.architects.router.build_router import build_router
from mephisto.abstractions.architects.channels.websocket_channel import WebsocketChannel
from mephisto.operations.registry import register_mephisto_abstraction
from typing import Any, Tuple, List, Dict, Optional, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from mephisto.abstractions._subcomponents.channel import Channel
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.blueprint import SharedTaskState
    from argparse import _ArgumentGroup as ArgumentGroup

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)

ARCHITECT_TYPE = "heroku"

USER_NAME = getpass.getuser()
HEROKU_SERVER_BUILD_DIRECTORY = "heroku_server"
HEROKU_CLIENT_URL = (
    "https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli"
)

HEROKU_WAIT_TIME = 3

HEROKU_TMP_DIR = os.path.join(get_mephisto_tmp_dir(), "heroku")
os.makedirs(HEROKU_TMP_DIR, exist_ok=True)


@dataclass
class HerokuArchitectArgs(ArchitectArgs):
    """Additional arguments for configuring a heroku architect"""

    _architect_type: str = ARCHITECT_TYPE
    use_hobby: bool = field(
        default=False, metadata={"help": "Launch on the Heroku Hobby tier"}
    )
    heroku_team: Optional[str] = field(
        default=MISSING, metadata={"help": "Heroku team to use for this launch"}
    )
    heroku_app_name: Optional[str] = field(
        default=MISSING, metadata={"help": "Heroku app name to use for this launch"}
    )
    heroku_config_args: Dict[str, str] = field(
        default_factory=dict,
        metadata={
            "help": "str:str dict containing all heroku config variables to set for the app"
        },
    )


@register_mephisto_abstraction()
class HerokuArchitect(Architect):
    """
    Sets up a server on heroku and deploys the task on that server
    """

    ArgsClass = HerokuArchitectArgs
    ARCHITECT_TYPE = ARCHITECT_TYPE

    def __init__(
        self,
        db: "MephistoDB",
        args: DictConfig,
        shared_state: "SharedTaskState",
        task_run: "TaskRun",
        build_dir_root: str,
    ):
        """
        Ensure heroku credentials are setup, then prepare the necessary files
        for launching for this task.

        All necessary paths should be built in the init or stored in the database
        such that a re-init on the same task run can pull the server information.

        This means that we can shutdown a server that is still running after a
        catastrophic failure.
        """
        # TODO(#102) put the expected info into the MephistoDB rather than storing here?
        # Servers will have a status which needs to be kept track of.
        self.args = args
        self.task_run = task_run
        self.deploy_name = f"{task_run.get_task().task_name}_{task_run.db_id}"
        self.build_dir = build_dir_root
        self.server_type = args.architect.server_type
        self.server_source_path = args.architect.get("server_source_path", None)
        self.heroku_config_args = dict(args.architect.heroku_config_args)

        # Cache-able parameters
        self.__heroku_app_name: Optional[str] = args.architect.get(
            "heroku_app_name", None
        )
        self.__heroku_executable_path: Optional[str] = None
        self.__heroku_user_identifier: Optional[str] = None

        self.created = False

    def _get_socket_urls(self) -> List[str]:
        """Returns the path to the heroku app socket"""
        heroku_app_name = self.__get_app_name()
        return ["wss://{}.herokuapp.com/".format(heroku_app_name)]

    def get_channels(
        self,
        on_channel_open: Callable[[str], None],
        on_catastrophic_disconnect: Callable[[str], None],
        on_message: Callable[[str, "Packet"], None],
    ) -> List["Channel"]:
        """
        Return a list of all relevant channels that the ClientIOHandler
        will need to register to in order to function
        """
        urls = self._get_socket_urls()
        return [
            WebsocketChannel(
                f"heroku_channel_{self.deploy_name}_{idx}",
                on_channel_open=on_channel_open,
                on_catastrophic_disconnect=on_catastrophic_disconnect,
                on_message=on_message,
                socket_url=url,
            )
            for idx, url in enumerate(urls)
        ]

    def download_file(self, target_filename: str, save_dir: str) -> None:
        """
        Heroku architects need to download the file
        """
        heroku_app_name = self.__get_app_name()
        target_url = (
            f"https://{heroku_app_name}.herokuapp.com/download_file/{target_filename}"
        )
        dest_path = os.path.join(save_dir, target_filename)
        r = requests.get(target_url, stream=True)

        with open(dest_path, "wb") as out_file:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)

    @classmethod
    def assert_task_args(cls, args: DictConfig, shared_state: "SharedTaskState"):
        """
        Assert that the provided arguments are valid. Should
        fail if a task launched with these arguments would
        not work.

        This should include throwing an exception if the architect
        needs login details or something similar given the
        arguments passed in.
        """
        heroku_executable_path = HerokuArchitect.get_heroku_client_path()
        try:
            output = subprocess.check_output(
                shlex.split(heroku_executable_path + " auth:whoami")
            )
        except subprocess.CalledProcessError:
            raise Exception(
                "A free Heroku account is required for launching tasks via "
                "the HerokuArchitect. Please register at "
                "https://signup.heroku.com/ and run `{} login -i` at the terminal "
                "to login to Heroku before trying to use HerokuArchitect."
                "".format(heroku_executable_path)
            )
        return

    @staticmethod
    def get_heroku_client_path() -> str:
        """
        Get the path to the heroku executable client, download a new one if it
        doesnt exist.
        """
        print("Locating heroku...")
        # Install Heroku CLI
        os_name = None
        bit_architecture = None

        # Get the platform we are working on
        if sys.platform == "darwin":  # Mac OS X
            os_name = "darwin"
        elif sys.platform.startswith("linux"):  # Linux
            os_name = "linux"
        else:
            os_name = "windows"

        # Find our architecture
        bit_architecture_info = platform.architecture()[0]
        if "64bit" in bit_architecture_info:
            bit_architecture = "x64"
        else:
            bit_architecture = "x86"

        # Find existing heroku files to use
        existing_heroku_directory_names = glob.glob(
            os.path.join(HEROKU_TMP_DIR, "heroku-cli-*")
        )
        if len(existing_heroku_directory_names) == 0:
            print("Getting heroku")
            if os.path.exists(os.path.join(HEROKU_TMP_DIR, "heroku.tar.gz")):
                os.remove(os.path.join(HEROKU_TMP_DIR, "heroku.tar.gz"))

            # Get the heroku client and unzip
            tar_path = os.path.join(HEROKU_TMP_DIR, "heroku.tar.gz")
            sh.wget(
                shlex.split(
                    "{}-{}-{}.tar.gz -O {}".format(
                        HEROKU_CLIENT_URL, os_name, bit_architecture, tar_path
                    )
                )
            )
            sh.tar(shlex.split(f"-xvzf {tar_path} -C {HEROKU_TMP_DIR}"))

            # Clean up the tar
            if os.path.exists(tar_path):
                os.remove(tar_path)

        heroku_directory_name = os.path.basename(
            glob.glob(os.path.join(HEROKU_TMP_DIR, "heroku-cli-*"))[0]
        )
        heroku_directory_path = os.path.join(HEROKU_TMP_DIR, heroku_directory_name)
        return os.path.join(heroku_directory_path, "bin", "heroku")

    @staticmethod
    def get_user_identifier() -> Tuple[str, str]:
        """
        Get heroku credentials for the current logged-in user
        """
        heroku_executable_path = HerokuArchitect.get_heroku_client_path()

        # get heroku credentials
        heroku_user_identifier = None
        while not heroku_user_identifier:
            try:
                output = subprocess.check_output(
                    shlex.split(heroku_executable_path + " auth:whoami")
                )
                output = subprocess.check_output(
                    shlex.split(heroku_executable_path + " auth:token")
                )
                heroku_user_identifier = netrc.netrc(
                    os.path.join(os.path.expanduser("~"), ".netrc")
                ).hosts["api.heroku.com"][0]
            except subprocess.CalledProcessError:
                print(
                    "A free Heroku account is required for launching Public tasks. "
                    "Please register at https://signup.heroku.com/ and run `{} "
                    "login -i` at the terminal to login to Heroku, and then run this "
                    "program again.".format(heroku_executable_path)
                )
                raise Exception("Please login to heroku before trying again.")
        return heroku_executable_path, heroku_user_identifier

    def __get_heroku_client(self) -> Tuple[str, str]:
        """
        Get an authorized heroku client path and authorization token
        """
        if (
            self.__heroku_executable_path is None
            or self.__heroku_user_identifier is None
        ):
            (
                heroku_executable_path,
                heroku_user_identifier,
            ) = HerokuArchitect.get_user_identifier()
            self.__heroku_executable_path = heroku_executable_path
            self.__heroku_user_identifier = heroku_user_identifier
        return self.__heroku_executable_path, self.__heroku_user_identifier

    def __get_build_directory(self) -> str:
        """
        Return the string where the server should be built in.
        """
        return os.path.join(
            self.build_dir,
            "{}_{}".format(HEROKU_SERVER_BUILD_DIRECTORY, self.deploy_name),
        )

    def __get_app_name(self) -> str:
        """
        Get the name of the heroku app associated with this task
        """
        if self.__heroku_app_name is None:
            _, heroku_user_identifier = self.__get_heroku_client()
            heroku_app_name = (
                "{}-{}-{}".format(
                    USER_NAME,
                    self.deploy_name,
                    hashlib.md5(heroku_user_identifier.encode("utf-8")).hexdigest(),
                )
            )[:30]
            heroku_app_name = heroku_app_name.replace("_", "-")
            while heroku_app_name[-1] == "-":
                heroku_app_name = heroku_app_name[:-1]
            self.__heroku_app_name = re.sub(r"[^a-zA-Z0-9-]", "", heroku_app_name)
        return self.__heroku_app_name

    def __compile_server(self) -> str:
        """
        Move the required task files to a specific directory to be deployed to
        heroku directly. Return the location that the packaged files are
        now prepared in.
        """
        print("Building server files...")
        heroku_server_development_root = self.__get_build_directory()
        os.makedirs(heroku_server_development_root)
        heroku_server_development_path = self.server_dir = build_router(
            heroku_server_development_root,
            self.task_run,
            version=self.server_type,
            server_source_path=self.server_source_path,
        )
        return heroku_server_development_path

    def __setup_heroku_server(self) -> str:
        """
        Deploy the server using the setup server directory, return the URL
        """

        heroku_executable_path, heroku_user_identifier = self.__get_heroku_client()
        server_dir = self.__get_build_directory()

        print("Heroku: Starting server...")
        branch = "main"
        heroku_server_directory_path = os.path.join(server_dir, "router")
        sh.git(shlex.split(f"-C {heroku_server_directory_path} init -b {branch}"))

        heroku_app_name = self.__get_app_name()

        # Create or attach to the server
        return_dir = os.getcwd()
        os.chdir(heroku_server_directory_path)
        try:
            if self.args.architect.get("heroku_team", None) is not None:
                subprocess.check_output(
                    shlex.split(
                        "{} create {} --team {}".format(
                            heroku_executable_path,
                            heroku_app_name,
                            self.args.architect.heroku_team,
                        )
                    )
                )
            else:
                subprocess.check_output(
                    shlex.split(
                        "{} create {}".format(heroku_executable_path, heroku_app_name)
                    )
                )
                self.created = True
        except subprocess.CalledProcessError as e:  # User has too many apps?
            logger.exception(e, exc_info=True)
            sh.rm(shlex.split("-rf {}".format(heroku_server_directory_path)))
            raise Exception(
                "An exception has occurred when launching your heroku app. This "
                "can commonly occur when you have hit your limit on concurrent "
                "apps in heroku, especially if you are running multiple tasks "
                "at once. It also may occur if the app-name generated for your "
                "task is using illegal characters for heroku. Check the logs "
                "above for confirmation.\n"
                "If the issue is indeed the concurrent server cap, Please wait for"
                " some of your existing tasks to complete. If you have no tasks "
                "running, login to heroku and delete some of the running apps or "
                "verify your account to allow more concurrent apps"
            )

        # Enable WebSockets
        try:
            subprocess.check_output(
                shlex.split(
                    "{} features:enable http-session-affinity".format(
                        heroku_executable_path
                    )
                )
            )
        except subprocess.CalledProcessError:  # Already enabled WebSockets
            pass
        os.chdir(return_dir)

        # push config args, as desired
        if len(self.heroku_config_args) > 0:
            config_strs = [
                f"{config_key}={config_val}"
                for config_key, config_val in self.heroku_config_args.items()
            ]
            full_config_str = " ".join(config_strs)
            subprocess.check_output(
                shlex.split(
                    f"{heroku_executable_path} config:set -a {heroku_app_name} {full_config_str}"
                )
            )

        # commit and push to the heroku server
        sh.git(shlex.split(f"-C {heroku_server_directory_path} add -A"))
        sh.git(shlex.split(f'-C {heroku_server_directory_path} commit -m "app"'))
        sh.git(
            shlex.split(f"-C {heroku_server_directory_path} push -f heroku {branch}")
        )

        os.chdir(heroku_server_directory_path)
        subprocess.check_output(
            shlex.split("{} ps:scale web=1".format(heroku_executable_path))
        )

        if self.args.architect.use_hobby is True:
            try:
                subprocess.check_output(
                    shlex.split("{} dyno:type Hobby".format(heroku_executable_path))
                )
            except subprocess.CalledProcessError:  # User doesn't have hobby access
                self.__delete_heroku_server()
                sh.rm(shlex.split("-rf {}".format(heroku_server_directory_path)))
                raise Exception(
                    "Server launched with hobby flag but account cannot create "
                    "hobby servers."
                )
        os.chdir(return_dir)

        time.sleep(HEROKU_WAIT_TIME)

        return "https://{}.herokuapp.com".format(heroku_app_name)

    def __delete_heroku_server(self):
        """
        Remove the heroku server associated with this task run
        """
        heroku_executable_path, heroku_user_identifier = self.__get_heroku_client()
        heroku_app_name = self.__get_app_name()
        print("Heroku: Deleting server: {}".format(heroku_app_name))
        subprocess.check_output(
            shlex.split(
                "{} destroy {} --confirm {}".format(
                    heroku_executable_path, heroku_app_name, heroku_app_name
                )
            )
        )
        time.sleep(HEROKU_WAIT_TIME)

    def server_is_running(self) -> bool:
        """
        Utility function to check if the given heroku app (by app-name) is
        still running
        """
        heroku_executable_path, _token = self.__get_heroku_client()
        app_name = self.__get_app_name()
        output = subprocess.check_output(shlex.split(heroku_executable_path + " apps"))
        all_apps = str(output, "utf-8")
        return app_name in all_apps

    def build_is_clean(self) -> bool:
        """
        Utility function to see if the build has been cleaned up
        """
        server_dir = self.__get_build_directory()
        return not os.path.exists(server_dir)

    def prepare(self) -> str:
        """
        Produce the server files that will be deployed to the server
        """
        return self.__compile_server()

    def deploy(self) -> str:
        """
        Launch the server, and push the task files to the server. Return
        the server URL
        """
        return self.__setup_heroku_server()

    def cleanup(self) -> None:
        """
        Remove any files that were used for the deployment process that
        no longer need to be kept track of now that the task has
        been launched.
        """
        server_dir = self.__get_build_directory()
        sh.rm(shlex.split("-rf {}".format(server_dir)))

    def shutdown(self) -> None:
        """
        Shut down the server launched by this Architect, as stored
        in the db.
        """
        if self.created:  # only delete the server if it's created by us
            self.__delete_heroku_server()
