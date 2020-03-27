#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.blueprint import TaskRunner
from mephisto.data_model.agent import Agent
from parlai.core.agents import Agent as ParlAIAgent

from mephisto.data_model.packet import (
    Packet,
    PACKET_TYPE_AGENT_ACTION,
    PACKET_TYPE_UPDATE_AGENT_STATUS,
)

from importlib import import_module

import os
import sh
import shlex
import shutil
import subprocess
import sys

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.blueprint import AgentState
    from mephsito.data_model.assignment import Assignment


class MephistoAgentWrapper(ParlAIAgent):
    """
    Class that wraps a mephisto agent to be used as an 
    agent in ParlAI worlds
    """

    def __init__(self, agent: Agent):
        self.mephisto_agent = agent
        self.__agent_id = "unnamed agent"

    @property
    def agent_id(self):
        """
        Agent IDs in ParlAI are used to identify the speaker,
        and often are a label like "teacher"
        """
        return self.__agent_id

    @agent_id.setter
    def agent_id(self, new_agent_id: str):
        """
        We want to be able to display these labels to the 
        frontend users, so when these are updated by a 
        world we forward that to the frontend
        """
        packaged_act = Packet(
            packet_type=PACKET_TYPE_UPDATE_AGENT_STATUS,
            sender_id="mephisto",
            receiver_id=self.mephisto_agent.db_id,
            data={"agent_display_name": new_agent_id},
        )
        self.mephisto_agent.observe(packaged_act)
        self.__agent_id = new_agent_id

    def act(self, timeout=None):
        """
        ParlAI Agents send an act dict, we must convert this
        """
        if timeout is None:
            gotten_act = self.mephisto_agent.act()
        else:
            gotten_act = self.mephisto_agent.act(timeout=timeout)
        if gotten_act is None:
            return None
        parsed_act = gotten_act.data
        parsed_act["id"] = self.__agent_id
        return parsed_act

    def observe(self, act):
        """
        ParlAI Agents observe a dict, we must convert these to  packets?
        """
        packaged_act = Packet(
            packet_type=PACKET_TYPE_AGENT_ACTION,
            sender_id="mephisto",
            receiver_id=self.mephisto_agent.db_id,
            data=act,
        )
        self.mephisto_agent.observe(packaged_act)


class ParlAIChatTaskRunner(TaskRunner):
    """
    Task runner for a parlai chat task
    """

    def __init__(self, task_run: "TaskRun", opts: Any):
        super().__init__(task_run, opts)
        world_file_path = os.path.expanduser(self.opts["world_file"])
        world_file_path = os.path.expanduser(self.opts["world_file"])
        world_module_path = world_file_path[:-3]
        sys.path.append(world_module_path)
        world_module_name = os.path.basename(world_file_path)[:-3]
        self.parlai_world_module = import_module(world_module_name)
        self.is_concurrent = True

    # TODO reconnects should get the same agent as was initially given

    def get_init_data_for_agent(self, agent: "Agent") -> Dict[str, Any]:
        """
        Return the data for an agent already assigned to a particular unit
        """
        init_state = agent.state.get_init_state()
        if init_state is not None:
            # reconnecting agent, give what we've got
            return init_state
        else:
            assignment = agent.get_unit().get_assignment()
            assignment_data = self.get_data_for_assignment(assignment)
            agent.state.set_init_state(assignment_data.shared)
            new_state = agent.state.get_init_state()
            assert new_state is not None, "Recently initialized state still None"
            return new_state

    def run_assignment(self, assignment: "Assignment", agents: List["Agent"]) -> None:
        """
        Static runners will get the task data, send it to the user, then
        wait for the agent to act (the data to be completed)
        """
        for agent in agents:
            assert agent is not None, "task was not fully assigned"
        opt: Dict[str, Any] = self.opts.get('world_opt', {})
        parlai_agents = [MephistoAgentWrapper(a) for a in agents]
        world = self.parlai_world_module.make_world(opt, parlai_agents)  # type: ignore
        while not world.episode_done() and assignment.db_id in self.running_assignments:
            world.parley()

        # TODO it would be nice to have individual agents be able to submit their
        # final things without needing to wait for their partner, such
        # as if one needs to rate and the other doesn't

        world.shutdown()

    def cleanup_assignment(self, assignment: "Assignment") -> None:
        """Handle cleanup for a specific assignment"""
        pass  # TODO perhaps we need to requeue or do something additional?
