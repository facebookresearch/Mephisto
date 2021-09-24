#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
This file contains the various datatypes that are used on the operations layer
to facilitate executing task runs.
"""

from dataclasses import dataclass
from typing import Dict, Set, Optional, List, Any, Union, TYPE_CHECKING
import threading

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import TaskRunner, Blueprint
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.abstractions.architect import Architect
    from mephisto.operations.task_launcher import TaskLauncher
    from mephisto.abstractions.channel import Channel
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from mephisto.operations.client_io_handler import ClientIOHandler


@dataclass
class LiveTaskRun:
    task_run: "TaskRun"
    # Core abstraction instances
    architect: "Architect"
    blueprint: "Blueprint"
    provider: "CrowdProvider"
    # Live job operations and state
    qualifications: List[Dict[str, Any]]
    task_runner: "TaskRunner"
    task_launcher: "TaskLauncher"

    client_io: "ClientIOHandler"

    # Temporary until IO handler is written
    channel_ids: List[str]


@dataclass
class ChannelInfo:
    channel_id: str
    live_run: "LiveTaskRun"
    channel: "Channel"


@dataclass
class AgentInfo:
    agent: Union["Agent", "OnboardingAgent"]
    used_channel_id: str
    assignment_thread: Optional[threading.Thread] = None
