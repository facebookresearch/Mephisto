#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mephisto.abstractions.architects.ec2.ec2_helpers as ec2_helpers
from mephisto.abstractions.architects.ec2.ec2_helpers import (
    DEFAULT_FALLBACK_FILE,
    FALLBACK_INSTANCE_TYPE,
)
import boto3  # type: ignore
import os
import json

from typing import Dict, Any

DEFAULT_KEY_PAIR_NAME = "mephisto-server-key"


def update_details(
    open_file,
    new_data: Dict[str, Any],
):
    """
    Overwrite the contents of the open file with the given data.
    """
    open_file.seek(0)
    open_file.truncate(0)
    json.dump(new_data, open_file, sort_keys=True, indent=4)


def launch_ec2_fallback(
    iam_profile: str,  # Iam role name, should be saved in aws credentials
    domain_name: str,
    ssh_ip_block: str,
    access_logs_key: str,
    key_pair_name: str = DEFAULT_KEY_PAIR_NAME,
    server_details_file: str = DEFAULT_FALLBACK_FILE,
    instance_type: str = FALLBACK_INSTANCE_TYPE,
) -> Dict[str, Any]:
    """
    This function is used to set up a mephisto
    vpc and fallback server for the AWS setup. At the moment
    it requires that you already have a domain registered,
    and it is up to you to delegate the domain to the
    amazon nameservers created by this function. This
    function will request the ssl certificate from amazon

    At the moment, it only works on the us-east region.
    Feel free to open a PR to extend this functionality
    if you need another region!
    """
    assert not domain_name.startswith("www."), (
        "You should provide a domain name without www, like 'example.com', "
        "or 'crowdsourcing.example.com'"
    )
    key_pair_name = DEFAULT_KEY_PAIR_NAME if key_pair_name is None else key_pair_name
    server_details_file = (
        DEFAULT_FALLBACK_FILE if server_details_file is None else server_details_file
    )
    instance_type = FALLBACK_INSTANCE_TYPE if instance_type is None else instance_type

    session = boto3.Session(profile_name=iam_profile, region_name="us-east-2")

    try:
        with open(server_details_file, "r") as saved_details_file:
            existing_details = json.load(saved_details_file)
    except:
        existing_details = {"domain": domain_name, "cidr": ssh_ip_block}

    with open(server_details_file, "w+") as saved_details_file:
        # Get a ssl certificate for the domain
        cert_details = existing_details.get("cert_details")
        if cert_details is None:
            print("Getting a certificate for the given domain...")
            cert_details = ec2_helpers.get_certificate(session, domain_name)
            existing_details["cert_details"] = cert_details
            update_details(saved_details_file, existing_details)
        else:
            print("Using existing certificate")

        # Create a hosted zone for the given domain
        hosted_zone_id = existing_details.get("hosted_zone_id")
        if hosted_zone_id is None:
            print("Creating hosted zone for the given domain...")
            hosted_zone_id = ec2_helpers.create_hosted_zone(session, domain_name)
            existing_details["hosted_zone_id"] = hosted_zone_id
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing hosted zone {hosted_zone_id}")

        # Create the VPC to hold the servers
        vpc_details = existing_details.get("vpc_details")
        if vpc_details is None:
            print("Initializing VPC...")
            vpc_details = ec2_helpers.create_mephisto_vpc(session)
            existing_details["vpc_details"] = vpc_details
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing vpc {vpc_details['vpc_id']}")

        # Set up a security group for everything
        security_group_id = existing_details.get("security_group_id")
        if security_group_id is None:
            print("Creating security group...")
            security_group_id = ec2_helpers.create_security_group(
                session, vpc_details["vpc_id"], ssh_ip_block
            )
            existing_details["security_group_id"] = security_group_id
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing security group {security_group_id}")

        # Create a keypair for the server
        key_pair_filename = existing_details.get("key_pair_filename")
        if key_pair_filename is None:
            print(f"Generating keypair named {key_pair_name}")
            key_pair_filename = ec2_helpers.create_key_pair(session, key_pair_name)
            existing_details["key_pair_filename"] = key_pair_filename
            existing_details["key_pair_name"] = key_pair_name
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing keypair at {key_pair_filename}")

        # Create the instance running the fallback server
        instance_id = existing_details.get("instance_id")
        if instance_id is None:
            print("Creating a new instance for fallback server...")
            instance_id = ec2_helpers.create_instance(
                session,
                key_pair_name,
                security_group_id,
                vpc_details["subnet_1_id"],
                "mephisto-default-fallover",
                instance_type=instance_type,
            )
            existing_details["instance_id"] = instance_id
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing instance {instance_id}")

        # Create load balancer
        balancer_arn = existing_details.get("balancer_arn")
        if balancer_arn is None:
            print("Creating load balancer...")
            balancer_arn = ec2_helpers.create_load_balancer(
                session,
                [vpc_details["subnet_1_id"], vpc_details["subnet_2_id"]],
                security_group_id,
                vpc_details["vpc_id"],
            )

            print("Registering to hosted zone")
            ec2_helpers.register_zone_records(
                session,
                existing_details["hosted_zone_id"],
                domain_name,
                balancer_arn,
                cert_details["Name"],
                cert_details["Value"],
            )

            existing_details["balancer_arn"] = balancer_arn
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing balancer {balancer_arn}")

        # Create the target group for the fallback instance
        target_group_arn = existing_details.get("target_group_arn")
        if target_group_arn is None:
            print("Creating target group...")
            target_group_arn = ec2_helpers.create_target_group(
                session, vpc_details["vpc_id"], instance_id
            )
            existing_details["target_group_arn"] = target_group_arn
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing target group {target_group_arn}")

        # Create listener in balancer to direct to target group
        listener_arn = existing_details.get("listener_arn")
        if listener_arn is None:
            print("Creating listener for load balancer...")
            listener_arn = ec2_helpers.configure_base_balancer(
                session,
                balancer_arn,
                cert_details["arn"],
                target_group_arn,
            )
            existing_details["listener_arn"] = listener_arn
            update_details(saved_details_file, existing_details)
        else:
            print(f"Using existing listener {listener_arn}")

        # Finally, deploy the fallback server contents:
        ec2_helpers.deploy_fallback_server(
            session, instance_id, key_pair_name, access_logs_key
        )
        existing_details["access_logs_key"] = access_logs_key
        update_details(saved_details_file, existing_details)

    return existing_details


# TODO(CLEAN) Hydrize
def main():
    iam_role_name = input("Please enter local profile name for IAM role\n>> ")
    ec2_helpers.setup_ec2_credentials(iam_role_name)

    domain_name = input("Please provide the domain name you will be using\n>> ")
    ssh_ip_block = input("Provide the CIDR IP block for ssh access\n>> ")
    access_logs_key = input(
        "Please provide a key password to use for accessing server logs\n>> "
    )
    launch_ec2_fallback(iam_role_name, domain_name, ssh_ip_block, access_logs_key)


if __name__ == "__main__":
    main()
