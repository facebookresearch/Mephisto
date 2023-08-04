#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional
import urllib.parse

from .base_api_resource import BaseAPIResource
from .data_models import Participant
from .data_models import ParticipantGroup


class ParticipantGroups(BaseAPIResource):
    list_api_endpoint = "participant-groups/"
    retrieve_api_endpoint = "participant-groups/{id}/"
    remove_api_endpoint = "participant-groups/{id}/"
    list_participants_for_group_api_endpoint = "participant-groups/{id}/participants/"

    @classmethod
    def list(
        cls,
        project_id: Optional[str] = None,
        is_active: bool = True,
    ) -> List[ParticipantGroup]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1/get
        """
        params = {}
        if project_id:
            params["project_id"] = project_id
        if is_active:
            params["is_active"] = is_active

        endpoint = cls.list_api_endpoint
        if params:
            endpoint += "?" + urllib.parse.urlencode(params)

        response_json = cls.get(endpoint)
        participant_groups = [ParticipantGroup(**s) for s in response_json["results"]]
        return participant_groups

    @classmethod
    def retrieve(cls, id: str) -> ParticipantGroup:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1%7Bid%7D~1/get
        """
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return ParticipantGroup(**response_json)

    @classmethod
    def create(cls, **data) -> ParticipantGroup:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1/post
        """
        participant_group = ParticipantGroup(**data)
        response_json = cls.post(cls.list_api_endpoint, params=participant_group.to_dict())
        return ParticipantGroup(**response_json)

    @classmethod
    def remove(cls, id: str) -> None:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1%7Bid%7D~1/delete
        """
        cls.delete(cls.remove_api_endpoint.format(id=id))
        return None

    @classmethod
    def list_participants_for_group(cls, id: str) -> List[Participant]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1%7Bid%7D~1participants~1/get
        """
        response_json = cls.get(cls.list_participants_for_group_api_endpoint.format(id=id))
        participants = [Participant(**s) for s in response_json["results"]]
        return participants

    @classmethod
    def add_participants_to_group(cls, id: str, participant_ids: List[str]) -> List[Participant]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1%7Bid%7D~1participants~1/post
        """
        endpoint = cls.list_participants_for_group_api_endpoint.format(id=id)
        params = dict(participant_ids=participant_ids)
        response_json = cls.post(endpoint, params=params)
        participants = [Participant(**s) for s in response_json["results"]]
        return participants

    @classmethod
    def remove_participants_from_group(
        cls,
        id: str,
        participant_ids: List[str],
    ) -> List[Participant]:
        """
        API docs for this endpoint:
        https://docs.prolific.co/docs/api-docs/public/#tag/
            Participant-Groups/paths/~1api~1v1~1participant-groups~1%7Bid%7D~1participants~1/delete
        """
        endpoint = cls.list_participants_for_group_api_endpoint.format(id=id)
        params = dict(participant_ids=participant_ids)
        response_json = cls.delete(endpoint, params=params)
        participants = [Participant(**s) for s in response_json["results"]]
        return participants
