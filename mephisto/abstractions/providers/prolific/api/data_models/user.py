#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional
from typing import Union

from .base_model import BaseModel
from ..constants import EMAIL_FORMAT


class User(BaseModel):
    """
    More about Users:
        https://docs.prolific.co/docs/api-docs/public/#tag/Users
    """

    address: Optional[str]
    available_balance: Optional[Union[int, float]]
    balance: Optional[Union[int, float]]
    balance_breakdown: Optional[dict]
    beta_tester: bool
    billing_address: Optional[str]
    can_cashout_enabled: bool
    can_contact_support_enabled: bool
    can_instant_cashout_enabled: bool
    can_oidc_login: bool
    can_oidc_login_enabled: bool
    can_run_pilot_study_enabled: bool
    can_topup_3d: bool
    country: Optional[str]
    currency_code: Optional[str]
    current_project_id: Optional[str]
    date_joined: str
    datetime_created: str
    email: str
    email_preferences: dict
    experimental_group: Optional[int]
    fees_per_submission: Optional[Union[int, float]]
    fees_percentage: Optional[Union[int, float]]
    first_name: str
    has_accepted_survey_builder_terms: bool
    has_answered_vat_number: bool
    has_password: bool
    id: str
    invoice_usage_enabled: bool
    is_email_verified: bool
    is_staff: bool
    last_login: Optional[str]
    last_name: str
    minimum_reward_per_hour: Optional[Union[int, float]]
    name: str
    needs_to_confirm_US_state: bool
    on_hold: bool
    privacy_policy: bool
    redeemable_referral_coupon: Optional[str]
    referral_incentive: dict
    referral_url: Optional[str]
    representative_sample_credits: Optional[Union[int, float]]
    roles: List[str]
    service_margin_percentage: Optional[Union[int, float]]
    status: str
    terms_and_conditions: bool
    topups_over_referral_threshold: bool
    user_type: str
    username: str
    vat_number: Optional[int]
    vat_percentage: Optional[Union[int, float]]

    schema = {
        "type": "object",
        "properties": {
            "address": {"type": ["string", "null"]},
            "available_balance": {"type": ["number", "null"]},
            "balance": {"type": ["number", "null"]},
            "balance_breakdown": {"type": ["object", "null"]},
            "beta_tester": {"type": "boolean"},
            "billing_address": {"type": ["string", "null"]},
            "can_cashout_enabled": {"type": "boolean"},
            "can_contact_support_enabled": {"type": "boolean"},
            "can_instant_cashout_enabled": {"type": "boolean"},
            "can_oidc_login": {"type": "boolean"},
            "can_oidc_login_enabled": {"type": "boolean"},
            "can_run_pilot_study_enabled": {"type": "boolean"},
            "can_topup_3d": {"type": "boolean"},
            "country": {"type": ["string", "null"]},
            "currency_code": {"type": "string"},
            "current_project_id": {"type": ["string", "null"]},
            "date_joined": {"type": "string"},
            "datetime_created": {"type": "string"},
            "email": {
                "type": "string",
                "pattern": EMAIL_FORMAT,
            },
            "email_preferences": {"type": "object"},
            "experimental_group": {"type": ["number", "null"]},
            "fees_per_submission": {"type": ["number", "null"]},
            "fees_percentage": {"type": ["number", "null"]},
            "first_name": {"type": "string"},
            "has_accepted_survey_builder_terms": {"type": "boolean"},
            "has_answered_vat_number": {"type": "boolean"},
            "has_password": {"type": "boolean"},
            "id": {"type": "string"},
            "invoice_usage_enabled": {"type": "boolean"},
            "is_email_verified": {"type": "boolean"},
            "is_staff": {"type": "boolean"},
            "last_login": {"type": ["string", "null"]},
            "last_name": {"type": "string"},
            "minimum_reward_per_hour": {"type": ["number", "null"]},
            "name": {"type": "string"},
            "needs_to_confirm_US_state": {"type": "boolean"},
            "on_hold": {"type": "boolean"},
            "privacy_policy": {"type": "boolean"},
            "redeemable_referral_coupon": {"type": ["string", "null"]},
            "referral_incentive": {"type": "object"},
            "referral_url": {"type": ["string", "null"]},
            "representative_sample_credits": {"type": ["number", "null"]},
            "roles": {"type": "array"},
            "service_margin_percentage": {"type": ["number", "null"]},
            "status": {"type": "string"},
            "terms_and_conditions": {"type": "boolean"},
            "topups_over_referral_threshold": {"type": "boolean"},
            "user_type": {"type": "string"},
            "username": {"type": "string"},
            "vat_number": {"type": ["number", "null"]},
            "vat_percentage": {"type": ["number", "null"]},
        },
    }

    relation_user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {
                "type": "string",
                "pattern": EMAIL_FORMAT,
            },
            "roles": {"type": "array"},
        },
        "required": [
            "id",
        ],
    }

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id} {self.email}"
