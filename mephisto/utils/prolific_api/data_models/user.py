#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_model import BaseModel
from ..constants import EMAIL_FORMAT


class User(BaseModel):
    id: str
    email: str

    schema = {
        'type' : 'object',
        'properties' : {
            'id' : {
                'type' : 'string',
            },
            'email' : {
                'type' : 'string',
                'pattern': EMAIL_FORMAT,
            },
        },
    }

    relation_user_schema = {
        'type': 'object',
        'properties': {
            'id': {
                'type': 'string',
            },
            'name': {
                'type': 'string',
            },
            'email': {
                'type': 'string',
                'pattern': EMAIL_FORMAT,
            },
            'roles': {
                'type': 'array',
            },
        },
        'required': [
            'id',
        ]
    }

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.id} {self.email}'
