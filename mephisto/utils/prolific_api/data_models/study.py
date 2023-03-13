#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_model import BaseModel


class Study(BaseModel):
    id: str
    name: str
    internal_name: str
    description: str
    external_study_url: str
    prolific_id_option: str
    completion_codes: List[dict]
    total_available_places: int
    estimated_completion_time: int
    reward: int
    device_compatibility: List[str]
    peripheral_requirements: List
    eligibility_requirements: List

    _schema = {
        'type' : 'object',
        'properties' : {
            'id' : {
                'type' : 'string',
            },
            'name' : {
                'type' : 'string',
            },
            'internal_name' : {
                'type' : 'string',
            },
            'description' : {
                'type' : 'string',
            },
            'external_study_url' : {
                'type' : 'string',
            },
            'prolific_id_option' : {
                'type' : 'string',
                'items': {
                    'enum': ['question', 'url_parameters', 'not_required'],
                },
            },
            'completion_option' : {
                'type' : 'string',
                'items': {
                    'enum': ['url', 'code'],
                },
            },
            'completion_codes' : {
                'type' : 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'code': {
                            'type': 'string',
                        },
                        'code_type': {
                            'type': 'string',
                        },
                        'actions': {
                            'type': 'array',
                        },
                    },
                    'required': [
                        'code',
                        'code_type',
                    ]
                }
            },
            'total_available_places' : {
                'type' : 'number',
            },
            'estimated_completion_time' : {
                'type' : 'number',
            },
            'reward' : {
                'type' : 'number',
            },
            'device_compatibility' : {
                'type' : 'array',
                'items': {
                    'enum': ['desktop', 'tablet', 'mobile'],
                },
            },
            'peripheral_requirements' : {
                'type' : 'array',
            },
            'eligibility_requirements' : {
                'type' : 'array',
            },
        },
        'required': [
            'name',
            'description',
            'external_study_url',
            'prolific_id_option',
            'completion_option',
            'completion_codes',
            'total_available_places',
            'estimated_completion_time',
            'reward',
            'eligibility_requirements',
        ]
    }
