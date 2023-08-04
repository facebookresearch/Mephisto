#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict
from typing import List

from .base_model import BaseModel


class ParticipantGroup(BaseModel):
    """
    More about Participant Groups:
        https://docs.prolific.co/docs/api-docs/public/#tag/Participant-Groups
    """

    id: str
    name: str
    project_id: str
    participant_count: int
    feeder_studies: List[Dict]

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "project_id": {"type": "string"},
            "name": {"type": "string"},
            "participant_count": {"type": "number"},
            "feeder_studies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "internal_name": {"type": "string"},
                        "status": {"type": "string"},
                        "completion_codes": {"type": "array"},
                    },
                },
            },
        },
    }

    required_schema_fields = [
        "project_id",
        "name",
    ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id} {self.name}"
