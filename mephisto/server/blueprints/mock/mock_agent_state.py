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


class MockAgentState(AgentState):
    """
    Mock agent state that is to be used for testing
    """

    def __init__(self, agent: "Agent"):
        """Mock agent states keep everything in local memory"""
        self.agent = agent
        self.state: Dict[str, Any] = {}

    def load_data(self) -> None:
        """Mock agent states have no data stored"""
        pass

    def get_data(self) -> Dict[str, Any]:
        """Return dict of this agent's state"""
        return self.state

    def save_data(self) -> None:
        """Mock agents don't save data (yet)"""
        pass

    def update_data(self, state) -> None:
        """Put new data into this mock state"""
        # TODO this should actually take in packets instead
        # update once we use packets
        self.state = state
