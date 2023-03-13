#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_model import BaseModel


class User(BaseModel):
    id: str
    email: str

    _schema = {
        'type' : 'object',
        'properties' : {
            'id' : {
                'type' : 'string',
            },
            'email' : {
                'type' : 'string',
                'pattern': '^\\S+@\\S+\\.\\S+$',  # Simple checking
            },
        },
    }
