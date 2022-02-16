#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskRunner, SharedTaskState
from mephisto.data_model.agent import Agent, OnboardingAgent
import time

try:
    from parlai.core.agents import Agent as ParlAIAgent  # type: ignore
    from parlai.core.message import Message  # type: ignore
except ImportError:
    from mephisto.abstractions.blueprints.parlai_chat.parlai_not_installed import ParlAIAgent, Message  # type: ignore

    pass  # ParlAI is not installed. TODO remove when we move this blueprint to ParlAI

from importlib import import_module

import os
import sh  # type: ignore
import shlex
import shutil
import subprocess
import sys
from mephisto.abstractions.blueprint import AgentState
from uuid import uuid4

from typing import ClassVar, List, Type, Any, Dict, Union, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
        SharedParlAITaskState,
    )
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.assignment import Assignment
    from mephisto.data_model.unit import Unit
    from omegaconf import DictConfig


class MephistoAgentWrapper(ParlAIAgent):
    """
    Class that wraps a mephisto agent to be used as an
    agent in ParlAI worlds
    """

    def __init__(self, agent: Union[Agent, OnboardingAgent]):
        self.mephisto_agent = agent
        self.__agent_id = "unnamed agent"
        self.__mephisto_agent_id = agent.get_agent_id()
        self.__act_requested = False

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
        self.mephisto_agent.observe(
            {"task_data": {"agent_display_name": new_agent_id}},
        )
        self.__agent_id = new_agent_id

    def act(self, timeout=None):
        """
        ParlAI Agents send an act dict, we must convert this
        """
        gotten_act = self.mephisto_agent.get_live_update()
        if gotten_act is None:
            # No act received, see that one is requested:
            if not self.__act_requested:
                self.mephisto_agent.observe(
                    {"task_data": {"live_update_requested": True}}
                )
                self.__act_requested = True
            if timeout is not None:
                gotten_act = self.mephisto_agent.get_live_update(timeout=timeout)
        if gotten_act is None:
            return None
        self.__act_requested = False
        gotten_act["id"] = self.__agent_id
        return Message(gotten_act)

    def observe(self, act):
        """We can simply add a message id if not already provided to these"""
        if act.get("update_id") is None:
            act["update_id"] = str(uuid4())
        self.mephisto_agent.observe(dict(act))


class ParlAIChatTaskRunner(TaskRunner):
    """
    Task runner for a parlai chat task
    """

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
            SharedParlAITaskState,
        )

        assert isinstance(
            shared_state, SharedParlAITaskState
        ), "Must use SharedParlAITaskState for parlai blueprints"
        if shared_state.world_module is None:
            world_file_path = os.path.expanduser(args.blueprint.world_file)
            world_module_dir = os.path.dirname(world_file_path)
            sys.path.append(world_module_dir)
            world_module_name = os.path.basename(world_file_path)[:-3]
            world_module = import_module(world_module_name)
        else:
            world_module = shared_state.world_module
        self.parlai_world_module = world_module
        world_params = world_module.get_world_params()  # type: ignore
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
        shared_state = self.shared_state
        from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
            SharedParlAITaskState,
        )

        assert isinstance(
            shared_state, SharedParlAITaskState
        ), "Must use SharedParlAITaskState for parlai blueprints"
        opt: Dict[str, Any] = shared_state.onboarding_world_opt
        parlai_agent = MephistoAgentWrapper(agent)
        try:
            world = self.parlai_world_module.make_onboarding_world(  # type: ignore
                opt,
                parlai_agent,
                initialization_data=shared_state.onboarding_data,
            )
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

        # Ensure agent can submit after onboarding
        agent.update_status(AgentState.STATUS_WAITING)

        world.shutdown()
        agent.state.update_data(
            {
                "id": "SUBMIT_WORLD_DATA",
                "WORLD_DATA": world.prep_save_data([parlai_agent]),
                "text": "",
            }
        )

        # Mark the agent as done, then wait for the incoming submit action
        while not agent.await_submit(timeout=None):
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
        opt: Dict[str, Any] = cast("SharedParlAITaskState", self.shared_state).world_opt
        parlai_agents = [MephistoAgentWrapper(a) for a in agents]
        try:
            world = self.parlai_world_module.make_world(  # type: ignore
                opt, parlai_agents, initialization_data=assignment.get_assignment_data()
            )
        except TypeError:
            # make_world doesn't ask for initialization_data
            world = self.parlai_world_module.make_world(opt, parlai_agents)  # type: ignore

        world_id = self.get_world_id("assignment", assignment.db_id)
        self.id_to_worlds[world_id] = world
        while not world.episode_done() and assignment.db_id in self.running_assignments:
            world.parley()

        # Ensure agents can submit after completion
        for idx in range(len(parlai_agents)):
            agents[idx].observe({"task_data": {"task_done": True}})

        # TODO(WISH) it would be nice to have individual agents be able to submit their
        # final things without needing to wait for their partner, such
        # as if one needs to rate and the other doesn't

        world.shutdown()
        for idx in range(len(parlai_agents)):
            agents[idx].state.update_data(
                {
                    "id": "SUBMIT_WORLD_DATA",
                    "WORLD_DATA": world.prep_save_data([parlai_agents[idx]]),
                    "text": "",
                }
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
        opt: Dict[str, Any] = cast("SharedParlAITaskState", self.shared_state).world_opt
        parlai_agents = [MephistoAgentWrapper(a) for a in agents]
        try:
            world = self.parlai_world_module.make_world(  # type: ignore
                opt, parlai_agents, initialization_data=unit.get_assignment_data()
            )
        except TypeError:
            # make_world doesn't ask for initialization_data
            world = self.parlai_world_module.make_world(opt, parlai_agents)  # type: ignore

        world_id = self.get_world_id("unit", unit.db_id)
        self.id_to_worlds[world_id] = world
        while not world.episode_done() and unit.db_id in self.running_units:
            world.parley()

        # Ensure agent can submit after completion
        agent.observe({"task_data": {"task_done": True}})

        world.shutdown()
        if hasattr(world, "prep_save_data"):
            agent.observe(
                {
                    "id": "SUBMIT_WORLD_DATA",
                    "WORLD_DATA": world.prep_save_data(parlai_agents),
                    "text": "",
                }
            )

    def cleanup_unit(self, unit: "Unit") -> None:
        """Handle cleanup for a specific unit"""
        world_id = self.get_world_id("unit", unit.db_id)
        self.id_to_worlds[world_id].shutdown()
        del self.id_to_worlds[world_id]
