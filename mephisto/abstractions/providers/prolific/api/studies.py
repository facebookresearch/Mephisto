#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Union

from .base_api_resource import BaseAPIResource
from .constants import StudyAction
from .data_models import Study


class Studies(BaseAPIResource):
    list_api_endpoint = "studies/"
    list_for_project_api_endpoint = "projects/{project_id}/studies/"
    retrieve_api_endpoint = "studies/{id}/"
    update_api_endpoint = "studies/{id}/"
    remove_api_endpoint = "studies/{id}/"
    publish_cost_api_endpoint = "studies/{id}/transition/"
    stop_cost_api_endpoint = "studies/{id}/transition/"
    calculate_cost_api_endpoint = "study-cost-calculator/"

    @classmethod
    def list(cls) -> List[Study]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/Studies/paths/~1api~1v1~1studies~1/get
        """
        response_json = cls.get(cls.list_api_endpoint)
        studies = [Study(**s) for s in response_json["results"]]
        return studies

    @classmethod
    def list_for_project(cls, project_id: str) -> List[Study]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1projects~1%7Bproject_id%7D~1studies~1/get
        """
        endpoint = cls.list_for_project_api_endpoint.format(project_id=project_id)
        response_json = cls.get(endpoint)
        studies = [Study(**s) for s in response_json["results"]]
        return studies

    @classmethod
    def retrieve(cls, id: str) -> Study:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1studies~1%7Bid%7D~1/get
        """
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return Study(**response_json)

    @classmethod
    def create(cls, **data) -> Study:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/Studies/paths/~1api~1v1~1studies~1/post
        """
        study = Study(**data)
        study.validate()
        response_json = cls.post(cls.list_api_endpoint, params=study.to_dict())
        return Study(**response_json)

    @classmethod
    def update(cls, id: str, **data) -> Study:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1studies~1%7Bid%7D~1/patch
        """
        study = Study(**data)
        study.validate(check_required_fields=False)
        response_json = cls.patch(cls.update_api_endpoint.format(id=id), params=study.to_dict())
        return Study(**response_json)

    @classmethod
    def remove(cls, id: str) -> None:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1studies~1%7Bid%7D~1/delete
        """
        cls.delete(cls.remove_api_endpoint.format(id=id))
        return None

    @classmethod
    def publish(cls, id: str) -> Study:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1studies~1%7Bid%7D~1transition~1/post
        """
        params = dict(
            action=StudyAction.PUBLISH,
        )
        response_json = cls.post(cls.publish_cost_api_endpoint.format(id=id), params=params)
        return Study(**response_json)

    @classmethod
    def stop(cls, id: str) -> Study:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1studies~1%7Bid%7D~1transition~1/post
        """
        params = dict(
            action=StudyAction.STOP,
        )
        response_json = cls.post(cls.stop_cost_api_endpoint.format(id=id), params=params)
        return Study(**response_json)

    @classmethod
    def calculate_cost(
        cls,
        reward: Union[int, float],
        total_available_places: int,
    ) -> Union[int, float]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Studies/paths/~1api~1v1~1study-cost-calculator~1/post
        """
        params = dict(
            reward=reward,
            total_available_places=total_available_places,
        )
        response_json = cls.post(cls.calculate_cost_api_endpoint, params=params)
        return response_json["total_cost"]
