#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from . import constants
from .base_api_resource import BaseAPIResource
from .data_models import Submission


class Submissions(BaseAPIResource):
    list_api_endpoint = 'submissions/'
    retrieve_api_endpoint = 'submissions/{id}/'
    change_status_api_endpoint = 'submissions/{id}/transition/'

    @classmethod
    def list(cls, study_id: Optional[str] = None) -> List[Submission]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Submissions/paths/~1api~1v1~1submissions~1/get
        """
        endpoint = cls.list_api_endpoint
        if study_id:
            endpoint = f'{endpoint}?study={study_id}'
        response_json = cls.get(endpoint)
        submissions = [Submission(**s) for s in response_json['results']]
        return submissions

    @classmethod
    def retrieve(cls, id: str) -> Submission:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Submissions/paths/~1api~1v1~1submissions~1%7Bid%7D~1/get
        """
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return Submission(**response_json)

    @classmethod
    def _change_status(cls, id: str, action: str) -> Submission:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Submissions/paths/~1api~1v1~1submissions~1%7Bid%7D~1transition~1/post
        """
        params = dict(
            action=action,
        )
        endpoint = cls.change_status_api_endpoint.format(id=id)
        response_json = cls.post(endpoint, params=params)
        return Submission(**response_json)

    @classmethod
    def approve(cls, id: str) -> Submission:
        """API docs for this endpoint: see `Submissions.change_status`"""
        return cls._change_status(id, action=constants.SubmissionStatus.APPROVED)

    @classmethod
    def reject(cls, id: str) -> Submission:
        """API docs for this endpoint: see `Submissions.change_status`"""
        return cls._change_status(id, action=constants.SubmissionStatus.REJECTED)
