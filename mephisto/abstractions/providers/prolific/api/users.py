#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_api_resource import BaseAPIResource
from .data_models import User


class Users(BaseAPIResource):
    me_api_endpoint = "users/me/"

    @classmethod
    def me(cls) -> User:
        endpoint = cls.me_api_endpoint
        response_json = cls.get(endpoint)
        return User(**response_json)
