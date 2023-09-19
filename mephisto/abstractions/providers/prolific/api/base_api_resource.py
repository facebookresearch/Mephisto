#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import requests

from mephisto.utils.logger_core import get_logger
from . import status
from .exceptions import ProlificAPIKeyError
from .exceptions import ProlificAuthenticationError
from .exceptions import ProlificException
from .exceptions import ProlificRequestError

BASE_URL = os.environ.get("PROLIFIC_BASE_URL", "https://api.prolific.co/api/v1/")
CREDENTIALS_CONFIG_DIR = "~/.prolific/"
CREDENTIALS_CONFIG_PATH = os.path.join(CREDENTIALS_CONFIG_DIR, "credentials")

logger = get_logger(name=__name__)


def get_prolific_api_key() -> Union[str, None]:
    credentials_path = os.path.expanduser(CREDENTIALS_CONFIG_PATH)
    prolific_user = os.environ.get("PROLIFIC_API_USER", "")
    if os.path.exists(credentials_path):
        with open(credentials_path, "r") as f:
            all_keys = json.load(f)
            api_key = all_keys.get(prolific_user, None)
            return api_key
    return None


PROLIFIC_API_KEY = os.environ.get("PROLIFIC_API_KEY", "") or get_prolific_api_key()


class HTTPMethod:
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class BaseAPIResource(object):
    def __init__(self, id=None):
        self.id = id

    @classmethod
    def _base_request(
        cls,
        method: str,
        api_endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        api_key: Optional[str] = None,
    ) -> Union[dict, str, None]:
        log_prefix = f"[{cls.__name__}]"

        api_key = api_key or PROLIFIC_API_KEY
        if not api_key:
            raise ProlificAPIKeyError

        try:
            url = urljoin(BASE_URL, api_endpoint)

            headers = headers or {}
            headers.update(
                {
                    "Authorization": f"Token {api_key}",
                }
            )

            logger.debug(f"{log_prefix} {method} {url}. Params: {params}")

            if method == HTTPMethod.GET:
                response = requests.get(url, headers=headers, json=params)

            elif method == HTTPMethod.POST:
                response = requests.post(url, headers=headers, json=params)

            elif method == HTTPMethod.PATCH:
                response = requests.patch(url, headers=headers, json=params)

            elif method == HTTPMethod.DELETE:
                response = requests.delete(url, headers=headers, json=params)

            else:
                raise ProlificException("Invalid HTTP method.")

            response.raise_for_status()
            if response.status_code == status.HTTP_204_NO_CONTENT and not response.content:
                result = None
            else:
                result = response.json()

            logger.debug(f"{log_prefix} Response: {result}")

            return result

        except ProlificException:
            # Reraise these errors further to avoid catching them in the latest `except` condition
            raise

        except requests.exceptions.HTTPError as err:
            logger.error(f"{log_prefix} Request error: {err}. Response text: `{err.response.text}`")
            if err.response.status_code == status.HTTP_401_UNAUTHORIZED:
                raise ProlificAuthenticationError

            message = err.args[0]
            message = f"{message}. {err.response.text}"
            raise ProlificRequestError(message, status_code=err.response.status_code)

        except Exception:
            logger.exception(f"{log_prefix} Unexpected error")
            raise ProlificException

    @classmethod
    def get(cls, api_endpoint: str, params: Optional[dict] = None) -> dict:
        method = HTTPMethod.GET
        return cls._base_request(method, api_endpoint, params=params)

    @classmethod
    def post(cls, api_endpoint: str, params: Optional[dict] = None) -> dict:
        method = HTTPMethod.POST
        return cls._base_request(method, api_endpoint, params=params)

    @classmethod
    def patch(cls, api_endpoint: str, params: Optional[dict] = None) -> dict:
        method = HTTPMethod.PATCH
        return cls._base_request(method, api_endpoint, params=params)

    @classmethod
    def delete(cls, api_endpoint: str, params: Optional[dict] = None) -> dict:
        method = HTTPMethod.DELETE
        return cls._base_request(method, api_endpoint, params=params)
