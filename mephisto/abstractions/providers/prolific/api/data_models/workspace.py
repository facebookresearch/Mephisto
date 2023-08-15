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


class Workspace(BaseModel):
    """
    More about Workspaces:
        https://docs.prolific.co/docs/api-docs/public/#tag/Workspaces
    """

    description: str
    id: str
    naivety_distribution_rate: Optional[Union[Decimal, float]]
    owner: str
    projects: List[Dict]
    title: str
    users: List[Dict]
    wallet: str

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
            "projects": {
                "type": "array",
                "items": {
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
                        "naivety_distribution_rate": {"type": ["number", "null"]},
                    },
                },
            },
            "wallet": {"type": "string"},
            "naivety_distribution_rate": {"type": ["number", "null"]},
        },
    }

    required_schema_fields = [
        "title",
    ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id} {self.title}"
