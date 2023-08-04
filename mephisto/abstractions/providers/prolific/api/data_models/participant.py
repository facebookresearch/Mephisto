#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_model import BaseModel


class Participant(BaseModel):
    participant_id: str
    datetime_created: str

    schema = {
        "type": "object",
        "properties": {
            "participant_id": {"type": "string"},
            "datetime_created": {"type": "string"},
        },
    }

    id_field_name = "participant_id"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.participant_id}"
