#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskRunner
from mephisto.data_model.agent import Agent, OnboardingAgent
import time

try:
    from parlai.core.agents import Agent as ParlAIAgent
    from parlai.core.message import Message
except:

    class ParlAIAgent:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(
                "You need to install ParlAI to use this blueprint"
            )

    class Message:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(
                "You need to install ParlAI to use this blueprint"
            )

    pass  # ParlAI is not installed. TODO remove when we move this blueprint to ParlAI

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
from uuid import uuid4

from typing import ClassVar, List, Type, Any, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import AgentState
    from mephisto.data_model.assignment import Assignment


class MephistoAgentWrapper(ParlAIAgent):
    """
    Class that wraps a mephisto agent to be used as an
    agent in ParlAI worlds
    """

    def __init__(self, agent: Union[Agent, OnboardingAgent]):
        self.mephisto_agent = agent
        self.__agent_id = "unnamed agent"
        self.__mephisto_agent_id = agent.get_agent_id()

    @property
    def id(self):
        """Alias for agent_id"""
        return self.__agent_id

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
            receiver_id=self.__mephisto_agent_id,
            data={"state": {"agent_display_name": new_agent_id}},
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
        return Message(parsed_act)

    def observe(self, act):
        """
        ParlAI Agents observe a dict, we must convert these to  packets?
        """
        if act.get("message_id") is None:
            act["message_id"] = str(uuid4())
        packaged_act = Packet(
            packet_type=PACKET_TYPE_AGENT_ACTION,
            sender_id="mephisto",
            receiver_id=self.__mephisto_agent_id,
            data=act,
        )
        self.mephisto_agent.observe(packaged_act)


class ParlAIChatTaskRunner(TaskRunner):
    """
    Task runner for a parlai chat task
    """

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        if shared_state.world_module is None:
            world_file_path = os.path.expanduser(args.blueprint.world_file)
            world_module_dir = os.path.dirname(world_file_path)
            sys.path.append(world_module_dir)
            world_module_name = os.path.basename(world_file_path)[:-3]
            world_module = import_module(world_module_name)
        else:
            world_module = shared_state.world_module
        self.parlai_world_module = world_module
        world_params = self.parlai_world_module.get_world_params()
        self.is_concurrent = world_params["agent_count"] > 1
        self.id_to_worlds: Dict[str, Any] = {}

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

    def get_world_id(self, world_type: str, extra_id: str) -> str:
        """Get a world id specific to the given world type"""
        return f"{world_type}-{extra_id}"

    def run_onboarding(self, agent: "OnboardingAgent") -> None:
        """
        ParlAI Onboarding will initialize an onboarding
        world, then run it to completion if possible
        """
        opt: Dict[str, Any] = self.shared_state.onboarding_world_opt
        parlai_agent = MephistoAgentWrapper(agent)
        try:
            world = self.parlai_world_module.make_onboarding_world(
                opt,
                parlai_agent,
                initialization_data=self.get_init_data_for_agent(agent),
            )  # type: ignore
        except TypeError:
            # make_world doesn't ask for initialization_data
            world = self.parlai_world_module.make_onboarding_world(opt, parlai_agent)  # type: ignore

        world_id = self.get_world_id("onboard", agent.get_agent_id())
        self.id_to_worlds[world_id] = world
        while (
            not world.episode_done()
            and agent.get_agent_id() in self.running_onboardings
        ):
            world.parley()
        world.shutdown()
        if hasattr(world, "prep_save_data"):
            agent.observe(
                Packet(
                    packet_type=PACKET_TYPE_AGENT_ACTION,
                    sender_id="mephisto",
                    receiver_id=agent.db_id,
                    data={
                        "id": "SUBMIT_WORLD_DATA",
                        "WORLD_DATA": world.prep_save_data([parlai_agent]),
                        "text": "",
                    },
                )
            )
        # Mark the agent as done, then wait for the incoming submit action
        agent.mark_done()
        while not agent.has_action.is_set():
            done_act = agent.act()
            if done_act is not None:
                break
            time.sleep(0.3)

    def cleanup_onboarding(self, agent: "OnboardingAgent") -> None:
        """Shutdown the world"""
        onboarding_id = agent.get_agent_id()
        world_id = self.get_world_id("onboard", onboarding_id)
        # Only shut down world if it was actually started
        if world_id in self.id_to_worlds:
            self.id_to_worlds[world_id].shutdown()
            del self.id_to_worlds[world_id]

    def run_assignment(self, assignment: "Assignment", agents: List["Agent"]) -> None:
        """
        ParlAI runners will initialize a task world, then run them to completion
        if possible
        """
        for agent in agents:
            assert agent is not None, "task was not fully assigned"
        opt: Dict[str, Any] = self.shared_state.world_opt
        parlai_agents = [MephistoAgentWrapper(a) for a in agents]
        try:
            world = self.parlai_world_module.make_world(
                opt, parlai_agents, initialization_data=assignment.get_assignment_data()
            )  # type: ignore
        except TypeError:
            # make_world doesn't ask for initialization_data
            world = self.parlai_world_module.make_world(opt, parlai_agents)  # type: ignore

        world_id = self.get_world_id("assignment", assignment.db_id)
        self.id_to_worlds[world_id] = world
        while not world.episode_done() and assignment.db_id in self.running_assignments:
            world.parley()

        # TODO(WISH) it would be nice to have individual agents be able to submit their
        # final things without needing to wait for their partner, such
        # as if one needs to rate and the other doesn't

        world.shutdown()
        if hasattr(world, "prep_save_data"):
            for idx in range(len(parlai_agents)):
                agents[idx].observe(
                    Packet(
                        packet_type=PACKET_TYPE_AGENT_ACTION,
                        sender_id="mephisto",
                        receiver_id=agents[idx].db_id,
                        data={
                            "id": "SUBMIT_WORLD_DATA",
                            "WORLD_DATA": world.prep_save_data([parlai_agents[idx]]),
                            "text": "",
                        },
                    )
                )

    def cleanup_assignment(self, assignment: "Assignment") -> None:
        """Handle cleanup for a specific assignment"""
        world_id = self.get_world_id("assignment", assignment.db_id)
        self.id_to_worlds[world_id].shutdown()
        del self.id_to_worlds[world_id]

    def run_unit(self, unit: "Unit", agent: "Agent") -> None:
        """
        ParlAI runners will initialize a task world, then run them to completion
        if possible
        """
        agents = [agent]
        opt: Dict[str, Any] = self.shared_state.world_opt
        parlai_agents = [MephistoAgentWrapper(a) for a in agents]
        try:
            world = self.parlai_world_module.make_world(
                opt, parlai_agents, initialization_data=unit.get_assignment_data()
            )  # type: ignore
        except TypeError:
            # make_world doesn't ask for initialization_data
            world = self.parlai_world_module.make_world(opt, parlai_agents)  # type: ignore

        world_id = self.get_world_id("unit", unit.db_id)
        self.id_to_worlds[world_id] = world
        while not world.episode_done() and unit.db_id in self.running_units:
            world.parley()

        # TODO(WISH) it would be nice to have individual agents be able to submit their
        # final things without needing to wait for their partner, such
        # as if one needs to rate and the other doesn't

        world.shutdown()
        if hasattr(world, "prep_save_data"):
            agent.observe(
                Packet(
                    packet_type=PACKET_TYPE_AGENT_ACTION,
                    sender_id="mephisto",
                    receiver_id=agent.db_id,
                    data={
                        "id": "SUBMIT_WORLD_DATA",
                        "WORLD_DATA": world.prep_save_data(parlai_agents),
                        "text": "",
                    },
                )
            )

    def cleanup_unit(self, unit: "Unit") -> None:
        """Handle cleanup for a specific unit"""
        world_id = self.get_world_id("unit", unit.db_id)
        self.id_to_worlds[world_id].shutdown()
        del self.id_to_worlds[world_id]
