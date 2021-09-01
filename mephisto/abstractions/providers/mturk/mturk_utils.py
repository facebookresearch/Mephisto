#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import boto3
import os
import json
import re
from tqdm import tqdm
from typing import Dict, Optional, Tuple, List, Any, TYPE_CHECKING
from datetime import datetime

from botocore import client
from botocore.exceptions import ClientError, ProfileNotFound
from botocore.config import Config
from omegaconf import DictConfig

from mephisto.data_model.qualification import QUAL_EXISTS, QUAL_NOT_EXIST
from mephisto.operations.logger_core import get_logger
from mephisto.operations.config_handler import get_config_arg

logger = get_logger(name=__name__)

if TYPE_CHECKING:
    from mephisto.data_model.task_config import TaskConfig

MTURK_TASK_FEE = 0.2
MTURK_BONUS_FEE = 0.2
SANDBOX_ENDPOINT = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"

MTurkClient = Any

MTURK_LOCALE_REQUIREMENT = "00000000000000000071"

botoconfig = Config(retries=dict(max_attempts=10))

QUALIFICATION_TYPE_EXISTS_MESSAGE = (
    "You have already created a QualificationType with this name."
)


def client_is_sandbox(client: MTurkClient) -> bool:
    """
    Determine if the given client is communicating with
    the live server or a sandbox
    """
    return client.meta.endpoint_url == SANDBOX_ENDPOINT


def check_aws_credentials(profile_name: str) -> bool:
    try:
        # Check existing credentials
        boto3.Session(profile_name=profile_name)
        return True
    except ProfileNotFound:
        return False


def setup_aws_credentials(
    profile_name: str, register_args: Optional[DictConfig] = None
) -> bool:
    try:
        # Check existing credentials
        boto3.Session(profile_name=profile_name)
        if register_args is not None:
            # Eventually we could manually re-parse the file and see
            # if the credentials line up or not, then fix ourselves
            print(
                f"WARNING credentials provided, but there's already a "
                f"profile for {profile_name}. If these don't line up, you'll "
                f"need to manually navigate to your ~/.aws/credentials file "
                f"and remove the entry for this profile name, then run again.\n"
                f"As this profile is currently loading, we consider it "
                f"successfully registered anyways."
            )
        return True
    except ProfileNotFound:
        # Setup new credentials
        if register_args is not None:
            aws_access_key_id = register_args.access_key_id
            aws_secret_access_key = register_args.secret_access_key
        else:
            print(
                f"AWS credentials for {profile_name} not found. Please create "
                "an IAM user with "
                "programmatic access and AdministratorAccess policy at "
                'https://console.aws.amazon.com/iam/ (On the "Set permissions" '
                'page, choose "Attach existing policies directly" and then select '
                '"AdministratorAccess" policy). After creating the IAM user, '
                "please enter the user's Access Key ID and Secret Access "
                "Key below:"
            )
            aws_access_key_id = input("Access Key ID: ")
            aws_secret_access_key = input("Secret Access Key: ")
        if not os.path.exists(os.path.expanduser("~/.aws/")):
            os.makedirs(os.path.expanduser("~/.aws/"))
        aws_credentials_file_path = "~/.aws/credentials"
        aws_credentials_file_string = None
        expanded_aws_file_path = os.path.expanduser(aws_credentials_file_path)
        if os.path.exists(expanded_aws_file_path):
            with open(expanded_aws_file_path, "r") as aws_credentials_file:
                aws_credentials_file_string = aws_credentials_file.read()
        with open(expanded_aws_file_path, "a+") as aws_credentials_file:
            # Clean up file
            if aws_credentials_file_string:
                if aws_credentials_file_string.endswith("\n\n"):
                    pass
                elif aws_credentials_file_string.endswith("\n"):
                    aws_credentials_file.write("\n")
                else:
                    aws_credentials_file.write("\n\n")
            # Write login details
            aws_credentials_file.write("[{}]\n".format(profile_name))
            aws_credentials_file.write(
                "aws_access_key_id={}\n".format(aws_access_key_id)
            )
            aws_credentials_file.write(
                "aws_secret_access_key={}\n".format(aws_secret_access_key)
            )
        print(
            "AWS credentials successfully saved in {} file.\n".format(
                aws_credentials_file_path
            )
        )
        return True


def calculate_mturk_task_fee(task_amount: float) -> float:
    """
    MTurk Pricing: https://requester.mturk.com/pricing
    20% fee on the reward and bonus amount (if any) you pay Workers.
    """
    return MTURK_TASK_FEE * task_amount


def calculate_mturk_bonus_fee(bonus_amount: float) -> float:
    """
    MTurk Pricing: https://requester.mturk.com/pricing
    20% fee on the reward and bonus amount (if any) you pay Workers.
    """
    return MTURK_BONUS_FEE * bonus_amount


def get_requester_balance(client: MTurkClient) -> float:
    """Get the balance for the requester associated with this client"""
    return float(client.get_account_balance()["AvailableBalance"])


def check_mturk_balance(client: MTurkClient, balance_needed: float):
    """Checks to see if there is at least balance_needed amount in the
    requester account, returns True if the balance is greater than
    balance_needed
    """
    # Test that you can connect to the API by checking your account balance
    # In Sandbox this always returns $10,000
    try:
        user_balance = float(client.get_account_balance()["AvailableBalance"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "RequestError":
            print(
                "ERROR: To use the MTurk API, you will need an Amazon Web "
                "Services (AWS) Account. Your AWS account must be linked to "
                "your Amazon Mechanical Turk Account. Visit "
                "https://requestersandbox.mturk.com/developer to get started. "
                "(Note: if you have recently linked your account, please wait "
                "for a couple minutes before trying again.)\n"
            )
            quit()
        else:
            raise

    if user_balance < balance_needed:
        print(
            "You might not have enough money in your MTurk account. Please go "
            "to https://requester.mturk.com/account and increase your balance "
            "to at least ${}, and then try again.".format(balance_needed)
        )
        return False
    else:
        return True


def create_hit_config(
    opt: Dict[str, Any], task_description: str, unique_worker: bool, is_sandbox: bool
) -> None:
    """Writes a HIT config to file"""
    mturk_submit_url = "https://workersandbox.mturk.com/mturk/externalSubmit"
    if not is_sandbox:
        mturk_submit_url = "https://www.mturk.com/mturk/externalSubmit"
    hit_config = {
        "task_description": task_description,
        "is_sandbox": is_sandbox,
        "mturk_submit_url": mturk_submit_url,
        "unique_worker": unique_worker,
        "frame_height": opt.get("frame_height", 0),
        "allow_reviews": opt.get("allow_reviews", False),
        "block_mobile": opt.get("block_mobile", True),
        # Populate the chat pane title from chat_title, defaulting to the
        # hit_title if the task provides no chat_title
        "chat_title": opt.get("chat_title", opt.get("hit_title", "Live Chat")),
        "template_type": opt.get("frontend_template_type", "default"),
    }
    hit_config_file_path = os.path.join(opt["tmp_dir"], "hit_config.json")
    if os.path.exists(hit_config_file_path):
        os.remove(hit_config_file_path)
    with open(hit_config_file_path, "w") as hit_config_file:
        hit_config_file.write(json.dumps(hit_config))


def delete_qualification(client: MTurkClient, qualification_id: str) -> None:
    """Deletes a qualification by id"""
    client.delete_qualification_type(QualificationTypeId=qualification_id)


def find_qualification(
    client: MTurkClient, qualification_name: str, must_be_owned: bool = True
) -> Tuple[bool, Optional[str]]:
    """Query amazon to find the existing qualification name, return the Id,
    otherwise return none.
    If must_be_owned is true, it only returns qualifications owned by the user.
    Will return False if it finds another's qualification

    The return format is (meets_owner_constraint, qual_id)
    """
    # Search for the qualification owned by the current user
    response = client.list_qualification_types(
        Query=qualification_name, MustBeRequestable=True, MustBeOwnedByCaller=True
    )
    for qualification in response["QualificationTypes"]:
        if qualification["Name"] == qualification_name:
            return (True, qualification["QualificationTypeId"])

    # Qualification was not found to exist, check to see if someone else has it
    response = client.list_qualification_types(
        Query=qualification_name, MustBeRequestable=True, MustBeOwnedByCaller=False
    )

    for qualification in response["QualificationTypes"]:
        if qualification["Name"] == qualification_name:
            if must_be_owned:
                return (False, qualification["QualificationTypeId"])
            return (True, qualification["QualificationTypeId"])
    return (True, None)


def find_or_create_qualification(
    client: MTurkClient,
    qualification_name: str,
    description: str,
    must_be_owned: bool = True,
) -> Optional[str]:
    """Query amazon to find the existing qualification name, return the Id. If
    it exists and must_be_owned is true but we don't own it, this returns none.
    If it doesn't exist, the qualification is created
    """

    def _try_finding_qual_id():
        qual_usable, qual_id = find_qualification(
            client, qualification_name, must_be_owned=must_be_owned
        )
        if qual_id is None:
            return False, None
        elif qual_usable is False:
            return True, None
        else:
            return True, qual_id

    found_qual, qual_id = _try_finding_qual_id()
    if found_qual:
        return qual_id

    # Create the qualification, as it doesn't exist yet
    try:
        response = client.create_qualification_type(
            Name=qualification_name,
            Description=description,
            QualificationTypeStatus="Active",
        )
    except ClientError as e:
        msg = e.response.get("Error", {}).get("Message")
        if msg is not None and msg.startswith(QUALIFICATION_TYPE_EXISTS_MESSAGE):
            # Created this qualification somewhere else - find instead
            found_qual, qual_id = _try_finding_qual_id()
            assert found_qual, "Qualification exists, but could not be found?"
            return qual_id
        else:
            raise e

    return response["QualificationType"]["QualificationTypeId"]


def give_worker_qualification(
    client: MTurkClient,
    worker_id: str,
    qualification_id: str,
    value: Optional[int] = None,
) -> None:
    """Give a qualification to the given worker"""
    if value is not None:
        client.associate_qualification_with_worker(
            QualificationTypeId=qualification_id,
            WorkerId=worker_id,
            IntegerValue=value,
            SendNotification=False,
        )
    else:
        client.associate_qualification_with_worker(
            QualificationTypeId=qualification_id,
            WorkerId=worker_id,
            IntegerValue=1,
            SendNotification=False,
        )


def remove_worker_qualification(
    client: MTurkClient, worker_id: str, qualification_id: str, reason: str = ""
) -> None:
    """Give a qualification to the given worker"""
    client.disassociate_qualification_from_worker(
        QualificationTypeId=qualification_id, WorkerId=worker_id, Reason=reason
    )


def convert_mephisto_qualifications(
    client: MTurkClient, qualifications: List[Dict[str, Any]]
):
    """Convert qualifications from mephisto's format to MTurk's"""
    converted_qualifications = []
    for qualification in qualifications:
        converted = {}
        mturk_keys = [
            "QualificationTypeId",
            "Comparator",
            "IntegerValue",
            "IntegerValues",
            "LocaleValues",
            "ActionsGuarded",
        ]
        for key in mturk_keys:
            converted[key] = qualification.get(key)

        if converted["QualificationTypeId"] is None:
            qualification_name = qualification["qualification_name"]
            if client_is_sandbox(client):
                qualification_name += "_sandbox"
            qual_id = find_or_create_qualification(
                client,
                qualification_name,
                "Qualification required for Mephisto-launched tasks",
                False,
            )
            if qual_id is None:
                # TODO log more loudly that this qualification is being skipped?
                print(
                    f"Qualification name {qualification_name} can not be found or created on MTurk"
                )
            converted["QualificationTypeId"] = qual_id

        if converted["Comparator"] is None:
            converted["Comparator"] = qualification["comparator"]

        # if no Mturk Values are set, pull from the qualification's value
        if (
            converted["IntegerValue"] is None
            and converted["IntegerValues"] is None
            and converted["LocaleValues"] is None
            and converted["Comparator"] not in [QUAL_EXISTS, QUAL_NOT_EXIST]
        ):
            value = qualification["value"]
            if isinstance(value, list):
                converted["IntegerValues"] = value
            elif isinstance(value, int):
                converted["IntegerValue"] = value

        # IntegerValue is deprecated, and needs conversion to IntegerValues
        if converted["IntegerValue"] is not None:
            converted["IntegerValues"] = [converted["IntegerValue"]]
        del converted["IntegerValue"]

        if converted["IntegerValues"] is None:
            del converted["IntegerValues"]

        if converted["LocaleValues"] is None:
            del converted["LocaleValues"]

        if converted["ActionsGuarded"] is None:
            converted["ActionsGuarded"] = "DiscoverPreviewAndAccept"

        converted_qualifications.append(converted)
    return converted_qualifications


def create_hit_type(
    client: MTurkClient,
    task_config: "TaskConfig",
    qualifications: List[Dict[str, Any]],
    auto_approve_delay: Optional[int] = 7 * 24 * 3600,  # default 1 week
) -> str:
    """Create a HIT type to be used to generate HITs of the requested params"""
    hit_title = task_config.task_title
    hit_description = task_config.task_description
    hit_keywords = ",".join(task_config.task_tags)
    hit_reward = task_config.task_reward
    assignment_duration_in_seconds = task_config.assignment_duration_in_seconds
    existing_qualifications = convert_mephisto_qualifications(client, qualifications)

    # If the user hasn't specified a location qualification, we assume to
    # restrict the HIT to some english-speaking countries.
    locale_requirements: List[Any] = []
    has_locale_qual = False
    if existing_qualifications is not None:
        for q in existing_qualifications:
            if q["QualificationTypeId"] == MTURK_LOCALE_REQUIREMENT:
                has_locale_qual = True
        locale_requirements += existing_qualifications

    if not has_locale_qual and not client_is_sandbox(client):
        allowed_locales = get_config_arg("mturk", "allowed_locales")
        if allowed_locales is None:
            allowed_locales = [
                {"Country": "US"},
                {"Country": "CA"},
                {"Country": "GB"},
                {"Country": "AU"},
                {"Country": "NZ"},
            ]
        locale_requirements.append(
            {
                "QualificationTypeId": MTURK_LOCALE_REQUIREMENT,
                "Comparator": "In",
                "LocaleValues": allowed_locales,
                "ActionsGuarded": "DiscoverPreviewAndAccept",
            }
        )

    # Create the HIT type
    response = client.create_hit_type(
        AutoApprovalDelayInSeconds=auto_approve_delay,
        AssignmentDurationInSeconds=assignment_duration_in_seconds,
        Reward=str(hit_reward),
        Title=hit_title,
        Keywords=hit_keywords,
        Description=hit_description,
        QualificationRequirements=locale_requirements,
    )
    hit_type_id = response["HITTypeId"]
    return hit_type_id


def create_hit_with_hit_type(
    client: MTurkClient,
    frame_height: int,
    page_url: str,
    hit_type_id: str,
    num_assignments: int = 1,
) -> Tuple[str, str, Dict[str, Any]]:
    """Creates the actual HIT given the type and page to direct clients to"""
    page_url = page_url.replace("&", "&amp;")
    amazon_ext_url = (
        "http://mechanicalturk.amazonaws.com/"
        "AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"
    )
    question_data_struture = (
        '<ExternalQuestion xmlns="{}">'
        "<ExternalURL>{}</ExternalURL>"  # noqa: E131
        "<FrameHeight>{}</FrameHeight>"
        "</ExternalQuestion>"
        "".format(amazon_ext_url, page_url, frame_height)
    )

    is_sandbox = client_is_sandbox(client)

    # Create the HIT
    response = client.create_hit_with_hit_type(
        HITTypeId=hit_type_id,
        MaxAssignments=num_assignments,
        LifetimeInSeconds=60 * 60 * 24 * 31,
        Question=question_data_struture,
    )

    # The response included several fields that will be helpful later
    hit_type_id = response["HIT"]["HITTypeId"]
    hit_id = response["HIT"]["HITId"]

    # Construct the hit URL
    url_target = "workersandbox"
    if not is_sandbox:
        url_target = "www"
    hit_link = "https://{}.mturk.com/mturk/preview?groupId={}".format(
        url_target, hit_type_id
    )
    return hit_link, hit_id, response


def expire_hit(client: MTurkClient, hit_id: str):
    # Update expiration to a time in the past, the HIT expires instantly
    past_time = datetime(2015, 1, 1)
    client.update_expiration_for_hit(HITId=hit_id, ExpireAt=past_time)


def setup_sns_topic(
    session: boto3.Session, task_name: str, server_url: str, task_run_id: str
) -> str:
    """Create an sns topic and return the arn identifier"""
    # Create the topic and subscribe to it so that our server receives notifs
    client = session.client("sns", region_name="us-east-1", config=botoconfig)
    pattern = re.compile("[^a-zA-Z0-9_-]+")
    filtered_task_name = pattern.sub("", task_name)
    response = client.create_topic(Name=filtered_task_name)
    arn = response["TopicArn"]
    topic_sub_url = "{}/sns_posts?task_run_id={}".format(server_url, task_run_id)
    client.subscribe(TopicArn=arn, Protocol="https", Endpoint=topic_sub_url)
    response = client.get_topic_attributes(TopicArn=arn)
    policy_json = """{{
    "Version": "2008-10-17",
    "Id": "{}/MTurkOnlyPolicy",
    "Statement": [
        {{
            "Sid": "MTurkOnlyPolicy",
            "Effect": "Allow",
            "Principal": {{
                "Service": "mturk-requester.amazonaws.com"
            }},
            "Action": "SNS:Publish",
            "Resource": "{}"
        }}
    ]}}""".format(
        arn, arn
    )
    client.set_topic_attributes(
        TopicArn=arn, AttributeName="Policy", AttributeValue=policy_json
    )
    return arn


def subscribe_to_hits(client: MTurkClient, hit_type_id: str, sns_arn: str) -> None:
    """Subscribe an sns channel to the specific hit type"""
    # Get the mturk client and create notifications for our hits
    client.update_notification_settings(
        HITTypeId=hit_type_id,
        Notification={
            "Destination": sns_arn,
            "Transport": "SNS",
            "Version": "2006-05-05",
            "EventTypes": [
                "AssignmentAbandoned",
                "AssignmentReturned",
                "AssignmentSubmitted",
            ],
        },
        Active=True,
    )


def send_test_notif(client: MTurkClient, topic_arn: str, event_type: str) -> None:
    """
    Send a test notification of the given event type to the sns
    queue associated with the given arn
    """
    client.send_test_event_notification(
        Notification={
            "Destination": topic_arn,
            "Transport": "SNS",
            "Version": "2006-05-05",
            "EventTypes": [
                "AssignmentAbandoned",
                "AssignmentReturned",
                "AssignmentSubmitted",
            ],
        },
        TestEventType=event_type,
    )


def delete_sns_topic(session: boto3.Session, topic_arn: str) -> None:
    """Remove the sns queue of the given identifier"""
    client = session.client("sns", region_name="us-east-1", config=botoconfig)
    client.delete_topic(TopicArn=topic_arn)


def get_hit(client: MTurkClient, hit_id: str) -> Dict[str, Any]:
    """Get hit from mturk by hit_id"""
    hit = None
    try:
        hit = client.get_hit(HITId=hit_id)
    except ClientError as er:
        logger.warning(
            f"Skipping HIT {hit_id}. Unable to retrieve due to ClientError: {er}."
        )
    return hit


def get_assignment(client: MTurkClient, assignment_id: str) -> Dict[str, Any]:
    """Gets assignment from mturk by assignment_id. Only works if the
    assignment is in a completed state
    """
    return client.get_assignment(AssignmentId=assignment_id)


def get_assignments_for_hit(client: MTurkClient, hit_id: str) -> List[Dict[str, Any]]:
    """Get completed assignments for a hit"""
    assignments_info = client.list_assignments_for_hit(HITId=hit_id)
    return assignments_info.get("Assignments", [])


def approve_work(
    client: MTurkClient, assignment_id: str, override_rejection: bool = False
) -> None:
    """approve work for a given assignment through the mturk client"""
    try:
        client.approve_assignment(
            AssignmentId=assignment_id, OverrideRejection=override_rejection
        )
    except Exception as e:
        # TODO(#93) Break down this error to the many reasons why approve may fail,
        # only silently pass on approving an already approved assignment
        logger.exception(
            f"Approving MTurk assignment failed, likely because it has auto-approved. Details: {e}",
            exc_info=True,
        )


def reject_work(client: MTurkClient, assignment_id: str, reason: str) -> None:
    """reject work for a given assignment through the mturk client"""
    try:
        client.reject_assignment(AssignmentId=assignment_id, RequesterFeedback=reason)
    except Exception as e:
        # TODO(#93) Break down this error to the many reasons why approve may fail,
        # only silently pass on approving an already approved assignment
        logger.exception(
            f"Rejecting MTurk assignment failed, likely because it has auto-approved. Details:{e}",
            exc_info=True,
        )


def approve_assignments_for_hit(
    client: MTurkClient, hit_id: str, override_rejection: bool = False
):
    """Approve work for assignments associated with a given hit, through
    mturk client
    """
    assignments = get_assignments_for_hit(client, hit_id)
    for assignment in assignments:
        assignment_id = assignment["AssignmentId"]
        client.approve_assignment(
            AssignmentId=assignment_id, OverrideRejection=override_rejection
        )


def block_worker(client: MTurkClient, worker_id: str, reason: str) -> None:
    """Block a worker by id using the mturk client, passes reason along"""
    res = client.create_worker_block(WorkerId=worker_id, Reason=reason)


def unblock_worker(client: MTurkClient, worker_id: str, reason: str) -> None:
    """Remove a block on the given worker"""
    client.delete_worker_block(WorkerId=worker_id, Reason=reason)


def is_worker_blocked(client: MTurkClient, worker_id: str) -> bool:
    """Determine if the given worker is blocked by this client"""
    blocks = client.list_worker_blocks(MaxResults=100)["WorkerBlocks"]
    blocked_ids = [x["WorkerId"] for x in blocks]
    return worker_id in blocked_ids


def pay_bonus(
    client: MTurkClient,
    worker_id: str,
    bonus_amount: float,
    assignment_id: str,
    reason: str,
    unique_request_token: str,
) -> bool:
    """Handles paying bonus to a Turker, fails for insufficient funds.
    Returns True on success and False on failure
    """
    total_cost = bonus_amount + calculate_mturk_bonus_fee(bonus_amount)
    if not check_mturk_balance(client, balance_needed=total_cost):
        print("Cannot pay bonus. Reason: Insufficient " "funds in your MTurk account.")
        return False

    client.send_bonus(
        WorkerId=worker_id,
        BonusAmount=str(bonus_amount),
        AssignmentId=assignment_id,
        Reason=reason,
        UniqueRequestToken=unique_request_token,
    )

    return True


def email_worker(
    client: MTurkClient, worker_id: str, subject: str, message_text: str
) -> Tuple[bool, str]:
    """Send an email to a worker through the mturk client"""
    response = client.notify_workers(
        Subject=subject, MessageText=message_text, WorkerIds=[worker_id]
    )
    if len(response["NotifyWorkersFailureStatuses"]) > 0:
        failure_message = response["NotifyWorkersFailureStatuses"][0]
        return (False, failure_message["NotifyWorkersFailureMessage"])
    else:
        return (True, "")


def get_outstanding_hits(client: MTurkClient) -> Dict[str, List[Dict[str, Any]]]:
    """Return the HITs sorted by HITTypeId that are still on the MTurk Server"""
    new_hits = client.list_hits(MaxResults=100)
    all_hits = new_hits["HITs"]
    while len(new_hits["HITs"]) > 0:
        new_hits = client.list_hits(MaxResults=100, NextToken=new_hits["NextToken"])
        all_hits += new_hits["HITs"]

    hit_by_type: Dict[str, List[Dict[str, Any]]] = {}
    for h in all_hits:
        hit_type = h["HITTypeId"]
        if hit_type not in hit_by_type:
            hit_by_type[hit_type] = []
        hit_by_type[hit_type].append(h)

    return hit_by_type


def expire_and_dispose_hits(
    client: MTurkClient, hits: List[Dict[str, Any]], quiet: bool = False
) -> List[Dict[str, Any]]:
    """
    Loops over attempting to expire and dispose any hits in the hits list that can be disposed
    Returns any HITs that could not be disposed of
    """
    non_disposed_hits = []
    for h in tqdm(hits, disable=quiet):
        try:
            client.delete_hit(HITId=h["HITId"])
        except Exception as e:
            client.update_expiration_for_hit(
                HITId=h["HITId"], ExpireAt=datetime(2015, 1, 1)
            )
            h["dispose_exception"] = e
            non_disposed_hits.append(h)
    return non_disposed_hits
