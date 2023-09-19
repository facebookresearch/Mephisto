#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from jsonschema import validate


class BaseModel:
    id: str

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
        },
    }

    required_schema_fields = []
    id_field_name = "id"

    def __init__(self, **data):
        self.__dict__ = data

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {getattr(self, "id", "")}'

    def __repr__(self) -> str:
        return f"<{self.__str__()}>"

    def validate(self, check_required_fields: bool = True):
        schema = dict(self.schema)

        if check_required_fields:
            schema["required"] = self.required_schema_fields

        validate(instance=self.__dict__, schema=schema)

    def to_dict(self) -> dict:
        return self.__dict__
