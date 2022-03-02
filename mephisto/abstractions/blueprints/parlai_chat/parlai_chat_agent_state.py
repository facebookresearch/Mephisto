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
            self.final_submission: Optional[Dict[str, Any]] = None
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
        return {"task_data": self.init_data, "past_live_updates": self.messages}

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
            self.final_submission = state["outputs"].get("final_submission")

    def get_data(self) -> Dict[str, Any]:
        """Return dict with the messages of this agent"""
        return {
            "outputs": {
                "messages": self.messages,
                "final_submission": self.final_submission,
            },
            "inputs": self.init_data,
        }

    def get_parsed_data(self) -> Dict[str, Any]:
        """Return properly parsed data from this task"""
        init_data = self.init_data
        save_data = None

        agent_name = None
        for m in self.messages:
            if "agent_display_name" in m["task_data"]:
                agent_name = m["task_data"]["agent_display_name"]
                break

        messages = self.messages
        if len(messages) > 0:
            if "WORLD_DATA" in messages[-1]:
                save_data = messages[-1]["WORLD_DATA"]
                messages = messages[:-1]

        return {
            "agent_name": agent_name,
            "initial_data": init_data,
            "messages": messages,
            "save_data": save_data,
            "final_submission": self.final_submission,
        }

    def get_task_start(self) -> float:
        """
        Return the start time for this task, the timestamp of the very first message.
        """
        return self.messages[0]["timestamp"]

    def get_task_end(self) -> float:
        """
        Return the end time for this task, the timestamp of the very final message.
        """
        return self.messages[-1]["timestamp"]

    def save_data(self) -> None:
        """Save all messages from this agent to"""
        agent_file = self._get_expected_data_file()
        with open(agent_file, "w+") as state_json:
            json.dump(self.get_data(), state_json)

    def update_data(self, live_update: Dict[str, Any]) -> None:
        """
        Append the incoming packet as well as its arrival time
        """
        live_update["timestamp"] = time.time()
        self.messages.append(live_update)
        self.save_data()

    def update_submit(self, submitted_data: Dict[str, Any]) -> None:
        """Append any final submission to this state"""
        self.final_submission = submitted_data
        self.save_data()
