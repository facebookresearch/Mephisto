#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from .base_api_resource import BaseAPIResource
from .data_models import Submission


class Submissions(BaseAPIResource):
    list_api_endpoint = 'submissions/'
    retrieve_api_endpoint = 'submissions/{id}/'

    @classmethod
    def list(cls, study_id: Optional[str] = None) -> List[Submission]:
        endpoint = cls.list_api_endpoint
        if study_id:
            endpoint = f'{endpoint}?study={study_id}'
        response_json = cls.get(endpoint)
        submissions = [Submission(**s) for s in response_json['results']]
        return submissions

    @classmethod
    def retrieve(cls, id: str) -> Submission:
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return Submission(**response_json)
