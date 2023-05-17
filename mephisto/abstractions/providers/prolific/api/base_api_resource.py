#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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

BASE_URL = os.environ.get('PROLIFIC_BASE_URL', 'https://api.prolific.co/api/v1/')
CREDENTIALS_CONFIG_DIR = '~/.prolific/'
CREDENTIALS_CONFIG_PATH = os.path.join(CREDENTIALS_CONFIG_DIR, 'credentials')

logger = get_logger(name=__name__)


def get_prolific_api_key() -> Union[str, None]:
    credentials_path = os.path.expanduser(CREDENTIALS_CONFIG_PATH)
    if os.path.exists(credentials_path):
        with open(credentials_path, 'r') as f:
            api_key = f.read().strip()
            return api_key
    return None


API_KEY = os.environ.get('PROLIFIC_API_KEY', '') or get_prolific_api_key()


class HTTPMethod:
    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'


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
    ) -> Union[dict, str]:
        log_prefix = f'[{cls.__name__}]'

        if API_KEY is None:
            raise ProlificAPIKeyError

        try:
            url = urljoin(BASE_URL, api_endpoint)

            headers = headers or {}
            headers.update({
                'Authorization': f'Token {API_KEY}',
            })

            logger.debug(f'{log_prefix} {method} {url}. Params: {params}')

            if method == HTTPMethod.GET:
                response = requests.get(url, headers=headers, json=params)

            elif method == HTTPMethod.POST:
                response = requests.post(url, headers=headers, json=params)

            elif method == HTTPMethod.PATCH:
                response = requests.patch(url, headers=headers, json=params)

            elif method == HTTPMethod.DELETE:
                response = requests.delete(url, headers=headers)

            else:
                raise ProlificException('Invalid HTTP method.')

            response.raise_for_status()
            json = response.json()
            logger.debug(f'{log_prefix} Response: {json}')
            return json

        except requests.exceptions.HTTPError as err:
            logger.error(f'{log_prefix} Request error: {str(err)}')
            if err.response.status_code == status.HTTP_401_UNAUTHORIZED:
                raise ProlificAuthenticationError

            message = err.args[0]
            message = f'{message}. {err.response.text}'
            raise ProlificRequestError(message, status_code=err.response.status_code)

        except Exception:
            logger.exception(f'{log_prefix} Unexpected error')
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
