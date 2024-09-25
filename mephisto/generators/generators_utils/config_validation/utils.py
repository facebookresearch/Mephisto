#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from importlib import import_module
from json import JSONDecodeError
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from urllib.parse import urljoin
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError
from botocore.exceptions import NoCredentialsError

from mephisto.generators.generators_utils.config_validation.config_validation_constants import (
    INSERTIONS_PATH_NAME,
)
from mephisto.generators.generators_utils.constants import CONTENTTYPE_BY_EXTENSION
from mephisto.generators.generators_utils.constants import JSON_IDENTATION
from mephisto.generators.generators_utils.constants import S3_URL_EXPIRATION_MINUTES
from mephisto.utils.console_writer import ConsoleWriter
from .config_validation_constants import CUSTOM_TRIGGERS_JS_FILE_NAME
from .config_validation_constants import CUSTOM_TRIGGERS_JS_FILE_NAME_ENV_KEY
from .config_validation_constants import CUSTOM_VALIDATORS_JS_FILE_NAME
from .config_validation_constants import CUSTOM_VALIDATORS_JS_FILE_NAME_ENV_KEY

logger = ConsoleWriter()
s3_client = boto3.client("s3")


def import_object_from_module(dot_path_to_object: str) -> Any:
    module_name, importing_object_name = dot_path_to_object.rsplit(".", 1)
    _importing_object = getattr(import_module(module_name), importing_object_name)
    return _importing_object


def import_paths_in_validation_mappings(validation_functions_mapping: dict) -> dict:
    validation_mappings = {}

    for validator_name, func_path in validation_functions_mapping.items():
        module_name, func_name = func_path.rsplit(".", 1)
        func = getattr(import_module(module_name), func_name)
        validation_mappings[validator_name] = func

    return validation_mappings


class ValidationMappingsImportError(Exception):
    pass


_validation_mappings_cache = {}


def get_validation_mappings() -> Union[dict, None]:
    # Use cache if it's already not empty
    env_use_cache = os.environ.get("VALIDATION_MAPPING_USE_CACHE") == "true"
    if env_use_cache and _validation_mappings_cache:
        return _validation_mappings_cache

    env_path = os.environ.get("VALIDATION_MAPPING", "")

    try:
        # Use specified mappings from environment variable
        validation_mapping_dict = import_object_from_module(env_path)
    except Exception:
        raise ValidationMappingsImportError(
            f"Environment variable VALIDATION_MAPPING was not found: {env_path}"
        )

    # Validate mappings
    if not isinstance(validation_mapping_dict, dict):
        raise ValidationMappingsImportError(
            "Imported VALIDATION_MAPPING has incorrect format. "
            "Please, fix is or remove setting evironment variable if you did this accidentally"
        )

    validation_mapping_ = import_paths_in_validation_mappings(validation_mapping_dict)
    _validation_mappings_cache.update(validation_mapping_)
    return _validation_mappings_cache


def write_config_to_file(config_data: Union[List[dict], dict], file_path: str):
    config_str = json.dumps(config_data, indent=JSON_IDENTATION)

    with open(file_path, "w") as f:
        f.write(config_str)


def read_config_file(
    config_path: str, exit_if_no_file: bool = True
) -> Union[List[dict], dict, None]:

    if not os.path.exists(config_path):
        if exit_if_no_file:
            logger.info(f"[red]Required file not found: '{config_path}'.[/red]")
            exit()

        logger.info(f"[yellow]Required file not found: '{config_path}'.[/yellow]")
        return None

    try:
        with open(config_path) as config_file:
            config_data = json.load(config_file)
    except (JSONDecodeError, TypeError) as e:
        logger.info(f"[red]Could not read JSON from file: '{config_path}': {e}.[/red]")
        exit()

    return config_data


# TODO: Move this function and its tests into `mephisto.utils`, as it is too useful for one app
def make_error_message(
    main_message: str,
    error_list: List[str],
    indent: int = 2,
    list_title: Optional[str] = "Errors",
) -> str:
    prefix = "\n" + (" " * indent) + "- "
    errors_bullets = prefix + prefix.join(map(str, error_list))
    error_title = f"{main_message.rstrip('.')}. {list_title}:" if main_message else ""
    return error_title + errors_bullets


def get_file_ext(file_name: str) -> str:
    """Cut off file extension without period"""
    return Path(file_name).suffix.lower()[1:]


def is_insertion_file(path: str, ext: str = "html") -> bool:
    if not isinstance(path, str):
        return False

    if f"{INSERTIONS_PATH_NAME}/" in path and path.endswith(f".{ext}"):
        return True

    return False


def _set_file_env_var(data_path: str, file_name: str, env_var_name: str):
    file_path = os.path.abspath(os.path.join(data_path, INSERTIONS_PATH_NAME, file_name))
    file_exists = os.path.exists(file_path)
    os.environ[env_var_name] = file_path if file_exists else ""


def set_custom_validators_js_env_var(data_path: str):
    _set_file_env_var(
        data_path=data_path,
        file_name=CUSTOM_VALIDATORS_JS_FILE_NAME,
        env_var_name=CUSTOM_VALIDATORS_JS_FILE_NAME_ENV_KEY,
    )


def set_custom_triggers_js_env_var(data_path: str):
    _set_file_env_var(
        data_path=data_path,
        file_name=CUSTOM_TRIGGERS_JS_FILE_NAME,
        env_var_name=CUSTOM_TRIGGERS_JS_FILE_NAME_ENV_KEY,
    )


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
        logger.info(f"[red]Cannot extract S3 key from invalid URL '{s3_url}'[/red]")
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
