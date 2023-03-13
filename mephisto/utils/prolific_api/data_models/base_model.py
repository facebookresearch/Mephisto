#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from jsonschema import validate


class BaseModel:
    id: str

    _schema = {
        'type' : 'object',
        'properties' : {
            'id' : {
                'type' : 'string',
            },
        },
    }

    def __init__(self, **data):
        validate(instance=data, schema=self._schema)
        self.__dict__ = data

    def to_dict(self) -> dict:
        return self.__dict__
