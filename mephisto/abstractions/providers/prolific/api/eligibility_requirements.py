#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_api_resource import BaseAPIResource
from .data_models import EligibilityRequirement


class EligibilityRequirements(BaseAPIResource):
    list_api_endpoint = "eligibility-requirements/"
    count_api_endpoint = "eligibility-count/"

    @classmethod
    def list(cls) -> List[EligibilityRequirement]:
        response_json = cls.get(cls.list_api_endpoint)
        eligibility_requirements = [EligibilityRequirement(**s) for s in response_json["results"]]
        return eligibility_requirements

    @classmethod
    def count_participants(cls) -> int:
        response_json = cls.post(cls.count_api_endpoint)
        return response_json["count"]
