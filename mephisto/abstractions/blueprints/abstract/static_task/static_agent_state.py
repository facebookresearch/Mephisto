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

from mephisto.utils.logger_core import get_logger

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

    def update_data(self, live_update: Dict[str, Any]) -> None:
        """
        Process the incoming data packet, and handle updating the state
        """
        raise Exception("Static tasks should only have final act, but got live update")

    def update_submit(self, submission_data: Dict[str, Any]) -> None:
        """Move the submitted output to the local dict"""
        outputs: Dict[str, Any]
        output_files = submission_data.get("files")
        if output_files is not None:
            submission_data["files"] = [f["filename"] for f in submission_data["files"]]
        self.state["outputs"] = submission_data
        times_dict = self.state["times"]
        assert isinstance(times_dict, dict)
        times_dict["task_end"] = time.time()
        self.save_data()

    def get_task_start(self) -> Optional[float]:
        """
        Extract out and return the start time recorded for this task.
        """
        stored_times = self.state["times"]
        assert stored_times is not None
        return stored_times["task_start"]

    def get_task_end(self) -> Optional[float]:
        """
        Extract out and return the end time recorded for this task.
        """
        stored_times = self.state["times"]
        assert stored_times is not None
        return stored_times["task_end"]
