#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional, Dict, Any
import time

PACKET_TYPE_ALIVE = "alive"
PACKET_TYPE_SUBMIT_ONBOARDING = "submit_onboarding"
PACKET_TYPE_SUBMIT_UNIT = "submit_unit"
PACKET_TYPE_SUBMIT_METADATA = "submit_metadata"
PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE = "client_bound_live_update"
PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE = "mephisto_bound_live_update"
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
        client_timestamp: Optional[float] = None,
        router_incoming_timestamp: Optional[float] = None,
        router_outgoing_timestamp: Optional[float] = None,
        server_timestamp: Optional[float] = None,
    ):
        self.type = packet_type
        self.subject_id = subject_id
        self.data = {} if data is None else data
        if server_timestamp is None:
            server_timestamp = time.time()
        self.server_timestamp = server_timestamp
        self.client_timestamp = client_timestamp
        self.router_incoming_timestamp = router_incoming_timestamp
        self.router_outgoing_timestamp = router_outgoing_timestamp

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
            client_timestamp=input_dict.get("client_timestamp"),
            router_incoming_timestamp=input_dict.get("router_incoming_timestamp"),
            router_outgoing_timestamp=input_dict.get("router_outgoing_timestamp"),
            server_timestamp=input_dict.get("server_timestamp"),
        )

    def to_sendable_dict(self) -> Dict[str, Any]:
        return {
            "packet_type": self.type,
            "subject_id": self.subject_id,
            "data": self.data,
            "client_timestamp": self.client_timestamp,
            "router_incoming_timestamp": self.router_incoming_timestamp,
            "router_outgoing_timestamp": self.router_outgoing_timestamp,
            "server_timestamp": self.server_timestamp,
        }

    def copy(self):
        return Packet.from_dict(self.to_sendable_dict())

    def __str__(self) -> str:
        return str(self.to_sendable_dict())
