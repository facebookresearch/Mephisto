#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Dict, Any, TYPE_CHECKING
from mephisto.data_model.blueprint import AgentState
import os
import json

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent


class StaticAgentState(AgentState):
    """
    Agent state for static tasks
    """

    # TODO implement. Going to get frontend working first

    def __init__(self, agent: "Agent"):
        """Mock agent states keep everything in local memory"""
        self.agent = agent
        self.state: List[Dict[str, Any]] = []

    def load_data(self) -> None:
        """Load data for this agent from disk"""
        # TODO implement
        pass

    def get_data(self) -> List[Dict[str, Any]]:
        """Return dict of this agent's state"""
        return self.state

    def save_data(self) -> None:
        """Save static agent data to disk"""
        # TODO implement
        pass

    def update_data(self, packet) -> None:
        """Process the incoming data packet, and handle it"""
        self.state.append(packet)
