#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional, Dict, Any, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState
import os
import time
from uuid import uuid4
from dataclasses import dataclass, fields


@dataclass
class RemoteRequest:
    uuid: str
    target: str
    args_json: Optional[str]
    response_json: Optional[str]
    timestamp: float

    def to_dict(self):
        return dict((field.name, getattr(self, field.name)) for field in fields(self))


class RemoteProcedureAgentState(AgentState):
    """
    Holds information about tasks with live interactions in a remote query model.
    """

    def _set_init_state(self, data: Any):
        """Set the initial state for this agent"""
        self.init_data: Optional[Dict[str, Any]] = data

    def get_init_state(self) -> Optional[Dict[str, Any]]:
        """
        Return the initial state for this agent,
        None if no such state exists
        """
        if self.init_data is None:
            return None
        prev_requests = []
        if len(self.requests) > 0:
            requests = self.requests.values()
            sorted_requests = sorted(requests, key=lambda x: x.timestamp)
            prev_requests = [r.to_dict() for r in sorted_requests]
        return {
            "task_data": self.init_data,
            "previous_requests": prev_requests,
        }

    def _get_expected_data_file(self) -> str:
        """Return the place we would expect to find data for this agent state"""
        agent_dir = self.agent.get_data_dir()
        os.makedirs(agent_dir, exist_ok=True)
        return os.path.join(agent_dir, "state.json")

    def _load_data(self) -> None:
        """Load stored data from a file to this object"""
        self.requests: Dict[str, RemoteRequest] = {}
        self.init_data = None
        self.final_submission: Optional[Dict[str, Any]] = None
        agent_file = self._get_expected_data_file()
        if self.agent.db.key_exists(agent_file):
            state = self.agent.db.read_dict(agent_file)
            self.requests = {x["uuid"]: RemoteRequest(**x) for x in state["requests"]}
            self.init_data = state["init_data"]
            self.final_submission = state["final_submission"]
            # Backwards compatibility for times
            if "start_time" in state:
                self.metadata.task_start = state["start_time"]
                self.metadata.task_end = state["end_time"]

    def get_data(self) -> Dict[str, Any]:
        """Return dict with the messages of this agent"""
        return {
            "final_submission": self.final_submission,
            "init_data": self.init_data,
            "requests": [r.to_dict() for r in self.requests.values()],
            "start_time": self.metadata.task_start,
            "end_time": self.metadata.task_end,
        }

    def get_parsed_data(self) -> Dict[str, Any]:
        """Return the formatted content"""
        # TODO implement actually getting this data
        return self.get_data()

    def _save_data(self) -> None:
        """Save all messages from this agent to"""
        agent_file = self._get_expected_data_file()
        self.agent.db.write_dict(agent_file, self.get_data())

    def update_data(self, live_update: Dict[str, Any]) -> None:
        """
        Append the incoming packet as well as who it came from
        """
        if "handles" in live_update:
            # outgoing
            response_id = str(uuid4())
            response = RemoteRequest(
                uuid=response_id,
                target=live_update["handles"],
                args_json=None,
                response_json=live_update["response"],
                timestamp=time.time(),
            )
            self.requests[response_id] = response
        else:
            # incoming
            request = RemoteRequest(
                uuid=live_update["request_id"],
                target=live_update["target"],
                args_json=live_update["args"],
                response_json=None,
                timestamp=time.time(),
            )
            self.requests[live_update["request_id"]] = request

    def _update_submit(self, submitted_data: Dict[str, Any]) -> None:
        """Append any final submission to this state"""
        self.final_submission = submitted_data
