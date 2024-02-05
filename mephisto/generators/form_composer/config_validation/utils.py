import json
import os
from json import JSONDecodeError
from typing import List
from typing import Tuple
from typing import Union
from urllib.parse import urljoin
from urllib.parse import urlparse

import boto3

from mephisto.generators.form_composer.constants import JSON_IDENTATION


def write_config_to_file(config_data: Union[List[dict], dict], file_path: str):
    config_str = json.dumps(config_data, indent=JSON_IDENTATION)

    with open(file_path, "w") as f:
        f.write(config_str)


def is_s3_url(value: str) -> bool:
    if isinstance(value, str):
        parsed_url = urlparse(value)
        return bool(
            parsed_url.scheme == 'https' and
            "s3" in parsed_url.hostname and
            parsed_url.netloc and
            parsed_url.path
        )

    return False


def _get_bucket_and_key_from_S3_url(s3_url: str) -> Tuple[str, str]:
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.hostname.split('.')[0]
    relative_path = parsed_url.path

    if not relative_path:
        raise ValueError(f'Cannot extract S3 key from invalid URL "{s3_url}"')

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


def read_config_file(config_path: str) -> Union[List[dict], dict]:
    try:
        with open(config_path) as config_file:
            config_data = json.load(config_file)
    except (JSONDecodeError, TypeError, FileNotFoundError):
        print(f"Could not read JSON from '{config_path}' file")
        raise
    return config_data


def make_error_message(main_message: str, error_list: List[str]) -> str:
    errors_bullet = "\n  - " + "\n  - ".join(map(str, error_list))
    return f"{main_message}. Errors:{errors_bullet}"
