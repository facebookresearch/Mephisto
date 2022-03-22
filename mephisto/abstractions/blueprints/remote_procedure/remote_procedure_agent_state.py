#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState
import os
import json
import time
import weakref
from uuid import uuid4
from dataclasses import dataclass, fields

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.packet import Packet


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

    def __init__(self, agent: "Agent"):
        """
        Create an agent state that keeps track of incoming actions from the frontend client
        Initialize with an existing file if it exists.
        """
        self.agent = weakref.proxy(agent)
        data_file = self._get_expected_data_file()
        if os.path.exists(data_file):
            self.load_data()
        else:
            self.requests: Dict[str, RemoteRequest] = {}
            self.start_time = time.time()
            self.end_time = -1
            self.init_data: Optional[Dict[str, Any]] = None
            self.final_submission: Optional[Dict[str, Any]] = None
            self.save_data()

    def set_init_state(self, data: Any) -> bool:
        """Set the initial state for this agent"""
        if self.init_data is not None:
            # Initial state is already set
            return False
        else:
            self.init_data = data
            self.save_data()
            return True

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
        return {"task_data": self.init_data, "previous_requests": prev_requests}

    def _get_expected_data_file(self) -> str:
        """Return the place we would expect to find data for this agent state"""
        agent_dir = self.agent.get_data_dir()
        os.makedirs(agent_dir, exist_ok=True)
        return os.path.join(agent_dir, "state.json")

    def load_data(self) -> None:
        """Load stored data from a file to this object"""
        agent_file = self._get_expected_data_file()
        with open(agent_file, "r") as state_json:
            state = json.load(state_json)
            self.requests = {x["uuid"]: x for x in state["requests"]}
            self.init_data = state["init_data"]
            self.outputs = state["final_submission"]

    def get_data(self) -> Dict[str, Any]:
        """Return dict with the messages of this agent"""
        return {
            "final_submission": self.final_submission,
            "init_data": self.init_data,
            "requests": [r.to_dict() for r in self.requests.values()],
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def get_parsed_data(self) -> Dict[str, Any]:
        """Return the formatted content"""
        # TODO implement actually getting this data
        return self.get_data()

    def get_task_start(self) -> float:
        """
        Return the start time for this task
        """
        return self.start_time

    def get_task_end(self) -> float:
        """
        Return the end time for this task
        """
        return self.end_time

    def save_data(self) -> None:
        """Save all messages from this agent to"""
        agent_file = self._get_expected_data_file()
        with open(agent_file, "w+") as state_json:
            json.dump(self.get_data(), state_json)

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

    def update_submit(self, submitted_data: Dict[str, Any]) -> None:
        """Append any final submission to this state"""
        self.final_submission = submitted_data
        self.save_data()
