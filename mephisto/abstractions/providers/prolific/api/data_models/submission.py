#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
        'type': 'object',
        'properties': {
            'completed_at': {'type': 'string'},
            'entered_code': {'type': 'string'},
            'id': {'type': 'string'},
            'participant': {'type': 'string'},
            'started_at': {'type': 'string'},
            'status': {'type': 'string'},
            'study_id': {'type': 'string'},
        },
    }

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.id}'
