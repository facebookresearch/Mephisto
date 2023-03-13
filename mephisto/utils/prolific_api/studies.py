#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_api_resource import BaseAPIResource
from .data_models import Study


class Studies(BaseAPIResource):
    list_api_endpoint = 'studies'
    retrieve_api_endpoint = 'studies/{id}'
    delete_api_endpoint = 'studies/{id}'

    @classmethod
    def list(cls):
        response_json = cls.get(cls.list_api_endpoint)
        projects = [Study(**s) for s in response_json]
        return projects

    @classmethod
    def retrieve(cls, id: str):
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return Study(**response_json)

    @classmethod
    def create(cls, **data):
        study = Study(**data)
        response_json = cls.post(cls.list_api_endpoint, params=study.to_dict())
        return Study(**response_json)

    @classmethod
    def remove(cls, id: str):
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        return cls.delete(endpoint)
