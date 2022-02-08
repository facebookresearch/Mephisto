#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional, Dict, Any

PACKET_TYPE_ALIVE = "alive"
PACKET_TYPE_SUBMIT = "submit"
PACKET_TYPE_CLIENT_BOUND_LIVE_DATA = "client_bound_live_data"
PACKET_TYPE_MEPHISTO_BOUND_LIVE_DATA = "mephisto_bound_live_data"
PACKET_TYPE_REGISTER_AGENT = "register_agent"
PACKET_TYPE_AGENT_DETAILS = "agent_details"
PACKET_TYPE_UPDATE_STATUS = "update_status"
PACKET_TYPE_REQUEST_STATUSES = "request_statuses"
PACKET_TYPE_RETURN_STATUSES = "return_statuses"
PACKET_TYPE_ERROR = "log_error"


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
        subject_id: str,  # Target agent id the packet is about
        data: Optional[Dict[str, Any]] = None,
    ):
        self.type = packet_type
        self.subject_id = subject_id
        self.data = {} if data is None else data
        # TODO(#97) Packet validation! Only certain packets can be sent
        # with no data

    @staticmethod
    def from_dict(input_dict: Dict[str, Any]) -> "Packet":
        required_fields = ["packet_type", "subject_id", "data"]
        for field in required_fields:
            assert (
                field in input_dict
            ), f"Packet input dict {input_dict} missing required field {field}"
        return Packet(
            packet_type=input_dict["packet_type"],
            subject_id=input_dict["subject_id"],
            data=input_dict["data"],
        )

    def to_sendable_dict(self) -> Dict[str, Any]:
        return {
            "packet_type": self.type,
            "subject_id": self.subject_id,
            "data": self.data,
        }

    def copy(self):
        return Packet.from_dict(self.to_sendable_dict())

    def __str__(self) -> str:
        return str(self.to_sendable_dict())
