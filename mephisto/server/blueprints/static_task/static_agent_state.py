#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Dict, Optional, Any, TYPE_CHECKING
from mephisto.data_model.blueprint import AgentState
import os
import json

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.packet import Packet


DATA_FILE = "agent_data.json"


class StaticAgentState(AgentState):
    """
    Agent state for static tasks
    """

    # TODO implement. Going to get frontend working first

    def __init__(self, agent: "Agent"):
        """
        Static agent states should store
        input dict -> output dict pairs to disc
        """
        self.agent = agent
        self.state: List[Dict[str, Any]] = []
        self.load_data()

    def set_init_state(self, data: Any) -> bool:
        """Set the initial state for this agent"""
        if self.get_init_state() is not None:
            # Initial state is already set
            return False
        else:
            self.state.append(data)
            self.save_data()
            return True

    def get_init_state(self) -> Optional[Dict[str, Any]]:
        """
        Return the initial state for this agent,
        None if no such state exists
        """
        if len(self.state) == 0:
            return None
        else:
            return self.state[0]

    def load_data(self) -> None:
        """Load data for this agent from disk"""
        data_dir = self.agent.get_data_dir()
        data_path = os.path.join(data_dir, DATA_FILE)
        if os.path.exists(data_path):
            with open(data_path, "r") as data_file:
                self.state = json.load(data_file)
        else:
            self.state = []

    def get_data(self) -> List[Dict[str, Any]]:
        """Return dict of this agent's state"""
        return self.state

    def save_data(self) -> None:
        """Save static agent data to disk"""
        data_dir = self.agent.get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, DATA_FILE), "w+") as data_file:
            json.dump(self.state, data_file)
        print("SAVED_DATA_TO_DISC", self.state)

    def update_data(self, packet: "Packet") -> None:
        """
        Process the incoming data packet, and handle
        updating the state
        """
        assert (
            packet.data.get("MEPHISTO_is_submit") is True
        ), "Static tasks should only have final act"
        self.state.append(packet.data["task_data"])
        if packet.data.get("files") != None:
            print("Got files:", str(packet.data["files"])[:500])
        self.save_data()
