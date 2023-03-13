#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_model import BaseModel


class ParticipantGroup(BaseModel):
    id: str

    _schema = {
        'type' : 'object',
        'properties' : {
            'id' : {
                'type' : 'string',
            },
        },
    }
