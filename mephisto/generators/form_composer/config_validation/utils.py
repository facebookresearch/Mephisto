#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from json import JSONDecodeError
from pathlib import Path
from typing import Any
from typing import List
from typing import Tuple
from typing import Union
from urllib.parse import urljoin
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError
from botocore.exceptions import NoCredentialsError
from rich import print

from mephisto.generators.form_composer.constants import CONTENTTYPE_BY_EXTENSION
from mephisto.generators.form_composer.constants import JSON_IDENTATION
from mephisto.generators.form_composer.constants import S3_URL_EXPIRATION_MINUTES
from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)
s3_client = boto3.client("s3")


def write_config_to_file(config_data: Union[List[dict], dict], file_path: str):
    config_str = json.dumps(config_data, indent=JSON_IDENTATION)

    with open(file_path, "w") as f:
        f.write(config_str)


def read_config_file(
    config_path: str, exit_if_no_file: bool = True
) -> Union[List[dict], dict, None]:

    if not os.path.exists(config_path):
        if exit_if_no_file:
            print(f"[red]Required file not found: '{config_path}'.[/red]")
            exit()

        print(f"[yellow]Required file not found: '{config_path}'.[/yellow]")
        return None

    try:
        with open(config_path) as config_file:
            config_data = json.load(config_file)
    except (JSONDecodeError, TypeError) as e:
        print(f"[red]Could not read JSON from file: '{config_path}': {e}.[/red]")
        exit()

    return config_data


def make_error_message(main_message: str, error_list: List[str], indent: int = 2) -> str:
    prefix = "\n" + (" " * indent) + "- "
    errors_bullets = prefix + prefix.join(map(str, error_list))
    error_title = f"{main_message.rstrip('.')}. Errors:" if main_message else ""
    return error_title + errors_bullets


def get_file_ext(file_name: str) -> str:
    """Cut off file extension without period"""
    return Path(file_name).suffix.lower()[1:]


# ----- S3 -----


def _run_and_handle_boto_errors(
    fn: callable,
    error_message: str = "Error occurred",
    reraise: bool = True,
) -> Any:
    """Handles standard boto errors in a standard way"""
    try:
        return fn()

    except BotoCoreError as e:
        if isinstance(e, NoCredentialsError):
            error_message = "Missing AWS credentials caused the following error: " + error_message
        logger.exception(error_message)

        if reraise:
            raise


def is_s3_url(value: str) -> bool:
    if isinstance(value, str):
        parsed_url = urlparse(value)
        return bool(
            parsed_url.scheme == "https"
            and "s3" in parsed_url.hostname
            and parsed_url.netloc
            and parsed_url.path
        )

    return False


def _get_bucket_and_key_from_S3_url(s3_url: str) -> Tuple[str, str]:
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.hostname.split(".")[0]
    relative_path = parsed_url.path

    if not relative_path:
        print(f"[red]Cannot extract S3 key from invalid URL '{s3_url}'[/red]")
        exit()

    # Remove a slash from the beginning of the path
    s3_key = relative_path[1:]
    return bucket_name, s3_key


def get_file_urls_from_s3_storage(s3_url: str) -> List[str]:
    urls = []

    base_url = "{0.scheme}://{0.netloc}/".format(urlparse(s3_url))
    bucket, s3_path = _get_bucket_and_key_from_S3_url(s3_url)

    s3 = boto3.resource("s3")
    my_bucket = s3.Bucket(bucket)

    for object_summary in my_bucket.objects.filter(Prefix=s3_path):
        file_s3_key: str = object_summary.key
        filename = os.path.basename(file_s3_key)
        is_file = bool(filename)
        if is_file:
            urls.append(urljoin(base_url, file_s3_key))

    return urls


def get_s3_presigned_url(s3_url: str, expires_in_mins: int = S3_URL_EXPIRATION_MINUTES) -> str:
    """Generate expiring URL to access protected content"""

    def boto_action():
        expires_in_secs = expires_in_mins * 60
        return s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_key,
                **aws_params,
            },
            ExpiresIn=expires_in_secs,
        )

    bucket_name, s3_key = _get_bucket_and_key_from_S3_url(s3_url)

    # If we don't set a Content-Type for a presigned URL,
    # browser cannot even embed PDF files correctly in iframes or separate tab.
    # We need to specify the exact Content-Type
    # for all file types we use at least in private buckets
    aws_params = {}
    extension = get_file_ext(s3_key)

    content_type = CONTENTTYPE_BY_EXTENSION.get(extension)

    if extension and content_type:
        aws_params["ResponseContentType"] = content_type

    error_message = f"Could not make presigned URL for key '{s3_key}'"
    presigned_url = _run_and_handle_boto_errors(boto_action, error_message)

    return presigned_url
