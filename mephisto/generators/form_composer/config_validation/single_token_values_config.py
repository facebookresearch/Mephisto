from typing import Dict
from typing import List
from typing import Tuple

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError

from .utils import get_file_urls_from_s3_storage
from .utils import write_config_to_file


def validate_single_token_values_config(
    config_json: Dict[str, List[str]],
) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_json, dict):
        is_valid = False
        errors.append("Config must be a key/value JSON Object.")
        return is_valid, errors

    for i, token_values in enumerate(config_json.items()):
        token, values = token_values

        if not values:
            is_valid = False
            errors.append(
                f"You passed empty array of values for token '{token}'. "
                f"It must contain at least one value or just remove it you left it by mistake."
            )

    return is_valid, errors


def update_single_token_values_config_with_file_urls(
    url: str, single_token_values_config_path: str,
):
    try:
        files_locations = get_file_urls_from_s3_storage(url)
    except (BotoCoreError, ClientError, NoCredentialsError) as e:
        print(f"Could not retrieve files from S3 URL '{url}'. Reason: {e}")
        return None

    if not files_locations:
        print(
            f"Could not retrieve files from '{url}' - "
            f"check if this location exists and contains files"
        )
        return None

    single_token_values_config_data = {
        "file_location": files_locations,
    }
    write_config_to_file(single_token_values_config_data, single_token_values_config_path)
