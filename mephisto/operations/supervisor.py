#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import threading
import time
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import worker_is_qualified
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.abstractions.blueprints.mixins.use_gold_unit import UseGoldUnit
from mephisto.operations.registry import get_crowd_provider_from_type
from mephisto.operations.task_launcher import (
    TaskLauncher,
    SCREENING_UNIT_INDEX,
    GOLD_UNIT_INDEX,
)
from mephisto.operations.datatypes import LiveTaskRun, ChannelInfo, AgentInfo
from mephisto.abstractions.channel import Channel, STATUS_CHECK_TIME

from typing import Dict, Set, Optional, List, Any, Union, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import TaskRunner

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)

# This class manages communications between the server
# and workers, ensures that their status is properly tracked,
# and also provides some helping utility functions for
# groups of workers or worker/agent compatibility.

# Mostly, the supervisor oversees the communications
# between LiveTaskRuns and workers over the channels


class Supervisor:
    def __init__(self, db: "MephistoDB"):
        self.db = db
        self.live_runs: Dict[str, "LiveTaskRun"] = {}
        self.is_shutdown = False

    def register_run(self, live_run: "LiveTaskRun") -> "LiveTaskRun":
        """Register the channels for a LiveTaskRun with this supervisor"""
        task_run = live_run.task_run
        self.live_runs[task_run.db_id] = live_run
        live_run.client_io.launch_channels(live_run, self)
        return live_run

    def shutdown(self) -> None:
        """Close all of the channels, join threads"""
        # Prepopulate agents and channels to close, as
        # these may change during iteration
        # Closing IO handling state
        self.is_shutdown = True
        runs_to_close = list(self.live_runs.keys())
        logger.debug(f"Ending runs {runs_to_close}")
        # TODO runs are started in operator, and should be closed there
        for run_id in runs_to_close:
            self.live_runs[run_id].task_runner.shutdown()
            self.live_runs[run_id].client_io.shutdown()
            self.live_runs[run_id].worker_pool.shutdown()

    def agent_info_to_live_run(self, agent_info: AgentInfo) -> LiveTaskRun:
        """Temporary helper to extract the live run for an agent info"""
        # This should be replaced by having the separate agents aware of the
        # live run they belong to
        task_run = agent_info.agent.get_task_run()
        return self.live_runs[task_run.db_id]
