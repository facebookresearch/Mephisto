#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from decimal import Decimal
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from .base_model import BaseModel
from .user import User


class Project(BaseModel):
    """
    More about Projects:
        https://docs.prolific.co/docs/api-docs/public/#tag/Projects
    """

    id: str
    title: str
    description: str
    owner: str
    users: List[Dict]
    studies: List[Dict]
    workspace: str
    naivety_distribution_rate: Optional[Union[Decimal, float]]

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "owner": {"type": "string"},
            "users": {
                "type": "array",
                "items": User.relation_user_schema,
            },
            "studies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                    },
                },
            },
            "workspace": {"type": "string"},
            "naivety_distribution_rate": {"type": ["number", "null"]},
        },
    }

    required_schema_fields = [
        "title",
    ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id} {self.title}"
