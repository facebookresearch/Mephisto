#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sh  # type: ignore
import shutil
import time
import requests
import re
import json
import boto3  # type: ignore
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig  # type: ignore
from mephisto.abstractions.architect import Architect, ArchitectArgs
from mephisto.abstractions.architects.router.build_router import build_router
from mephisto.abstractions.architects.channels.websocket_channel import WebsocketChannel
from mephisto.operations.registry import register_mephisto_abstraction
from typing import List, Dict, Optional, TYPE_CHECKING, Callable

import mephisto.abstractions.architects.ec2.ec2_helpers as ec2_helpers
from mephisto.abstractions.architects.ec2.ec2_helpers import (
    DEFAULT_FALLBACK_FILE,
    DEFAULT_SERVER_DETAIL_LOCATION,
    SCRIPTS_DIRECTORY,
)

if TYPE_CHECKING:
    from mephisto.abstractions._subcomponents.channel import Channel
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.blueprint import SharedTaskState

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)

ARCHITECT_TYPE = "ec2"
FINAL_SERVER_BUILD_DIRECTORY = "routing_server"
DEPLOY_WAIT_TIME = 3


def url_safe_string(in_string: str) -> str:
    """
    Produces a domain string that is safe for use
    in ec2 resources
    """
    hyphenated = in_string.replace("_", "-")
    return re.sub("[^0-9a-zA-Z-]+", "", hyphenated)


@dataclass
class EC2ArchitectArgs(ArchitectArgs):
    """Additional arguments for configuring a heroku architect"""

    _architect_type: str = ARCHITECT_TYPE
    instance_type: str = field(
        default="t2.micro", metadata={"help": "Instance type to run router"}
    )
    subdomain: str = field(
        default="${mephisto.task.task_name}",
        metadata={"help": "Subdomain name for routing"},
    )
    profile_name: str = field(
        default=MISSING, metadata={"help": "Profile name for deploying an ec2 instance"}
    )


@register_mephisto_abstraction()
class EC2Architect(Architect):
    """
    Sets up a server on heroku and deploys the task on that server
    """

    ArgsClass = EC2ArchitectArgs
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
        Create an architect with all required parameters for launch loaded
        """
        self.args = args
        self.task_run = task_run
        with open(DEFAULT_FALLBACK_FILE, "r") as fallback_detail_file:
            self.fallback_details = json.load(fallback_detail_file)

        self.subdomain = url_safe_string(args.architect.subdomain)
        self.root_domain = self.fallback_details["domain"]
        self.router_name = f"{self.subdomain}-routing-server"
        self.full_domain = f"{self.subdomain}.{self.root_domain}"
        self.server_source_path = args.architect.get("server_source_path", None)
        self.instance_type = args.architect.instance_type
        self.profile_name = args.architect.profile_name
        self.server_type: str = args.architect.server_type
        self.build_dir = build_dir_root
        self.server_detail_path = self._get_detail_path(self.subdomain)

        self.session = boto3.Session(
            profile_name=self.profile_name, region_name="us-east-2"
        )

        self.server_dir: Optional[str] = None
        self.server_id: Optional[str] = None
        self.target_group_arn: Optional[str] = None
        self.router_rule_arn: Optional[str] = None
        self.created = False

    @classmethod
    def _get_detail_path(cls, subdomain):
        """Return the location where a detail file will be stored for the given domain"""
        return os.path.join(DEFAULT_SERVER_DETAIL_LOCATION, f"{subdomain}.json")

    def _get_socket_urls(self) -> List[str]:
        """Returns the path to the heroku app socket"""
        return [f"wss://{self.full_domain}/"]

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
                f"ec2_channel_{self.subdomain}_{idx}",
                on_channel_open=on_channel_open,
                on_catastrophic_disconnect=on_catastrophic_disconnect,
                on_message=on_message,
                socket_url=url,
            )
            for idx, url in enumerate(urls)
        ]

    def download_file(self, target_filename: str, save_dir: str) -> None:
        """
        Download the file from local storage
        """
        target_url = f"https://{self.full_domain}/download_file/{target_filename}"
        dest_path = os.path.join(save_dir, target_filename)
        r = requests.get(target_url, stream=True)

        with open(dest_path, "wb") as out_file:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)

    @classmethod
    def check_domain_unused_locally(self, subdomain: str):
        """
        Checks to see if we have an active local record for the given subdomain
        """
        return not os.path.exists(self._get_detail_path(subdomain))

    @classmethod
    def assert_task_args(cls, args: DictConfig, shared_state: "SharedTaskState"):
        """
        Assert that the given profile is already ready, that a fallback exists
        and that all the configuration is ready
        """
        profile_name = args.architect.profile_name
        assert ec2_helpers.check_aws_credentials(
            profile_name
        ), "Given profile doesn't have registered credentials"
        #   Producing a domain string that is safe for use
        #   in ec2 resources
        subdomain = url_safe_string(args.architect.subdomain)

        assert cls.check_domain_unused_locally(
            subdomain=subdomain
        ), "Given subdomain does exist"

        # VALID_INSTANCES = []
        # assert args.architect.instance_type in VALID_INSTANCES

        assert os.path.exists(
            DEFAULT_FALLBACK_FILE
        ), "Must have fallback launched to use EC2 architect"

        with open(DEFAULT_FALLBACK_FILE, "r") as fallback_detail_file:
            fallback_details = json.load(fallback_detail_file)

        REQUIRED_KEYS = [
            "key_pair_name",
            "security_group_id",
            "vpc_details",
            "listener_arn",
        ]
        for key in REQUIRED_KEYS:
            assert key in fallback_details, f"Fallback file missing required key {key}"

        session = boto3.Session(profile_name=profile_name, region_name="us-east-2")
        assert ec2_helpers.rule_is_new(
            session, subdomain, fallback_details["listener_arn"]
        ), "Rule was not new, existing subdomain found registered to the listener. Check on AWS."

    def __get_build_directory(self) -> str:
        """
        Return the string where the server should be built in.
        """
        return os.path.join(
            self.build_dir,
            FINAL_SERVER_BUILD_DIRECTORY,
        )

    def __compile_server(self) -> str:
        """
        Move the required task files to a specific directory to be deployed to
        ec2 directly. Return the location that the packaged files are
        now prepared in.
        """
        print("Building server files...")
        server_build_root = self.__get_build_directory()
        os.makedirs(server_build_root)
        self.server_dir = server_dir = build_router(
            server_build_root,
            self.task_run,
            version=self.server_type,
            server_source_path=self.server_source_path,
        )
        setup_path = os.path.join(SCRIPTS_DIRECTORY, self.server_type)
        setup_dest = os.path.join(server_build_root, "setup")
        shutil.copytree(setup_path, setup_dest)
        possible_node_modules = os.path.join(
            server_build_root, "router", "node_modules"
        )
        if os.path.exists(possible_node_modules):
            shutil.rmtree(possible_node_modules)
        return server_dir

    def __setup_ec2_server(self) -> str:
        """
        Deploy the server using the setup server directory, return the URL
        """
        server_dir = os.path.abspath(self.__get_build_directory())

        print("EC2: Starting instance...")

        # Launch server
        server_id = ec2_helpers.create_instance(
            self.session,
            self.fallback_details["key_pair_name"],
            self.fallback_details["security_group_id"],
            self.fallback_details["vpc_details"]["subnet_1_id"],
            self.router_name,
            instance_type=self.instance_type,
        )
        self.server_id = server_id

        self.created = True

        print("EC2: Configuring routing table...")
        # Configure router
        (
            self.target_group_arn,
            self.router_rule_arn,
        ) = ec2_helpers.register_instance_to_listener(
            self.session,
            server_id,
            self.fallback_details["vpc_details"]["vpc_id"],
            self.fallback_details["listener_arn"],
            self.full_domain,
        )

        # Write out details
        server_details = {
            "balancer_rule_arn": self.router_rule_arn,
            "instance_id": self.server_id,
            "subdomain": self.subdomain,
            "target_group_arn": self.target_group_arn,
        }

        with open(self.server_detail_path, "w+") as detail_file:
            json.dump(server_details, detail_file)

        print("EC2: Deploying server...")
        # Push server files and execute launch
        ec2_helpers.deploy_to_routing_server(
            self.session,
            server_id,
            self.fallback_details["key_pair_name"],
            server_dir,
        )

        return f"https://{self.full_domain}"

    def __delete_ec2_server(self):
        """
        Remove the heroku server associated with this task run
        """
        server_id = self.server_id
        assert server_id is not None, "Cannot shutdown a non-existent server"
        print(f"Ec2: Deleting server: {self.server_id}")
        if self.router_rule_arn is not None:
            ec2_helpers.delete_rule(
                self.session,
                self.router_rule_arn,
                self.target_group_arn,
            )

        ec2_helpers.delete_instance(
            self.session,
            server_id,
        )
        os.unlink(self.server_detail_path)

    def server_is_running(self) -> bool:
        """
        Utility function to check if the given heroku app (by app-name) is
        still running
        """
        return os.path.exists(self.server_detail_path)

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
        return self.__setup_ec2_server()

    def cleanup(self) -> None:
        """
        Remove any files that were used for the deployment process that
        no longer need to be kept track of now that the task has
        been launched.
        """
        server_dir = self.__get_build_directory()
        shutil.rmtree(server_dir)

    def shutdown(self) -> None:
        """
        Shut down the server launched by this Architect, as stored
        in the db.
        """
        if self.created:  # only delete the server if it's created by us
            self.__delete_ec2_server()
