#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.core.utils import get_crowd_provider_from_type, get_task_runner_from_type

from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent


# TODO what is the best method for creating new ones of these for different task types
# in ways that are supported by different backends? Perhaps abstract additional
# methods into the required db interface? Move any file manipulations into a
# extra_data_handler subcomponent of the MephistoDB class?
# Can handle doing this split after getting the first round of tests done because
# otherwise it's a lot of written but untestable code.
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
    STATUS_PARTNER_DISCONNECT = "partner disconnect"
    STATUS_EXPIRED = "expired"
    STATUS_RETURNED = "returned"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

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

    def __new__(cls, agent: "Agent") -> "AgentState":
        """
        The new method is overridden to be able to automatically generate
        the expected Requester class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Requester
        as you will instead be returned the correct Requester class according to
        the crowdprovider associated with this Requester.
        """
        if cls == AgentState:
            # We are trying to construct an AgentState, find what type to use and
            # create that instead
            correct_class = get_task_runner_from_type(agent.task_type).AgentStateClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    @abstractmethod
    def load_data(self) -> None:
        """
        Load stored data from a file to this object
        """
        raise NotImplementedError()

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Return the currently stored data for this task in the dict format
        expected by any frontend displays
        """
        raise NotImplementedError()

    @abstractmethod
    def save_data(self) -> None:
        """
        Save the relevant data from this Unit to a file in the expected location
        """
        raise NotImplementedError()

    @abstractmethod
    def update_data(self, *args) -> None:
        """
        Put new current Unit data into this AgentState
        """
        # TODO maybe refine the signature for this function once use cases
        # are fully scoped

        # Some use cases might just be appending new data, some
        # might instead prefer to maintain a final state.

        # Maybe the correct storage is of a series of actions taken
        # on this Unit? Static tasks only have 2 turns max, dynamic
        # ones may have multiple turns or steps.
        raise NotImplementedError()

    @staticmethod
    def valid() -> List[str]:
        """Return all valid Agent statuses"""
        # TODO write a test that ensures all AgentState statuses are here
        return [
            AgentState.STATUS_NONE,
            AgentState.STATUS_ONBOARDING,
            AgentState.STATUS_WAITING,
            AgentState.STATUS_IN_TASK,
            AgentState.STATUS_COMPLETED,
            AgentState.STATUS_DISCONNECT,
            AgentState.STATUS_PARTNER_DISCONNECT,
            AgentState.STATUS_EXPIRED,
            AgentState.STATUS_RETURNED,
        ]
