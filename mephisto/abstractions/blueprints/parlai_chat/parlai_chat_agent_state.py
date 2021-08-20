#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.packet import (
    PACKET_TYPE_AGENT_ACTION,
    PACKET_TYPE_UPDATE_AGENT_STATUS,
)
import os
import json
import time
import weakref

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.packet import Packet


class ParlAIChatAgentState(AgentState):
    """
    Holds information about ParlAI-style chat. Data is stored in json files
    containing every act from the ParlAI world.
    """

    def __init__(self, agent: "Agent"):
        """
        Create an AgentState to track the state of an agent's work on a Unit

        Initialize with an existing file if it exists.
        """
        self.agent = weakref.proxy(agent)
        data_file = self._get_expected_data_file()
        if os.path.exists(data_file):
            self.load_data()
        else:
            self.messages: List[Dict[str, Any]] = []
            self.init_data = None
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
        return {"task_data": self.init_data, "raw_messages": self.messages}

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
            self.messages = state["outputs"]["messages"]
            self.init_data = state["inputs"]

    def get_data(self) -> Dict[str, Any]:
        """Return dict with the messages of this agent"""
        return {"outputs": {"messages": self.messages}, "inputs": self.init_data}

    def get_parsed_data(self) -> Dict[str, Any]:
        """Return the formatted input, conversations, and final data"""
        init_data = self.init_data
        save_data = None
        messages = [
            m["data"]
            for m in self.messages
            if m["packet_type"] == PACKET_TYPE_AGENT_ACTION
        ]
        agent_name = None
        if len(messages) > 0:
            for m in self.messages:
                if m["packet_type"] == PACKET_TYPE_UPDATE_AGENT_STATUS:
                    if "agent_display_name" in m["data"]["state"]:
                        agent_name = m["data"]["state"]["agent_display_name"]
                        break
            if "MEPHISTO_is_submit" in messages[-1]:
                messages = messages[:-1]
            if "WORLD_DATA" in messages[-1]:
                save_data = messages[-1]["WORLD_DATA"]
                messages = messages[:-1]
        return {
            "agent_name": agent_name,
            "initial_data": init_data,
            "messages": messages,
            "save_data": save_data,
        }

    def save_data(self) -> None:
        """Save all messages from this agent to"""
        agent_file = self._get_expected_data_file()
        with open(agent_file, "w+") as state_json:
            json.dump(self.get_data(), state_json)

    def update_data(self, packet: "Packet") -> None:
        """
        Append the incoming packet as well as who it came from
        """
        message_data = packet.to_sendable_dict()
        message_data["timestamp"] = time.time()
        self.messages.append(message_data)
        self.save_data()
