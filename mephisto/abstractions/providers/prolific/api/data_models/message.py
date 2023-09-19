#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from .base_model import BaseModel


class Message(BaseModel):
    """
    More about Messages:
        https://docs.prolific.co/docs/api-docs/public/#tag/Messages
    """

    body: str
    channel_id: Optional[str]
    recipient_id: str
    sender_id: str
    sent_at: str
    type: str

    schema = {
        "type": "object",
        "properties": {
            "body": {"type": "string"},
            "channel_id": {"type": ["string", "null"]},
            "recipient_id": {"type": "string"},
            "sender_id": {"type": "string"},
            "sent_at": {"type": "string"},
            "type": {"type": "string"},
        },
    }

    required_schema_fields = [
        "body",
        "recipient_id",
        "study_id",
    ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.sender_id}: {self.body}"
