#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from mephisto.data_model.blueprint import AgentState
import os
import json

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
        self.agent = agent
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
        return {'task_data': self.init_data, 'raw_messages': self.messages}

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
            self.messages = state["messages"]
            self.init_data = state["init_data"]

    def get_data(self) -> Dict[str, Any]:
        """Return dict with the messages of this agent"""
        return {"outputs": self.messages, "inputs": self.init_data}

    def save_data(self) -> None:
        """Save all messages from this agent to """
        agent_file = self._get_expected_data_file()
        with open(agent_file, "w+") as state_json:
            json.dump(self.get_data(), state_json)

    def update_data(self, packet: "Packet") -> None:
        """
        Append the incoming packet as well as who it came from
        """
        self.messages.append(packet.to_sendable_dict())
        self.save_data()
