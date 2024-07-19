#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from uuid import uuid4

from mephisto.abstractions._subcomponents.agent_state import AgentState
from mephisto.abstractions._subcomponents.agent_state import DEFAULT_METADATA_PROPERTY_NAME
from mephisto.utils.logger_core import get_logger

try:
    from detoxify import Detoxify

    DETOXIFY_INSTALLED = True
except ImportError:
    DETOXIFY_INSTALLED = False

logger = get_logger(name=__name__)


def save_agent_metadata(data: dict, state: AgentState):
    """Handles saving metadata"""
    if "tips" in data:
        _save_tips(data, state)
    elif "feedback" in data:
        _save_feedback(data, state)
    elif "worker_opinion" in data:
        _save_worker_opinion(data, state)
    else:
        _save_metadata_without_transforming(data, state)


def _save_metadata_without_transforming(data: dict, state: AgentState):
    """Default saving the metadata submission"""
    state.update_metadata(property_name=DEFAULT_METADATA_PROPERTY_NAME, property_value=data)


def _save_tips(data: dict, state: AgentState):
    """Handles the metadata submission of a tip"""

    tips_property_name = "tips"

    assert_message = (
        "The {property_name} field must exist in _AgentStateMetadata. "
        "Go into _AgentStateMetadata and add the {property_name} field"
    ).format(property_name=tips_property_name)
    assert hasattr(state.metadata, tips_property_name) is True, assert_message

    new_tip_header = data[tips_property_name]["header"]
    new_tip_text = data[tips_property_name]["text"]
    copy_of_tips = None
    tip_to_add = {
        "id": str(uuid4()),
        "header": new_tip_header,
        "text": new_tip_text,
        "accepted": False,
    }
    if state.metadata.tips is None:
        state.update_metadata(property_name=tips_property_name, property_value=[tip_to_add])
    else:
        copy_of_tips = state.metadata.tips.copy()
        copy_of_tips.append(tip_to_add)
        state.update_metadata(property_name=tips_property_name, property_value=copy_of_tips)


def _save_feedback(data: dict, state: AgentState):
    """Handles the metadata submission of a feedback"""

    feedback_property_name = "feedback"

    questions_and_answers = data[feedback_property_name]["data"]
    for question_obj in questions_and_answers:
        new_feedback_text = question_obj["text"]
        new_feedback_toxicity = (
            Detoxify("original").predict(new_feedback_text)["toxicity"]
            if DETOXIFY_INSTALLED is True
            else None
        )
        feedback_to_add = {
            "id": str(uuid4()),
            "question": question_obj["question"],
            "text": new_feedback_text,
            "reviewed": False,
            "toxicity": (None if new_feedback_toxicity is None else str(new_feedback_toxicity)),
        }
        if state.metadata.feedback is None:
            state.update_metadata(
                property_name=feedback_property_name,
                property_value=[feedback_to_add],
            )
        else:
            copy_of_feedback = state.metadata.feedback.copy()
            copy_of_feedback.append(feedback_to_add)
            state.update_metadata(
                property_name=feedback_property_name,
                property_value=copy_of_feedback,
            )


def _save_worker_opinion(data: dict, state: AgentState):
    """Handles the metadata submission of a worker opinion"""

    worker_opinion_property_name = "worker_opinion"

    # Add information about attachments
    worker_opinion_attachments_to_add = data["files"]
    worker_opinion_attachments_by_fields_to_add = data["filesByFields"]

    # Add questions and their answers
    worker_opinion_questions_to_add = []
    questions_and_answers = data[worker_opinion_property_name]["questions"]
    for question_obj in questions_and_answers:
        new_worker_opinion_text = question_obj["text"]
        new_worker_opinion_toxicity = (
            Detoxify("original").predict(new_worker_opinion_text)["toxicity"]
            if DETOXIFY_INSTALLED is True
            else None
        )

        worker_opinion_questions_to_add.append(
            {
                "id": str(uuid4()),
                "question": question_obj["question"],
                "answer": new_worker_opinion_text,
                "reviewed": False,
                "toxicity": (
                    None
                    if new_worker_opinion_toxicity is None
                    else str(new_worker_opinion_toxicity)
                ),
            }
        )

    if state.metadata.worker_opinion is not None:
        worker_opinion_prev = state.metadata.worker_opinion.copy()

        # Attachments (list of files)
        worker_opinion_attachments_prev = worker_opinion_prev.get("attachments", [])
        worker_opinion_attachments_to_add = (
            worker_opinion_attachments_prev + worker_opinion_attachments_to_add
        )

        # Attachments by fields (dict with files by fieldname)
        worker_opinion_attachments_by_fields_prev = worker_opinion_prev.get(
            "attachments_by_fields",
            {},
        )
        worker_opinion_attachments_by_fields_to_add = {
            **worker_opinion_attachments_by_fields_prev,
            **worker_opinion_attachments_by_fields_to_add,
        }

        # Questions (list of questions with answers)
        worker_opinion_questions_prev = worker_opinion_prev.get("questions", [])
        worker_opinion_questions_to_add = (
            worker_opinion_questions_prev + worker_opinion_questions_to_add
        )

    # Save transformed data
    state.update_metadata(
        property_name=worker_opinion_property_name,
        property_value={
            "attachments": worker_opinion_attachments_to_add,
            "attachments_by_fields": worker_opinion_attachments_by_fields_to_add,
            "questions": worker_opinion_questions_to_add,
        },
    )
