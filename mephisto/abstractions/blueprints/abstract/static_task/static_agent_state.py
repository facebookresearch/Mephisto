#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState
import os.path

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
        }

    def _set_init_state(self, data: Any):
        """Set the initial state for this agent"""
        self.state["inputs"] = data

    def get_init_state(self) -> Optional[Dict[str, Any]]:

        """
        Return the initial state for this agent,
        None if no such state exists
        """
        if self.state["inputs"] is None:
            return None
        return self.state["inputs"].copy()

    def _load_data(self) -> None:
        """Load data for this agent from disk"""
        data_dir = self.agent.get_data_dir()
        data_path = os.path.join(data_dir, DATA_FILE)
        if self.agent.db.key_exists(data_path):
            self.state = self.agent.db.read_dict(data_path)
            # Old compatibility with saved times
            if "times" in self.state:
                assert isinstance(self.state["times"], dict)
                self.metadata.task_start = self.state["times"]["task_start"]
                self.metadata.task_end = self.state["times"]["task_end"]
        else:
            self.state = self._get_empty_state()

    def get_data(self) -> Dict[str, Any]:
        """Return dict of this agent's state"""
        return self.state.copy()

    def _save_data(self) -> None:
        """Save static agent data to disk"""
        data_dir = self.agent.get_data_dir()
        out_filename = os.path.join(data_dir, DATA_FILE)
        self.agent.db.write_dict(out_filename, self.state)
        logger.info(f"SAVED_DATA_TO_DISC at {out_filename}")

    def update_data(self, live_update: Dict[str, Any]) -> None:
        """
        Process the incoming data packet, and handle updating the state
        """
        raise Exception("Static tasks should only have final act, but got live update")

    def _update_submit(self, submission_data: Dict[str, Any]) -> None:
        """Move the submitted output to the local dict"""
        outputs: Dict[str, Any]
        assert isinstance(submission_data, dict), (
            "Static tasks must get dict results. Ensure you are passing an object to "
            f"your frontend task's `handleSubmit` method. Got {submission_data}"
        )
        output_files = submission_data.get("files")
        if output_files is not None:
            submission_data["files"] = [f["filename"] for f in submission_data["files"]]
        self.state["outputs"] = submission_data
