#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import datetime
from typing import List
from typing import Optional

from .base_api_resource import BaseAPIResource
from .data_models import Message


class Messages(BaseAPIResource):
    list_api_endpoint = "messages/"
    retrieve_api_endpoint = "messages/unread/"

    @classmethod
    def list(
        cls,
        user_id: Optional[str] = None,
        created_after: Optional[datetime] = None,
    ) -> List[Message]:
        """
        Get messages between you and another user or your messages with all users
        :param user_id: Another user ID, must be provided if no created_after date is provided
        :param created_after: Only fetch messages created after timestamp.
            Must be provided if no user_id is provided.
            You can only fetch up to the last 30 days of messages
        :return: List of Message objects
        """
        endpoint = cls.list_api_endpoint
        if user_id:
            endpoint += f"?user_id={user_id}"
        elif created_after:
            endpoint += f"?created_after={created_after.isoformat()}"

        response_json = cls.get(endpoint)
        messages = [Message(**s) for s in response_json["results"]]
        return messages

    @classmethod
    def list_unread(cls) -> List[Message]:
        """
        Get all unread messages.
        The messages you have sent are never returned, only messages you have received and not read.
        It does not mark those messages as read
        """
        response_json = cls.get(cls.list_api_endpoint)
        messages = [Message(**s) for s in response_json["results"]]
        return messages

    @classmethod
    def send(cls, **data) -> Message:
        """Send a message to a participant or another researcher"""
        message = Message(**data)
        message.validate()
        response_json = cls.post(cls.list_api_endpoint, params=message.to_dict())
        return Message(**response_json)
