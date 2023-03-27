#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from .base_api_resource import BaseAPIResource
from .data_models import Participant
from .data_models import ParticipantGroup


class ParticipantGroups(BaseAPIResource):
    list_api_endpoint = 'participant-groups/'
    list_perticipants_for_group_api_endpoint = 'participant-groups/{id}/participants/'

    @classmethod
    def list(cls, project_id: Optional[str] = None) -> List[ParticipantGroup]:
        endpoint = cls.list_api_endpoint
        if project_id:
            endpoint = f'{endpoint}?project_id={project_id}'

        response_json = cls.get(endpoint)
        participant_groups = [ParticipantGroup(**s) for s in response_json['results']]
        return participant_groups

    @classmethod
    def create(cls, **data) -> ParticipantGroup:
        participant_group = ParticipantGroup(**data)
        response_json = cls.post(cls.list_api_endpoint, params=participant_group.to_dict())
        return ParticipantGroup(**response_json)

    @classmethod
    def list_perticipants_for_group(cls, id: str) -> List[Participant]:
        response_json = cls.get(cls.list_perticipants_for_group_api_endpoint.format(id=id))
        participants = [Participant(**s) for s in response_json['results']]
        return participants
