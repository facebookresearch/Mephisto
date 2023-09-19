#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from .base_model import BaseModel


class Submission(BaseModel):
    """
    More about Submissions:
        https://docs.prolific.co/docs/api-docs/public/#tag/Submissions
    """

    completed_at: str
    entered_code: str
    id: str
    participant: str
    started_at: str
    status: str
    study_id: str

    schema = {
        "type": "object",
        "properties": {
            "completed_at": {"type": "string"},
            "entered_code": {"type": "string"},
            "id": {"type": "string"},
            "participant": {"type": "string"},
            "started_at": {"type": "string"},
            "status": {"type": "string"},
            "study_id": {"type": "string"},
        },
    }

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id}"


class ListSubmission(BaseModel):
    """
    Somehow Prolific returns completely different fields for one object and list of objects

    More about Submissions:
        https://docs.prolific.co/docs/api-docs/public/#tag/Submissions
    """

    completed_at: str
    has_siblings: bool
    entered_code: str
    id: str
    ip: str
    is_complete: bool
    participant_id: str
    return_requested: Optional[str]
    reward: int
    started_at: str
    status: str
    strata: dict
    study_code: str
    time_taken: int

    schema = {
        "type": "object",
        "properties": {
            "completed_at": {"type": "string"},
            "has_siblings": {"type": "boolean"},
            "entered_code": {"type": "string"},
            "id": {"type": "string"},
            "ip": {"type": "string"},
            "is_complete": {"type": "boolean"},
            "participant_id": {"type": "string"},
            "return_requested": {"type": ["string", "null"]},
            "reward": {"type": "number"},
            "started_at": {"type": "string"},
            "status": {"type": "string"},
            "strata": {"type": "object"},
            "study_code": {"type": "string"},
            "time_taken": {"type": "number"},
        },
    }

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id}"
