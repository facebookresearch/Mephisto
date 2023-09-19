#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

import pytest
from jsonschema.exceptions import ValidationError

from mephisto.abstractions.providers.prolific.api.data_models import Study


@pytest.mark.prolific
class TestDataModelsUtils(unittest.TestCase):
    def test_study_validation_passed(self, *args):
        data = {
            "name": "Name",
            "internal_name": "internal_name",
            "description": "Description",
            "external_study_url": "https://url",
            "prolific_id_option": "url_parameters",
            "completion_option": "url",
            "completion_codes": [],
            "total_available_places": 100,
            "estimated_completion_time": 5,
            "reward": 999,
            "device_compatibility": ["desktop"],
            "peripheral_requirements": [],
            "eligibility_requirements": [],
        }

        study = Study(**data)
        self.assertEqual(study.name, data["name"])

    def test_study_validation_error(self, *args):
        data = {
            "name": "Name",
        }

        with self.assertRaises(ValidationError) as cm:
            Study(**data).validate()

        self.assertEqual(cm.exception.validator, "required")
        self.assertEqual(cm.exception.message, "'description' is a required property")
