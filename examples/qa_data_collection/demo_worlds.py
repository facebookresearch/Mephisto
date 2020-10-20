#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
from parlai.core.worlds import validate


class QADataCollectionOnboardWorld(MTurkOnboardWorld):
    def __init__(self, opt, mturk_agent):
        super().__init__(opt, mturk_agent)
        self.opt = opt

    def parley(self):
        self.mturk_agent.agent_id = "Onboarding Agent"
        ad = {}
        ad['id'] = 'System'
        ad['text'] = 'Welcome onboard!'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act(timeout=self.opt["turn_timeout"])
        self.mturk_agent.observe(
            {
                "id": "System",
                "text": "Thank you for your input!",
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

    def __init__(self, opt, dataloader=None, mturk_agent=None):
        self.dataloader = dataloader
        self.mturk_agent = mturk_agent
        self.mturk_agent.agent_id = "QA Agent"
        self.episodeDone = False
        self.turn_index = -1
        self.context = None
        self.question = None
        self.answer = None
        self.opt = opt

        self.question_provided = False
        self.answer_provided = False

    def parley(self):

        def process_passage_change(response, ad):
            if "text" in ad:
                del ad["text"]
            ad["passage"] = self.dataloader.get(
                response['passage_id'])["context"]
            self.mturk_agent.observe(validate(ad))
            self.turn_index = self.turn_index - 1

        # Each turn starts from the QA Collector agent
        self.turn_index = (self.turn_index + 1) % 2
        ad = {'episode_done': False}
        ad['id'] = self.__class__.collector_agent_id

        if self.turn_index == 0:

            if not self.question_provided:
                qa = self.dataloader.act()
                ad["passage"] = qa["context"]

                ad['text'] = 'Please provide a question given this context.'
                self.mturk_agent.observe(validate(ad))
                self.question_provided = True

            response = self.mturk_agent.act(
                timeout=self.opt["turn_timeout"])

            if 'passage_id' in response:
                process_passage_change(response, ad)

            else:
                self.question = response

        if self.turn_index == 1:

            if not self.answer_provided:
                ad['text'] = 'Thanks. And what is the answer to your question?'

                ad['episode_done'] = True

                self.mturk_agent.observe(validate(ad))
                self.answer_provided = True

            response = self.mturk_agent.act(
                timeout=self.opt["turn_timeout"])
            if 'passage_id' in response:
                process_passage_change(response, ad)
            else:
                self.answer = response
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
        # self.task.shutdown()
        self.mturk_agent.shutdown()


def make_onboarding_world(opt, agent):
    return QADataCollectionOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Check the contents of the data to ensure they are valid"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents):
    return QADataCollectionWorld(opt, dataloader=opt["dataloader"], mturk_agent=agents[0])


def get_world_params():
    return {"agent_count": 1}
