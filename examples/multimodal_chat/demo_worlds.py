#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
from parlai.core.worlds import validate
from joblib import Parallel, delayed


class MTurkMultimodalOnboardWorld(MTurkOnboardWorld):
    def __init__(self, opt, mturk_agent):
        super().__init__(opt, mturk_agent)
        self.opt = opt

    def parley(self):
        self.mturk_agent.agent_id = "Onboarding Agent"
        self.mturk_agent.observe({"id": "System", "text": "Welcome onboard!"})
        x = self.mturk_agent.act(timeout=self.opt["turn_timeout"])
        self.mturk_agent.observe(
            {
                "id": "System",
                "text": "Thank you for your input! Please wait while "
                "we match you with another worker...",
                "episode_done": True,
            }
        )
        self.episodeDone = True


class MTurkMultimodalDialogWorld(MTurkTaskWorld):
    """
    Multimodal world where one agent gets control over a shared
    multimodal context that both agents can view.
    """

    def __init__(self, opt, agents=None, shared=None):
        # Add passed in agents directly.
        self.agents = agents
        self.acts = [None] * len(agents)
        self.episodeDone = False
        self.max_turns = opt.get("max_turns", 2)
        self.current_turns = 0
        self.send_task_data = opt.get("send_task_data", False)
        self.opt = opt
        self.actor_agent = agents[0]
        self.actor_agent.agent_id = "Actor"
        self.viewer_agent = agents[1]
        self.viewer_agent.agent_id = "Viewer"

    def parley(self):
        """
        For each agent, get an observation of the last action each of the other agents
        took.
        Then take an action yourself.
        """
        acts = self.acts
        if self.current_turns == 0:
            self.actor_agent.observe(
                {
                    "id": "Coordinator",
                    "text": "You are the acting agent. Observe your environment",
                    "task_data": {
                        "can_control_scene": True,
                    },
                }
            )
            self.viewer_agent.observe(
                {
                    "id": "Coordinator",
                    "text": "You are the viewing agent. Answer the actor's requests",
                    "task_data": {
                        "can_control_scene": False,
                    },
                }
            )
            self.current_turns += 0.1
        for index, agent in enumerate(self.agents):
            acts[index] = agent.act()
            if acts[index] is None:
                continue
            if len(acts[index]["text"]) > 0:
                self.current_turns += 1
            if acts[index].get("episode_done"):
                self.episodeDone = True
            for other_agent in self.agents:
                if other_agent != agent:
                    other_agent.observe(validate(acts[index]))
        if self.current_turns > self.max_turns:
            self.episodeDone = True

    def prep_save_data(self, agent):
        """Process and return any additional data from this world you may want to store"""
        return {"example_key": "example_value"}

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        """
        Shutdown all mturk agents in parallel, otherwise if one mturk agent is
        disconnected then it could prevent other mturk agents from completing.
        """
        global shutdown_agent

        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        Parallel(n_jobs=len(self.agents), backend="threading")(
            delayed(shutdown_agent)(agent) for agent in self.agents
        )


def make_onboarding_world(opt, agent):
    return MTurkMultimodalOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Check the contents of the data to ensure they are valid"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents, initialization_data=None):
    return MTurkMultimodalDialogWorld(opt, agents)


def get_world_params():
    return {"agent_count": 2}
