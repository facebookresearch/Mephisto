#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional, Dict, Any

PACKET_TYPE_INIT_DATA = "initial_data_send"
PACKET_TYPE_AGENT_ACTION = "agent_action"
PACKET_TYPE_REQUEST_ACTION = "request_act"
PACKET_TYPE_UPDATE_AGENT_STATUS = "update_status"
PACKET_TYPE_NEW_AGENT = "register_agent"
PACKET_TYPE_NEW_WORKER = "register_worker"
PACKET_TYPE_REQUEST_AGENT_STATUS = "request_status"
PACKET_TYPE_RETURN_AGENT_STATUS = "return_status"
PACKET_TYPE_GET_INIT_DATA = "init_data_request"
PACKET_TYPE_ALIVE = "alive"
PACKET_TYPE_PROVIDER_DETAILS = "provider_details"
PACKET_TYPE_SUBMIT_ONBOARDING = "submit_onboarding"
PACKET_TYPE_ERROR_LOG = "log_error"


class Packet:
    """
    Simple class for encapsulating messages as sent between the
    Mephisto python client, the router, and any frontend.

    Used to be able to make assertions about the kind of data
    being sent for specific message types.
    """

    def __init__(
        self,
        packet_type: str,
        sender_id: str,
        receiver_id: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.type = packet_type
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.data = {} if data is None else data
        # TODO(#97) Packet validation! Only certain packets can be sent
        # with no data

    @staticmethod
    def from_dict(input_dict: Dict[str, Any]) -> "Packet":
        required_fields = ["packet_type", "sender_id", "receiver_id", "data"]
        for field in required_fields:
            assert (
                field in input_dict
            ), f"Packet input dict {input_dict} missing required field {field}"
        return Packet(
            packet_type=input_dict["packet_type"],
            sender_id=input_dict["sender_id"],
            receiver_id=input_dict["receiver_id"],
            data=input_dict["data"],
        )

    def to_sendable_dict(self) -> Dict[str, Any]:
        return {
            "packet_type": self.type,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "data": self.data,
        }

    def copy(self):
        return Packet.from_dict(self.to_sendable_dict())

    def __str__(self) -> str:
        return str(self.to_sendable_dict())
