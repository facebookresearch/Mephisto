#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from . import status


class ProlificException(Exception):
    """Main Prolific exception. All other exceptions should be inherited from it"""

    default_message: str = "Prolific error"

    def __init__(self, message: Optional[str] = None):
        self.message = message or self.default_message


class ProlificAPIKeyError(ProlificException):
    default_message = "API key is missing."


class ProlificRequestError(ProlificException):
    default_message = "Request error."
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: Optional[str] = None, status_code: Optional[int] = None):
        self.message = message or self.default_message
        self.status_code = status_code or self.status_code


class ProlificAuthenticationError(ProlificRequestError):
    default_message = "Authentication was failed."
    status_code = status.HTTP_401_UNAUTHORIZED
