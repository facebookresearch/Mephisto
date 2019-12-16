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
import sh
import shlex
import shutil
import subprocess
import time
from mephisto.core.utils import get_mephisto_tmp_dir
from mephisto.data_model.architect import Architect
from mephisto.server.architects.router.build_router import build_router
from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB


USER_NAME = getpass.getuser()
HEROKU_SERVER_BUILD_DIRECTORY = "heroku_server"
HEROKU_CLIENT_URL = (
    "https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli"
)

HEROKU_WAIT_TIME = 3

class HerokuArchitect(Architect):
    """
    Sets up a server on heroku and deploys the task on that server
    """

    def __init__(
        self,
        db: "MephistoDB",
        opts: Dict[str, str],
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
        # TODO put the expected info into the MephistoDB rather than storing here?
        # Servers will have a status which needs to be kept track of.
        self.opts = opts
        self.task_run = task_run
        self.deploy_name = f"{task_run.get_task().task_name}_{task_run.db_id}"
        self.build_dir = build_dir_root
        self.tmp_dir = os.path.join(get_mephisto_tmp_dir(), 'heroku')
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        # Cache-able parameters
        self.__heroku_app_name: Optional[str] = None
        self.__heroku_executable_path: Optional[str] = None
        self.__heroku_user_identifier: Optional[str] = None

    def get_socket_urls(self) -> List[str]:
        """Return the path to the local server socket"""
        assert self.hostname is not None, "No hostname for socket"
        assert self.port is not None, "No ports for socket"
        if 'https://' in self.hostname:
            basename = self.hostname.split('https://')[1]
            protocol = "wss"
        elif 'http://' in self.hostname:
            basename = self.hostname.split('http://')[1]
            protocol = "ws"
        else:
            basename = self.hostname
            protocol = "ws"

        if basename in ['localhost', '127.0.0.1']:
            protocol = "ws"
        heroku_app_name = self.__get_app_name()
        return ["wss://{}.herokuapp.com/".format(heroku_app_name)]

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """
        Defines options that are potentially usable for this server location
        """
        # TODO update to a format that will be rendererable on the frontend.
        # TODO maybe use arg-parser somehow?
        return {
            "use_hobby": "Launch on the hobby tier?",
            "heroku_team": "Heroku team to use",
        }

    def __get_heroku_client(self) -> Tuple[str, str]:
        """
        Find the heroku executable client, download a new one if it
        doesnt exist. Ensure that the user is authorized.

        Return the executable path and authorization token
        """
        if (
            self.__heroku_executable_path is None
            or self.__heroku_user_identifier is None
        ):
            print("Locating heroku...")
            # Install Heroku CLI
            os_name = None
            bit_architecture = None

            # Get the platform we are working on
            platform_info = platform.platform()
            if "Darwin" in platform_info:  # Mac OS X
                os_name = "darwin"
            elif "Linux" in platform_info:  # Linux
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
                os.path.join(self.tmp_dir, "heroku-cli-*")
            )
            if len(existing_heroku_directory_names) == 0:
                print("Getting heroku")
                if os.path.exists(os.path.join(self.tmp_dir, "heroku.tar.gz")):
                    os.remove(os.path.join(self.tmp_dir, "heroku.tar.gz"))

                # Get the heroku client and unzip
                tar_path = os.path.join(self.tmp_dir, 'heroku.tar.gz')
                sh.wget(
                    shlex.split(
                        "{}-{}-{}.tar.gz -O {}".format(
                            HEROKU_CLIENT_URL, os_name, bit_architecture, tar_path
                        )
                    )
                )
                sh.tar(shlex.split(f"-xvzf {tar_path} -C {self.tmp_dir}"))

                # Clean up the tar
                if os.path.exists(tar_path):
                    os.remove(tar_path)

            heroku_directory_name = glob.glob(
                os.path.join(self.tmp_dir, "heroku-cli-*")
            )[0]
            heroku_directory_path = os.path.join(self.tmp_dir, heroku_directory_name)
            heroku_executable_path = os.path.join(
                heroku_directory_path, "bin", "heroku"
            )

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
                        "A free Heroku account is required for launching MTurk tasks. "
                        "Please register at https://signup.heroku.com/ and run `{} "
                        "login` at the terminal to login to Heroku, and then run this "
                        "program again.".format(heroku_executable_path)
                    )
                    raise SystemExit(
                        "Please login to heroku before trying again."
                    )
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
            heroku_app_name = heroku_app_name.replace("_", '-')
            while heroku_app_name[-1] == "-":
                heroku_app_name = heroku_app_name[:-1]
            self.heroku_app_name = heroku_app_name.replace("_", '-')
        return self.heroku_app_name

    def __compile_server(self) -> str:
        """
        Move the required task files to a specific directory to be deployed to
        heroku directly. Return the location that the packaged files are
        now prepared in.
        """
        print("Building server files...")
        heroku_server_development_root = self.__get_build_directory()
        os.makedirs(heroku_server_development_root)
        heroku_server_development_path = build_router(heroku_server_development_root, self.task_run)
        return heroku_server_development_path

    def __setup_heroku_server(self) -> str:
        """
        Deploy the server using the setup server directory, return the URL
        """

        heroku_executable_path, heroku_user_identifier = self.__get_heroku_client()
        server_dir = self.__get_build_directory()

        print("Heroku: Starting server...")

        heroku_server_directory_path = os.path.join(server_dir, "router")
        sh.git(shlex.split(f"-C {heroku_server_directory_path} init"))

        heroku_app_name = self.__get_app_name()

        # Create or attach to the server
        return_dir = os.getcwd()
        os.chdir(heroku_server_directory_path)
        try:
            if self.opts.get("heroku_team") is not None:
                subprocess.check_output(
                    shlex.split(
                        "{} create {} --team {}".format(
                            heroku_executable_path,
                            heroku_app_name,
                            self.opts.get("heroku_team"),
                        )
                    )
                )
            else:
                subprocess.check_output(
                    shlex.split(
                        "{} create {}".format(heroku_executable_path, heroku_app_name)
                    )
                )
        except subprocess.CalledProcessError as e:  # User has too many apps?
            # TODO check response codes to determine what actually happened
            print(e)
            sh.rm(shlex.split("-rf {}".format(heroku_server_directory_path)))
            raise SystemExit(
                "You have hit your limit on concurrent apps with heroku, which are"
                " required to run multiple concurrent tasks.\nPlease wait for some"
                " of your existing tasks to complete. If you have no tasks "
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

        # commit and push to the heroku server
        sh.git(shlex.split(f"-C {heroku_server_directory_path} add -A"))
        sh.git(shlex.split(f'-C {heroku_server_directory_path} commit -m "app"'))
        sh.git(shlex.split(f"-C {heroku_server_directory_path} push -f heroku master"))

        os.chdir(heroku_server_directory_path)
        subprocess.check_output(
            shlex.split("{} ps:scale web=1".format(heroku_executable_path))
        )

        if self.opts.get("use_hobby") is True:
            try:
                subprocess.check_output(
                    shlex.split("{} dyno:type Hobby".format(heroku_executable_path))
                )
            except subprocess.CalledProcessError:  # User doesn't have hobby access
                self.__delete_heroku_server()
                sh.rm(shlex.split("-rf {}".format(heroku_server_directory_path)))
                raise SystemExit(
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
        output = subprocess.check_output(
            shlex.split(heroku_executable_path + " apps")
        )
        all_apps = str(output, 'utf-8')
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
        self.__delete_heroku_server()
