#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from typing import (
    Optional,
    List,
    Dict,
    Any,
    Type,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.packet import Packet

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


# TODO(#567) File manipulations should ultimately be handled by the MephistoDB, rather than
# direct reading and writing within. This allows for a better abstraction between
# the kind of data collected and how it is stored.
class AgentState(ABC):
    """
    Class for holding state information about work by an Agent on a Unit, currently
    stored as current task work into a json file.

    Specific state implementations will need to be created for different Task Types,
    as different tasks store and load differing data.
    """

    # Possible Agent Status Values
    STATUS_NONE = "none"
    STATUS_ACCEPTED = "accepted"
    STATUS_ONBOARDING = "onboarding"
    STATUS_WAITING = "waiting"
    STATUS_IN_TASK = "in task"
    STATUS_COMPLETED = "completed"
    STATUS_DISCONNECT = "disconnect"
    STATUS_TIMEOUT = "timeout"
    STATUS_PARTNER_DISCONNECT = "partner disconnect"
    STATUS_EXPIRED = "expired"
    STATUS_RETURNED = "returned"
    STATUS_APPROVED = "approved"
    STATUS_SOFT_REJECTED = "soft_rejected"
    STATUS_REJECTED = "rejected"

    def __new__(cls, agent: Union["Agent", "OnboardingAgent"]) -> "AgentState":
        """Return the correct agent state for the given agent"""
        if cls == AgentState:
            from mephisto.data_model.agent import Agent
            from mephisto.operations.registry import get_blueprint_from_type

            # We are trying to construct an AgentState, find what type to use and
            # create that instead
            if isinstance(agent, Agent):
                correct_class = get_blueprint_from_type(agent.task_type).AgentStateClass
            else:
                correct_class = get_blueprint_from_type(
                    agent.task_type
                ).OnboardingAgentStateClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    @staticmethod
    def complete() -> List[str]:
        """Return all final Agent statuses which will not be updated by the WorkerPool"""
        return [
            AgentState.STATUS_COMPLETED,
            AgentState.STATUS_DISCONNECT,
            AgentState.STATUS_TIMEOUT,
            AgentState.STATUS_EXPIRED,
            AgentState.STATUS_RETURNED,
            AgentState.STATUS_SOFT_REJECTED,
            AgentState.STATUS_APPROVED,
            AgentState.STATUS_REJECTED,
        ]

    @staticmethod
    def valid() -> List[str]:
        """Return all valid Agent statuses"""
        return [
            AgentState.STATUS_NONE,
            AgentState.STATUS_ACCEPTED,
            AgentState.STATUS_ONBOARDING,
            AgentState.STATUS_WAITING,
            AgentState.STATUS_IN_TASK,
            AgentState.STATUS_COMPLETED,
            AgentState.STATUS_DISCONNECT,
            AgentState.STATUS_TIMEOUT,
            AgentState.STATUS_PARTNER_DISCONNECT,
            AgentState.STATUS_EXPIRED,
            AgentState.STATUS_RETURNED,
            AgentState.STATUS_SOFT_REJECTED,
            AgentState.STATUS_APPROVED,
            AgentState.STATUS_REJECTED,
        ]

    # Implementations of an AgentState must implement the following:

    @abstractmethod
    def __init__(self, agent: "Agent"):
        """
        Create an AgentState to track the state of an agent's work on a Unit

        Implementations should initialize any required files for saving and
        loading state data somewhere.

        If said file already exists based on the given agent, load that data
        instead.
        """
        raise NotImplementedError()

    @abstractmethod
    def set_init_state(self, data: Any) -> bool:
        """Set the initial state for this agent"""
        raise NotImplementedError()

    @abstractmethod
    def get_init_state(self) -> Optional[Any]:
        """
        Return the initial state for this agent,
        None if no such state exists
        """
        raise NotImplementedError()

    @abstractmethod
    def load_data(self) -> None:
        """
        Load stored data from a file to this object
        """
        raise NotImplementedError()

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Return the currently stored data for this task in the format
        expected by any frontend displays
        """
        raise NotImplementedError()

    def get_parsed_data(self) -> Any:
        """
        Return the portion of the data that is relevant to a human
        who wants to parse or analyze the data

        Utility function to handle stripping the data of any
        context that is only important for reproducing the task
        exactly. By default is just `get_data`
        """
        return self.get_data()

    @abstractmethod
    def save_data(self) -> None:
        """
        Save the relevant data from this Unit to a file in the expected location
        """
        raise NotImplementedError()

    @abstractmethod
    def update_data(self, live_update: Dict[str, Any]) -> None:
        """
        Put new live update data into this AgentState. Keep only what is
        necessary to recreate the task for evaluation and later use.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_submit(self, submit_data: Dict[str, Any]) -> None:
        """
        Update this AgentState with the final submission data.
        """
        raise NotImplementedError()

    def get_task_start(self) -> Optional[float]:
        """
        Return the start time for this task, if it is available
        """
        return 0.0

    def get_task_end(self) -> Optional[float]:
        """
        Return the end time for this task, if it is available
        """
        return 0.0
