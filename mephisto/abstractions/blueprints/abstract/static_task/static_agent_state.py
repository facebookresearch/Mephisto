#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Dict, Optional, Any, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState
import os
import json
import time
import weakref

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.packet import Packet

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)

DATA_FILE = "agent_data.json"


class StaticAgentState(AgentState):
    """
    Agent state for static tasks.
    """

    def _get_empty_state(self) -> Dict[str, Optional[Dict[str, Any]]]:
        return {
            "inputs": None,
            "outputs": None,
            "times": {"task_start": 0, "task_end": 0},
        }

    def __init__(self, agent: "Agent"):
        """
        Static agent states should store
        input dict -> output dict pairs to disc
        """
        self.agent = weakref.proxy(agent)
        self.state: Dict[str, Optional[Dict[str, Any]]] = self._get_empty_state()
        self.load_data()

    def set_init_state(self, data: Any) -> bool:
        """Set the initial state for this agent"""
        if self.get_init_state() is not None:
            # Initial state is already set
            return False
        else:
            self.state["inputs"] = data
            times_dict = self.state["times"]
            # TODO(#103) this typing may be better handled another way
            assert isinstance(times_dict, dict)
            times_dict["task_start"] = time.time()
            self.save_data()
            return True

    def get_init_state(self) -> Optional[Dict[str, Any]]:
        """
        Return the initial state for this agent,
        None if no such state exists
        """
        if self.state["inputs"] is None:
            return None
        return self.state["inputs"].copy()

    def load_data(self) -> None:
        """Load data for this agent from disk"""
        data_dir = self.agent.get_data_dir()
        data_path = os.path.join(data_dir, DATA_FILE)
        if os.path.exists(data_path):
            with open(data_path, "r") as data_file:
                self.state = json.load(data_file)
        else:
            self.state = self._get_empty_state()

    def get_data(self) -> Dict[str, Any]:
        """Return dict of this agent's state"""
        return self.state.copy()

    def save_data(self) -> None:
        """Save static agent data to disk"""
        data_dir = self.agent.get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        out_filename = os.path.join(data_dir, DATA_FILE)
        with open(out_filename, "w+") as data_file:
            json.dump(self.state, data_file)
        logger.info(f"SAVED_DATA_TO_DISC at {out_filename}")

    def update_data(self, packet: "Packet") -> None:
        """
        Process the incoming data packet, and handle
        updating the state
        """
        assert (
            packet.data.get("MEPHISTO_is_submit") is True
            or packet.data.get("onboarding_data") is not None
        ), "Static tasks should only have final act"

        outputs: Dict[str, Any]

        if packet.data.get("onboarding_data") is not None:
            outputs = packet.data["onboarding_data"]
        else:
            outputs = packet.data["task_data"]
        times_dict = self.state["times"]
        # TODO(#013) this typing may be better handled another way
        assert isinstance(times_dict, dict)
        times_dict["task_end"] = time.time()
        if packet.data.get("files") != None:
            logger.info(f"Got files: {str(packet.data['files'])[:500]}")
            outputs["files"] = [f["filename"] for f in packet.data["files"]]
        self.state["outputs"] = outputs
        self.save_data()
