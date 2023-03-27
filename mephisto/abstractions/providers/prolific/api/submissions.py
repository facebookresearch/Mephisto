#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_api_resource import BaseAPIResource
from .data_models import Submission


class Submissions(BaseAPIResource):
    list_api_endpoint = 'submissions/'
    retrieve_api_endpoint = 'submissions/{id}/'

    @classmethod
    def list(cls) -> List[Submission]:
        response_json = cls.get(cls.list_api_endpoint)
        submissions = [Submission(**s) for s in response_json['results']]
        return submissions

    @classmethod
    def retrieve(cls, id: str) -> Submission:
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return Submission(**response_json)
