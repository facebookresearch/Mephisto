#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from .base_model import BaseModel


class EligibilityRequirement(BaseModel):
    """
    More about Eligibility Requirements:
        https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    _cls: str
    attributes: List[dict]
    category: str
    details_display: str
    id: str
    order: int
    query: dict
    recommended: bool
    requirement_type: str
    subcategory: Optional[str]
    type: str

    schema = {
        "type": "object",
        "properties": {
            "_cls": {"type": "string"},
            "attributes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "number"},
                        "label": {"type": "string"},
                        "name": {"type": "string"},
                        "value": {"type": "boolean"},
                    },
                },
            },
            "category": {"type": "string"},
            "details_display": {"type": "string"},
            "id": {"type": "string"},
            "order": {"type": "number"},
            "query": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "help_text": {"type": "string"},
                    "id": {"type": "string"},
                    "is_new": {"type": "boolean"},
                    "participant_help_text": {"type": "string"},
                    "question": {"type": "string"},
                    "researcher_help_text": {"type": "string"},
                    "tags": {"type": "array"},
                    "title": {"type": "string"},
                },
            },
            "recommended": {"type": "boolean"},
            "requirement_type": {"type": "string"},
            "subcategory": {"type": ["string", "null"]},
            "type": {"type": "string"},
        },
    }

    def __init__(self, **data):
        super().__init__(**data)
        setattr(self, "id", data.get("query", {}).get("id"))

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self._cls} {self.id}"
