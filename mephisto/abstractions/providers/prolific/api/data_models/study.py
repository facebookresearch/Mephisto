#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional
from typing import Union

from .base_model import BaseModel


class Study(BaseModel):
    """
    More about Studies:
        https://docs.prolific.co/docs/api-docs/public/#tag/Studies
    """

    alternative_completion_codes: List
    average_reward_per_hour: Union[int, float]
    average_reward_per_hour_without_adjustment: Union[int, float]
    average_time_taken: int
    average_time_taken_seconds: int
    can_be_reallocated: bool
    completion_code: str
    completion_code_action: Optional[str]
    completion_codes: Optional[List[dict]]
    completion_option: Optional[str]
    currency_code: Optional[str]
    date_created: str
    description: str
    device_compatibility: List[str]
    discount_from_coupons: Union[int, float]
    eligibility_requirements: List[dict]
    eligible_participant_count: int
    estimated_completion_time: Union[int, float]
    estimated_reward_per_hour: Union[int, float]
    external_app: str
    external_id: str
    external_study_url: str
    failed_attention_code: Optional[str]
    fees_per_submission: Union[int, float]
    fees_percentage: Union[int, float]
    has_had_adjustment: bool
    id: str
    internal_name: str
    is_reallocated: bool
    is_underpaying: Optional[bool]
    last_email_update_sent_datetime: Optional[str]
    maximum_allowed_time: int
    metadata: Optional[Union[str, dict, int]]
    minimum_reward_per_hour: Union[int, float]
    naivety_distribution_rate: Optional[Union[int, float]]
    name: str
    number_of_submissions: Union[int, float]
    peripheral_requirements: List
    places_taken: Union[int, float]
    privacy_notice: str
    progress_percentage: Union[int, float]
    project: Optional[str]
    prolific_id_option: Optional[str]
    publish_at: Optional[str]
    published_at: Optional[str]
    publisher: Optional[str]
    quota_requirements: Optional[List]
    reallocated_places: int
    receipt: Optional[str]
    representative_sample: Optional[str]
    representative_sample_fee: Union[int, float]
    researcher: dict
    reward: Union[int, float]
    reward_level: dict
    service_margin_percentage: str
    share_id: Optional[str]
    stars_remaining: int
    status: str
    study_type: str
    submissions_config: dict
    total_available_places: int
    total_cost: Union[int, float]
    total_participant_pool: Union[int, float]
    vat_percentage: Union[int, float]
    workspace: str

    schema = {
        "type": "object",
        "properties": {
            "alternative_completion_codes": {"type": "array"},
            "average_reward_per_hour": {"type": "number"},
            "average_reward_per_hour_without_adjustment": {"type": "number"},
            "average_time_taken": {"type": "number"},
            "average_time_taken_seconds": {"type": "number"},
            "can_be_reallocated": {"type": "boolean"},
            "completion_code": {"type": "string"},
            "completion_code_action": {"type": ["string", "null"]},
            "completion_codes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "code_type": {"type": "string"},
                        "actions": {"type": "array"},
                    },
                    "required": [
                        "code",
                        "code_type",
                    ],
                },
            },
            "completion_option": {
                "type": ["string", "null"],
                "items": {"enum": ["url", "code"]},
            },
            "currency_code": {"type": ["string", "null"]},
            "date_created": {"type": "string"},
            "description": {"type": "string"},
            "device_compatibility": {
                "type": "array",
                "items": {"enum": ["desktop", "tablet", "mobile"]},
            },
            "discount_from_coupons": {"type": "number"},
            "eligibility_requirements": {"type": "array"},
            "eligible_participant_count": {"type": "number"},
            "estimated_completion_time": {"type": "number"},
            "estimated_reward_per_hour": {"type": "number"},
            "external_app": {"type": "string"},
            "external_id": {"type": "string"},
            "external_study_url": {"type": "string"},
            "failed_attention_code": {"type": ["string", "null"]},
            "fees_per_submission": {"type": "number"},
            "fees_percentage": {"type": "number"},
            "has_had_adjustment": {"type": "boolean"},
            "id": {"type": "string"},
            "internal_name": {"type": "string"},
            "is_reallocated": {"type": "boolean"},
            "is_underpaying": {"type": ["boolean", "null"]},
            "last_email_update_sent_datetime": {"type": ["string", "null"]},
            "maximum_allowed_time": {"type": "number"},
            "metadata": {"type": ["string", "object", "number", "null"]},
            "minimum_reward_per_hour": {"type": "number"},
            "naivety_distribution_rate": {"type": ["number", "null"]},
            "name": {"type": "string"},
            "number_of_submissions": {"type": "number"},
            "peripheral_requirements": {"type": "array"},
            "places_taken": {"type": "number"},
            "privacy_notice": {"type": "string"},
            "progress_percentage": {"type": "number"},
            "project": {"type": "string"},
            "prolific_id_option": {
                "type": ["string", "null"],
                "items": {"enum": ["question", "url_parameters", "not_required"]},
            },
            "publish_at": {"type": ["string", "null"]},
            "published_at": {"type": ["string", "null"]},
            "publisher": {"type": ["string", "null"]},
            "quota_requirements": {"type": ["array", "null"]},
            "reallocated_places": {"type": "number"},
            "receipt": {"type": ["string", "null"]},
            "representative_sample": {"type": ["string", "null"]},
            "representative_sample_fee": {"type": "number"},
            "researcher": {"type": "object"},
            "reward": {"type": "number"},
            "reward_level": {"type": "object"},
            "service_margin_percentage": {"type": "string"},
            "share_id": {"type": ["string", "null"]},
            "stars_remaining": {"type": "number"},
            "status": {"type": "string"},
            "study_type": {"type": "string"},
            "submissions_config": {"type": "object"},
            "total_available_places": {"type": "number"},
            "total_cost": {"type": "number"},
            "total_participant_pool": {"type": "number"},
            "vat_percentage": {"type": "number"},
            "workspace": {"type": "string"},
        },
    }

    required_schema_fields = [
        "name",
        "description",
        "external_study_url",
        "prolific_id_option",
        "completion_option",
        "completion_codes",
        "total_available_places",
        "estimated_completion_time",
        "reward",
        "eligibility_requirements",
    ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id} {self.name}"
