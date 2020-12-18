#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
from parlai.core.worlds import validate
from joblib import Parallel, delayed


class QADataCollectionOnboardWorld(MTurkOnboardWorld):
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


class QADataCollectionWorld(MTurkTaskWorld):
    """
    World for recording a turker's question and answer given a context.
    Assumes the context is a random context from a given task, e.g. from SQuAD, CBT,
    etc.
    """

    collector_agent_id = 'QA Collector'

    def __init__(self, opt, agent):
        self.agent = agent
        self.agent.agent_id = "QA Agent"
        self.episodeDone = False
        self.turn_index = -1
        self.context = None
        self.question = None
        self.answer = None
        self.opt = opt

    def parley(self):
        # Each turn starts from the QA Collector agent
        self.turn_index = (self.turn_index + 1) % 2
        ad = {'episode_done': False}
        ad['id'] = self.__class__.collector_agent_id


        if self.turn_index == 0:
            # At the first turn, the QA Collector agent provides the context
            # and prompts the turker to ask a question regarding the context

            # Get context from SQuAD teacher agent
            # qa = self.task.act()
            qa = {"text":"This is a sample question\n"}
            self.context = '\n'.join(qa['text'].split('\n')[:-1])

            # Wrap the context with a prompt telling the turker what to do next
            ad['text'] = (
                self.context + '\n\nPlease provide a question given this context.'
            )
            self.agent.observe(validate(ad))
            self.question = self.agent.act(timeout=self.opt["turn_timeout"])
            # Can log the turker's question here

        if self.turn_index == 1:
            # At the second turn, the QA Collector collects the turker's
            # question from the first turn, and then prompts the
            # turker to provide the answer

            # A prompt telling the turker what to do next
            ad['text'] = 'Thanks. And what is the answer to your question?'

            # ad['episode_done'] = True  # end of episode

            self.agent.observe(validate(ad))
            self.answer = self.agent.act(timeout=self.opt["turn_timeout"])

            self.episodeDone = True


        # if self.current_turns >= self.max_turns:
            self.episodeDone = True
            for agent in self.agents:
                agent.observe(
                    {
                        "id": "Coordinator",
                        "text": "Please fill out the form to complete the chat:",
                        "task_data": {
                            "respond_with_form": [
                                {
                                    "type": "choices",
                                    "question": "How much did you enjoy talking to this user?",
                                    "choices": [
                                        "Not at all",
                                        "A little",
                                        "Somewhat",
                                        "A lot",
                                    ],
                                },
                                {
                                    "type": "choices",
                                    "question": "Do you think this user is a bot or a human?",
                                    "choices": [
                                        "Definitely a bot",
                                        "Probably a bot",
                                        "Probably a human",
                                        "Definitely a human",
                                    ],
                                },
                                {"type": "text", "question": "Enter any comment here"},
                            ]
                        },
                    }
                )
                agent.act()  # Request a response
            for agent in self.agents:  # Ensure you get the response
                form_result = agent.act(timeout=self.opt["turn_timeout"])

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
        # self.task.shutdown()
        self.agent.shutdown()


def make_onboarding_world(opt, agent):
    return QADataCollectionOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Check the contents of the data to ensure they are valid"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents):
    return QADataCollectionWorld(opt, agents[0])


def get_world_params():
    return {"agent_count": 1}
