#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# types of exceptions thrown when an agent exits the chat. These are thrown
# on a failed act call call. If one of these is thrown and not handled,
# the world should die and enter cleanup.
class AbsentAgentError(Exception):
    """Exceptions for when an agent leaves a task"""

    def __init__(self, message, agent_id):
        self.message = message
        self.agent_id = agent_id


class AgentDisconnectedError(AbsentAgentError):
    """Exception for a real disconnect event (no signal)"""

    def __init__(self, agent_id):
        super().__init__(f"Agent disconnected", agent_id)


class AgentTimeoutError(AbsentAgentError):
    """Exception for when a worker doesn't respond in time"""

    def __init__(self, timeout, agent_id):
        super().__init__(f"Agent exceeded {timeout}", agent_id)


class AgentReturnedError(AbsentAgentError):
    """Exception for an explicit return event (worker returns task)"""

    def __init__(self, agent_id):
        super().__init__(f"Agent returned task", agent_id)


class AgentShutdownError(AbsentAgentError):
    """Exception for when a task is shutdown but agents are still in a task"""

    def __init__(self, agent_id):
        super().__init__(f"This agent has been forced to shut down", agent_id)
