#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict, Optional, Tuple, List, Any, TYPE_CHECKING
import boto3  # type: ignore
import botocore.exceptions  # type: ignore
import time
import os
import subprocess
import json
import getpass
import hashlib
from mephisto.abstractions.providers.mturk.mturk_utils import setup_aws_credentials
from mephisto.abstractions.architects.router import build_router

from botocore import client  # type: ignore
from botocore.exceptions import ClientError, ProfileNotFound  # type: ignore
from botocore.config import Config  # type: ignore
from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


if TYPE_CHECKING:
    from omegaconf import DictConfig  # type: ignore

botoconfig = Config(
    region_name="us-east-2", retries={"max_attempts": 10, "mode": "standard"}
)

DEFAULT_AMI_ID = "ami-0f19d220602031aed"
AMI_DEFAULT_USER = "ec2-user"
DEFAULT_INSTANCE_TYPE = "m2.micro"
FALLBACK_INSTANCE_TYPE = "t2.nano"
MY_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_KEY_PAIR_DIRECTORY = os.path.join(MY_DIR, "keypairs")
DEFAULT_SERVER_DETAIL_LOCATION = os.path.join(MY_DIR, "servers")
SCRIPTS_DIRECTORY = os.path.join(MY_DIR, "run_scripts")
DEFAULT_FALLBACK_FILE = os.path.join(DEFAULT_SERVER_DETAIL_LOCATION, "fallback.json")
FALLBACK_SERVER_LOC = os.path.join(MY_DIR, "fallback_server")
KNOWN_HOST_PATH = os.path.expanduser("~/.ssh/known_hosts")
MAX_RETRIES = 10


def get_owner_tag() -> Dict[str, str]:
    """
    Creates a tag with the user's username
    as the owner for the given resource
    """
    return {"Key": "Owner", "Value": getpass.getuser()}


def check_aws_credentials(profile_name: str) -> bool:
    try:
        # Check existing credentials
        boto3.Session(profile_name=profile_name)
        return True
    except ProfileNotFound:
        return False


def setup_ec2_credentials(
    profile_name: str, register_args: Optional["DictConfig"] = None
) -> bool:
    return setup_aws_credentials(profile_name, register_args)


def get_domain_if_available(session: boto3.Session, domain_name: str) -> bool:
    """
    Attempt to register the given domain with Route53, return
    True if registration is successful, False otherwise.

    Details on valid domains can be found here:
    https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/registrar-tld-list.html

    Pricing is available on amazon
    """
    client = session.client("route53domains")
    avail_result = "PENDING"

    while avail_result == "PENDING":
        avail = client.check_domain_availabiliity(DomainName=domain_name)
        avail_result = avail["Availability"]
        time.sleep(0.3)

    # May extend to handle other available cases
    if avail_result not in ["AVAILABLE"]:
        print(
            f"Domain was not listed as available, instead "
            f"{avail_result}, visit route53 for more detail"
        )
        return False

    print("Automated domain registration isn't yet implemented")
    # Registration can be completed using client.register_domain
    # Details are available here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53domains.html#Route53Domains.Client.register_domain

    return False


def find_hosted_zone(session: boto3.Session, domain_name: str) -> Optional[str]:
    """
    search for a hosted zone with the given name, return its id
    if found and None otherwise
    """
    client = session.client("route53")

    zones = client.list_hosted_zones_by_name()

    logger.debug(f"Found zones {zones}")
    for zone in zones["HostedZones"]:
        if zone["Name"] == f"{domain_name}.":
            return zone["Id"]

    return None


def create_hosted_zone(session: boto3.Session, domain_name: str) -> str:
    """
    Given a domain name, tries to create a hosted zone
    for that domain. Returns the hosted zone id
    """
    client = session.client("route53")

    zone_id = find_hosted_zone(session, domain_name)
    if zone_id is None:

        res = client.create_hosted_zone(
            Name=domain_name,
            CallerReference=str(time.time()),
            HostedZoneConfig={
                "Comment": "Mephisto hosted zone",
            },
        )
        nameservers = res["DelegationSet"]["NameServers"]
        BOLD_WHITE_ON_BLUE = "\x1b[1;37;44m"
        RESET = "\x1b[0m"
        print(
            f"{BOLD_WHITE_ON_BLUE}"
            "Registered new hosted zone! You should ensure your domain "
            "name is registered to delegate to the following nameservers: "
            f"\n{nameservers}"
            f"{RESET}"
        )
        zone_id = res["HostedZone"]["Id"]
    else:
        logger.debug(f"This hosted zone already exists! Returning {zone_id}")

    return zone_id


def find_certificate_arn(session: boto3.Session, domain_name: str) -> Optional[str]:
    """
    Finds the certificate for the given domain if it exists, and returns
    the certification arn.
    """
    client = session.client("acm")
    certs = client.list_certificates()
    logger.debug(f"Found existing certs: {certs}")
    for cert in certs["CertificateSummaryList"]:
        if cert["DomainName"] == domain_name:
            return cert["CertificateArn"]
    return None


def get_certificate(session: boto3.Session, domain_name: str) -> Dict[str, str]:
    """
    Gets the certificate for the given domain name, and returns
    the dns validation name and target and cert arn ('Name' and 'Value', 'arn')
    """
    client = session.client("acm")
    cert_domain_name = f"*.{domain_name}"
    certificate_arn = find_certificate_arn(session, cert_domain_name)
    if certificate_arn is None:  # cert not yet issued
        logger.debug("Requesting new certificate")
        response = client.request_certificate(
            DomainName=cert_domain_name,
            ValidationMethod="DNS",
            IdempotencyToken=f"{domain_name.split('.')[0]}request",
            Options={
                "CertificateTransparencyLoggingPreference": "ENABLED",
            },
        )
        certificate_arn = response["CertificateArn"]
    else:
        logger.debug(f"Using existing certificate {certificate_arn}")
    attempts = 0
    sleep_time = 2
    details = None
    while attempts < MAX_RETRIES:
        try:
            details = client.describe_certificate(
                CertificateArn=certificate_arn,
            )
            return_data = details["Certificate"]["DomainValidationOptions"][0][
                "ResourceRecord"
            ]
            return_data["arn"] = certificate_arn
            return return_data
        except KeyError:
            # Resource record not created yet, try again
            attempts += 1
            logger.info(f"Attempt {attempts} had no certification details, retrying")
            time.sleep(sleep_time)
            sleep_time *= 2
    raise Exception("Exceeded MAX_RETRIES waiting for certificate records")


def register_zone_records(
    session: boto3.Session,
    zone_id: str,
    domain_name: str,
    load_balancer_arn: str,
    acm_valid_name: str,
    acm_valid_target: str,
) -> int:
    """
    Creates the required zone records for this mephisto hosted zone. Requires
    the load balancer target, and the ACM certificate addresses

    Returns the change id
    """
    # Get details about the load balancer
    ec2_client = session.client("elbv2")
    balancer = ec2_client.describe_load_balancers(
        LoadBalancerArns=[load_balancer_arn],
    )["LoadBalancers"][0]
    load_balancer_dns = balancer["DNSName"]
    load_balancer_zone = balancer["CanonicalHostedZoneId"]

    # Create the records
    client = session.client("route53")
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            "Comment": "Creating records for Mephisto load balancer and DNS validations for certs",
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": f"*.{domain_name}",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": load_balancer_zone,
                            "DNSName": load_balancer_dns,
                            "EvaluateTargetHealth": True,
                        },
                    },
                },
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": f"{domain_name}",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": load_balancer_zone,
                            "DNSName": load_balancer_dns,
                            "EvaluateTargetHealth": True,
                        },
                    },
                },
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": acm_valid_name,
                        "Type": "CNAME",
                        "TTL": 300,
                        "ResourceRecords": [
                            {"Value": acm_valid_target},
                        ],
                    },
                },
            ],
        },
    )
    return response["ChangeInfo"]["Id"]


def create_mephisto_vpc(session: boto3.Session) -> Dict[str, str]:
    """
    Create the required vpc with two subnets, an associated
    internet gateway, and routing tables.

    Currently sets up using US-east for both subnets
    """
    client = session.client("ec2")

    # Create VPC
    vpc_response = client.create_vpc(
        CidrBlock="10.0.0.0/16",
        TagSpecifications=[
            {
                "ResourceType": "vpc",
                "Tags": [
                    {"Key": "Name", "Value": "mephisto-core-vpc"},
                    get_owner_tag(),
                ],
            }
        ],
    )
    vpc_id = vpc_response["Vpc"]["VpcId"]

    # Create internet gateway
    gateway_response = client.create_internet_gateway(
        TagSpecifications=[
            {
                "ResourceType": "internet-gateway",
                "Tags": [{"Key": "Name", "Value": "mephisto-gateway"}, get_owner_tag()],
            }
        ],
    )
    gateway_id = gateway_response["InternetGateway"]["InternetGatewayId"]
    client.attach_internet_gateway(
        InternetGatewayId=gateway_id,
        VpcId=vpc_id,
    )

    # Create subnets
    subnet_1_response = client.create_subnet(
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [
                    {"Key": "Name", "Value": "mephisto-subnet-1"},
                    get_owner_tag(),
                ],
            }
        ],
        CidrBlock="10.0.0.0/24",
        AvailabilityZone="us-east-2a",
        VpcId=vpc_id,
    )
    subnet_1_id = subnet_1_response["Subnet"]["SubnetId"]

    subnet_2_response = client.create_subnet(
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [
                    {"Key": "Name", "Value": "mephisto-subnet-2"},
                    get_owner_tag(),
                ],
            }
        ],
        CidrBlock="10.0.1.0/24",
        AvailabilityZone="us-east-2b",
        VpcId=vpc_id,
    )
    subnet_2_id = subnet_2_response["Subnet"]["SubnetId"]

    # Create routing tables
    table_1_response = client.create_route_table(
        TagSpecifications=[
            {
                "ResourceType": "route-table",
                "Tags": [
                    {"Key": "Name", "Value": "mephisto-routes-1"},
                    get_owner_tag(),
                ],
            }
        ],
        VpcId=vpc_id,
    )
    route_table_1_id = table_1_response["RouteTable"]["RouteTableId"]

    table_2_response = client.create_route_table(
        TagSpecifications=[
            {
                "ResourceType": "route-table",
                "Tags": [
                    {"Key": "Name", "Value": "mephisto-routes-2"},
                    get_owner_tag(),
                ],
            }
        ],
        VpcId=vpc_id,
    )
    route_table_2_id = table_2_response["RouteTable"]["RouteTableId"]

    # Add routes in tables to gateway
    client.create_route(
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=gateway_id,
        RouteTableId=route_table_1_id,
    )
    client.create_route(
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=gateway_id,
        RouteTableId=route_table_2_id,
    )

    # Associate routing tables
    client.associate_route_table(
        RouteTableId=route_table_1_id,
        SubnetId=subnet_1_id,
    )
    client.associate_route_table(
        RouteTableId=route_table_2_id,
        SubnetId=subnet_2_id,
    )

    return {
        "vpc_id": vpc_id,
        "gateway_id": gateway_id,
        "subnet_1_id": subnet_1_id,
        "subnet_2_id": subnet_2_id,
        "route_1_id": route_table_1_id,
        "route_2_id": route_table_2_id,
    }


def create_security_group(session: boto3.Session, vpc_id: str, ssh_ip: str) -> str:
    """
    Create a security group with public access
    for 80 and 443, but only access from ssh_ip (comma-separated) for 22
    """
    client = session.client("ec2")

    create_response = client.create_security_group(
        Description="Security group used for Mephisto host servers",
        GroupName="mephisto-server-security-group",
        VpcId=vpc_id,
        TagSpecifications=[
            {
                "ResourceType": "security-group",
                "Tags": [
                    {"Key": "Name", "Value": "mephisto-server-security-group"},
                    get_owner_tag(),
                ],
            }
        ],
    )
    group_id = create_response["GroupId"]
    ssh_perms = [
        {
            "FromPort": 22,
            "ToPort": 22,
            "IpProtocol": "tcp",
            "IpRanges": [
                {
                    "CidrIp": one_ip,
                    "Description": "SSH from allowed ip",
                }
            ],
        }
        for one_ip in ssh_ip.split(",")
    ]

    response = client.authorize_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {
                "FromPort": 80,
                "ToPort": 80,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Public insecure http access",
                    }
                ],
            },
            {
                "FromPort": 80,
                "ToPort": 80,
                "IpProtocol": "tcp",
                "Ipv6Ranges": [
                    {
                        "CidrIpv6": "::/0",
                        "Description": "Public insecure http access",
                    }
                ],
            },
            {
                "FromPort": 5000,
                "ToPort": 5000,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Internal router access",
                    }
                ],
            },
            {
                "FromPort": 5000,
                "ToPort": 5000,
                "IpProtocol": "tcp",
                "Ipv6Ranges": [
                    {
                        "CidrIpv6": "::/0",
                        "Description": "Internal router access",
                    }
                ],
            },
            {
                "FromPort": 443,
                "ToPort": 443,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Public secure http access",
                    }
                ],
            },
            {
                "FromPort": 443,
                "ToPort": 443,
                "IpProtocol": "tcp",
                "Ipv6Ranges": [
                    {
                        "CidrIpv6": "::/0",
                        "Description": "Public secure http access",
                    }
                ],
            },
        ]
        + ssh_perms,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    return group_id


def create_key_pair(
    session: boto3.Session,
    key_name: str,
    key_pair_dir: str = DEFAULT_KEY_PAIR_DIRECTORY,
) -> str:
    """
    creates a key pair by the given name, and writes it to file
    """
    target_keypair_filename = os.path.join(key_pair_dir, f"{key_name}.pem")
    if os.path.exists(target_keypair_filename):
        logger.warning(f"Keypair already exists! {target_keypair_filename}")
        return target_keypair_filename
    client = session.client("ec2")

    response = client.create_key_pair(
        KeyName=key_name,
        TagSpecifications=[
            {
                "ResourceType": "key-pair",
                "Tags": [{"Key": "Name", "Value": key_name}, get_owner_tag()],
            }
        ],
    )
    with open(target_keypair_filename, "w+") as keypair_file:
        keypair_file.write(response["KeyMaterial"])
        subprocess.check_call(["chmod", "400", target_keypair_filename])

    return target_keypair_filename


def create_instance(
    session: boto3.Session,
    key_pair_name: str,
    security_group_id: str,
    subnet_id: str,
    instance_name: str,
    volume_size: int = 8,
    instance_type: str = DEFAULT_INSTANCE_TYPE,
) -> str:
    """
    Create an instance, return the instance id, allocation id, and association id
    """
    client = session.client("ec2")
    instance_response = client.run_instances(
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": volume_size,
                    "VolumeType": "gp2",
                    "Encrypted": True,
                },
            }
        ],
        ImageId=DEFAULT_AMI_ID,
        InstanceType=instance_type,
        KeyName=key_pair_name,
        MaxCount=1,
        MinCount=1,
        Monitoring={
            "Enabled": False,
        },  # standard monitoring is enough
        Placement={
            "Tenancy": "default",
        },
        SecurityGroupIds=[security_group_id],
        SubnetId=subnet_id,
        DisableApiTermination=False,  # we need to allow shutdown from botocore
        # IamInstanceProfile={ # Maybe we can move the iam role to do rest of registration?
        #     'Arn': 'string',
        #     'Name': 'string'
        # },
        InstanceInitiatedShutdownBehavior="stop",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": instance_name},
                    get_owner_tag(),
                ],
            },
        ],
        HibernationOptions={"Configured": False},
        MetadataOptions={
            "HttpTokens": "optional",
            "HttpEndpoint": "enabled",
        },
        EnclaveOptions={"Enabled": False},
    )
    instance_id = instance_response["Instances"][0]["InstanceId"]

    logger.debug(f"Waiting for instance {instance_id} to come up before continuing")
    waiter = client.get_waiter("instance_running")
    waiter.wait(
        InstanceIds=[instance_id],
    )

    return instance_id


def create_target_group(
    session: boto3.Session,
    vpc_id: str,
    instance_id: str,
    group_name="mephisto-fallback",
) -> str:
    """
    Create a target group for the given instance
    """
    client = session.client("elbv2")
    group_name_hash = hashlib.md5(group_name.encode("utf-8")).hexdigest()
    anti_collision_group_name = f"{group_name_hash[:8]}-{group_name}"
    final_group_name = f"{anti_collision_group_name[:28]}-tg"
    create_target_response = client.create_target_group(
        Name=final_group_name[:32],
        Protocol="HTTP",
        ProtocolVersion="HTTP1",
        Port=5000,
        VpcId=vpc_id,
        Matcher={
            "HttpCode": "200-299",
        },
        TargetType="instance",
        Tags=[
            {"Key": "string", "Value": "string"},
        ],
    )
    target_group_arn = create_target_response["TargetGroups"][0]["TargetGroupArn"]

    client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[
            {
                "Id": instance_id,
            }
        ],
    )

    return target_group_arn


def rule_is_new(
    session: boto3.Session,
    subdomain: str,
    listener_arn: str,
) -> bool:
    """
    Check to see if a rule already exists with the given subdomain
    """
    client = session.client("elbv2")
    find_rule_response = client.describe_rules(
        ListenerArn=listener_arn,
    )
    rules = find_rule_response["Rules"]
    for rule in rules:
        if len(rule["Conditions"]) == 0:
            continue  # base rule
        host_condition = rule["Conditions"][0]
        values = host_condition.get("Values")
        if values is None or len(values) == 0:
            values = host_condition["HostHeaderConfig"]["Values"]
        existing = values[0]
        if existing.startswith(f"{subdomain}."):
            return False

    return True


def register_instance_to_listener(
    session: boto3.Session,
    instance_id: str,
    vpc_id: str,
    listener_arn: str,
    domain: str,
) -> Tuple[str, str]:
    """
    Creates a rule for this specific redirect case,
    and returns the target group id and rule arn
    """
    subdomain_root = domain.split(".")[0]
    target_group_arn = create_target_group(session, vpc_id, instance_id, subdomain_root)
    client = session.client("elbv2")

    find_rule_response = client.describe_rules(
        ListenerArn=listener_arn,
    )

    # Get the next available priority
    priorities = set([r["Priority"] for r in find_rule_response["Rules"]])
    priority = 1
    while str(priority) in priorities:
        priority += 1

    rule_response = client.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {
                "Field": "host-header",
                "HostHeaderConfig": {
                    "Values": [
                        domain,
                        f"*.{domain}",
                    ],
                },
            },
        ],
        Priority=priority,
        Actions=[
            {
                "Type": "forward",
                "TargetGroupArn": target_group_arn,
            },
        ],
    )
    rule_arn = rule_response["Rules"][0]["RuleArn"]

    return target_group_arn, rule_arn


def create_load_balancer(
    session: boto3.Session,
    subnet_ids: List[str],
    security_group_id: str,
    vpc_id: str,
) -> str:
    """
    Creates a load balancer and returns the balancer's arn
    """
    client = session.client("elbv2")

    create_response = client.create_load_balancer(
        Name="mephisto-hosts-balancer",
        Subnets=subnet_ids,
        SecurityGroups=[security_group_id],
        Scheme="internet-facing",
        Type="application",
        IpAddressType="ipv4",
    )
    balancer_arn = create_response["LoadBalancers"][0]["LoadBalancerArn"]
    return balancer_arn


def configure_base_balancer(
    session: boto3.Session,
    balancer_arn: str,
    certificate_arn: str,
    target_group_arn: str,
) -> str:
    """
    Configure the default rules for this load balancer. Return the id
    of the listener to add rules to for redirecting to specified target groups
    """

    client = session.client("elbv2")

    _redirect_response = client.create_listener(
        LoadBalancerArn=balancer_arn,
        Protocol="HTTP",
        Port=80,
        DefaultActions=[
            {
                "Type": "redirect",
                "RedirectConfig": {
                    "Protocol": "HTTPS",
                    "Port": "443",
                    "Host": "#{host}",
                    "Path": "/#{path}",
                    "Query": "#{query}",
                    "StatusCode": "HTTP_301",
                },
            }
        ],
    )

    forward_response = client.create_listener(
        LoadBalancerArn=balancer_arn,
        Protocol="HTTPS",
        Port=443,
        SslPolicy="ELBSecurityPolicy-2016-08",
        Certificates=[
            {
                "CertificateArn": certificate_arn,
            }
        ],
        DefaultActions=[
            {
                "Type": "forward",
                "TargetGroupArn": target_group_arn,
            }
        ],
    )
    listener_arn = forward_response["Listeners"][0]["ListenerArn"]
    return listener_arn


def get_instance_address(
    session: boto3.Session,
    instance_id: str,
) -> Tuple[str, str, str]:
    """
    Create a temporary publicly accessible IP for the given instance.
    Return the IP address, the allocation id, and the association id.
    """
    client = session.client("ec2")

    allocation_response = client.allocate_address(
        Domain="vpc",
        TagSpecifications=[
            {
                "ResourceType": "elastic-ip",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": f"{instance_id}-ip-address",
                    },
                    get_owner_tag(),
                ],
            }
        ],
    )
    ip_address = allocation_response["PublicIp"]
    allocation_id = allocation_response["AllocationId"]

    associate_response = client.associate_address(
        AllocationId=allocation_id,
        InstanceId=instance_id,
        AllowReassociation=False,
    )
    association_id = associate_response["AssociationId"]

    # Remove this IP from known hosts in case it's there,
    # as it's definitely not the old host anymore
    subprocess.check_call(
        [
            "ssh-keygen",
            "-f",
            f"{KNOWN_HOST_PATH}",
            "-R",
            f'"{ip_address}"',
        ]
    )

    return ip_address, allocation_id, association_id


def detete_instance_address(
    session: boto3.Session,
    allocation_id: str,
    association_id: str,
) -> None:
    """
    Removes the public ip described by the given allocation and association ids
    """
    client = session.client("ec2")
    client.disassociate_address(
        AssociationId=association_id,
    )

    client.release_address(
        AllocationId=allocation_id,
    )


def try_server_push(subprocess_args: List[str], retries=5, sleep_time=10.0):
    """
    Try to execute the server push provided in subprocess args
    """
    while retries > 0:
        try:
            subprocess.check_call(
                subprocess_args, env=dict(os.environ, SSH_AUTH_SOCK="")
            )
            return
        except subprocess.CalledProcessError:
            retries -= 1
            sleep_time *= 1.5
            logger.info(
                f"Timed out trying to push to server. Retries remaining: {retries}"
            )
            time.sleep(sleep_time)
    raise Exception(
        "Could not successfully push to the ec2 instance. See log for errors."
    )


def deploy_fallback_server(
    session: boto3.Session,
    instance_id: str,
    key_pair: str,
    log_access_pass: str,
) -> bool:
    """
    Deploy the fallback server to the given instance,
    return True if successful
    """
    client = session.client("ec2")
    server_host, allocation_id, association_id = get_instance_address(
        session, instance_id
    )
    try:
        keypair_file = os.path.join(DEFAULT_KEY_PAIR_DIRECTORY, f"{key_pair}.pem")
        password_file_name = os.path.join(FALLBACK_SERVER_LOC, f"access_key.txt")
        with open(password_file_name, "w+") as password_file:
            password_file.write(log_access_pass)

        remote_server = f"{AMI_DEFAULT_USER}@{server_host}"

        dest = f"{remote_server}:/home/ec2-user/"
        try_server_push(
            [
                "scp",
                "-o",
                "StrictHostKeyChecking=no",
                "-i",
                keypair_file,
                "-r",
                f"{FALLBACK_SERVER_LOC}",
                dest,
            ]
        )
        os.unlink(password_file_name)
        subprocess.check_call(
            [
                "ssh",
                "-i",
                keypair_file,
                remote_server,
                "bash",
                "/home/ec2-user/fallback_server/scripts/first_setup.sh",
            ],
            env=dict(os.environ, SSH_AUTH_SOCK=""),
        )
        detete_instance_address(session, allocation_id, association_id)
    except Exception as e:
        detete_instance_address(session, allocation_id, association_id)
        raise e

    return True


def deploy_to_routing_server(
    session: boto3.Session,
    instance_id: str,
    key_pair: str,
    push_directory: str,
) -> bool:
    client = session.client("ec2")
    server_host, allocation_id, association_id = get_instance_address(
        session, instance_id
    )
    keypair_file = os.path.join(DEFAULT_KEY_PAIR_DIRECTORY, f"{key_pair}.pem")

    print("Uploading files to server, then attempting to run")
    try:
        remote_server = f"{AMI_DEFAULT_USER}@{server_host}"
        dest = f"{remote_server}:/home/ec2-user/"
        try_server_push(
            [
                "scp",
                "-o",
                "StrictHostKeyChecking=no",
                "-i",
                keypair_file,
                "-r",
                f"{push_directory}",
                dest,
            ]
        )

        subprocess.check_call(
            [
                "ssh",
                "-i",
                keypair_file,
                remote_server,
                "bash",
                "/home/ec2-user/routing_server/setup/init_server.sh",
            ],
            env=dict(os.environ, SSH_AUTH_SOCK=""),
        )
        detete_instance_address(session, allocation_id, association_id)
        print("Server setup complete!")
    except Exception as e:
        detete_instance_address(session, allocation_id, association_id)
        raise e

    return True


def delete_rule(
    session: boto3.Session,
    rule_arn: str,
    target_group_arn: str,
) -> None:
    """
    Remove the given rule and the target group for this rule
    """
    client = session.client("elbv2")
    client.delete_rule(
        RuleArn=rule_arn,
    )

    client.delete_target_group(
        TargetGroupArn=target_group_arn,
    )


def delete_instance(
    session: boto3.Session,
    instance_id: str,
) -> None:
    """
    Remove the given instance and the associated elastic ip
    """
    client = session.client("ec2")
    client.terminate_instances(InstanceIds=[instance_id])


def remove_instance_and_cleanup(
    session: boto3.Session,
    server_name: str,
) -> None:
    """
    Cleanup for a launched server, removing the redirect rule
    clearing the target group, and then shutting down the instance.
    """
    server_detail_path = os.path.join(
        DEFAULT_SERVER_DETAIL_LOCATION, f"{server_name}.json"
    )

    with open(server_detail_path, "r") as detail_file:
        details = json.load(detail_file)

    delete_rule(session, details["balancer_rule_arn"], details["target_group_arn"])
    delete_instance(
        session,
        details["instance_id"],
    )
    os.unlink(server_detail_path)
    return None


def delete_listener(
    session: boto3.Session,
    listener_arn: str,
) -> None:
    client = session.client("elbv2")
    client.delete_listener(
        ListenerArn=listener_arn,
    )


def cleanup_fallback_server(
    iam_profile: str,
    delete_hosted_zone: bool = False,
    server_details_file: str = DEFAULT_FALLBACK_FILE,
) -> None:
    """
    Cleans up all of the resources for the given iam profile,
    assuming that the details are stored in the given
    server_details_file.

    Optionally includes deleting the hosted zone, which remains
    an option due to the DNS changes required
    """
    session = boto3.Session(profile_name=iam_profile, region_name="us-east-2")

    elb_client = session.client("elbv2")
    ec2_client = session.client("ec2")

    server_details_file = (
        DEFAULT_FALLBACK_FILE if server_details_file is None else server_details_file
    )
    with open(server_details_file, "r") as details_file:
        details = json.load(details_file)

    listener_arn = details.get("listener_arn")
    if listener_arn is not None:
        print(f"Deleting listener {listener_arn}...")
        find_rule_response = elb_client.describe_rules(
            ListenerArn=listener_arn,
        )
        rules = find_rule_response["Rules"]
        if len(rules) > 1:
            confirm = input(
                "There are still existing rules on the router, which would imply that active jobs are running right now. Are you SURE you want to DELETE ALL?[yes/no]"
            )
            if confirm != "yes":
                return
        elb_client.delete_listener(
            ListenerArn=listener_arn,
        )

    target_group_arn = details.get("target_group_arn")
    if target_group_arn is not None:
        print(f"Deleting target group {target_group_arn}...")
        elb_client.delete_target_group(
            TargetGroupArn=target_group_arn,
        )

    balancer_arn = details.get("balancer_arn")
    if balancer_arn is not None:
        print(f"Deleting balancer {balancer_arn}...")
        elb_client.delete_load_balancer(
            LoadBalancerArn=balancer_arn,
        )

    instance_id = details.get("instance_id")
    if instance_id is not None:
        print(f"Deleting instance {instance_id}...")
        delete_instance(session, instance_id)

    vpc_details = details.get("vpc_details")
    if vpc_details is not None:
        print(f"Deleting vpc {vpc_details['vpc_id']} and related resources...")
        ec2_client.delete_subnet(SubnetId=vpc_details["subnet_1_id"])
        ec2_client.delete_subnet(SubnetId=vpc_details["subnet_2_id"])
        ec2_client.delete_route_table(RouteTableId=vpc_details["route_1_id"])
        ec2_client.delete_route_table(RouteTableId=vpc_details["route_2_id"])
        table_response = ec2_client.describe_route_tables(
            Filters=[
                {
                    "Name": "vpc-id",
                    "Values": [vpc_details["vpc_id"]],
                }
            ]
        )
        tables = table_response["RouteTables"]
        for table in tables:
            ec2_client.delete_route_table(RouteTableId=table["RouteTableId"])

        ec2_client.delete_internet_gateway(InternetGatewayId=vpc_details["gateway_id"])

        security_group_id = details.get("security_group_id")
        if security_group_id is not None:
            print("Deleting security group {security_group_id}...")
            ec2_client.delete_security_group(
                GroupId=security_group_id,
            )

        ec2_client.delete_vpc(VpcId=vpc_details["vpc_id"])

    if delete_hosted_zone:
        hosted_zone_id = details.get("hosted_zone_id")
        if hosted_zone_id is not None:
            route53_client = session.client("route53")
            print(
                "Deleting hosted zones not yet implemented, "
                "navigate to the AWS Route53 console to complete "
                f"this step, deleting {hosted_zone_id}"
            )
            # To delete a hosted zone, we need to query it
            # for the list of records, than remove all
            # that aren't SOA/NS

    os.unlink(server_details_file)
    return None
