#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from mephisto.client.cli_video_annotator_commands import set_video_annotator_env_vars
from mephisto.generators.video_annotator.config_validation.unit_config import validate_unit_config


class TestUnitConfig(unittest.TestCase):
    def setUp(self):
        set_video_annotator_env_vars(use_validation_mapping_cache=False)

    def test_validate_unit_config_not_dict(self, *args, **kwargs):
        config_data = []

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(errors, ["Annotator config must be a key/value JSON Object."])

    def test_validate_unit_config_wrong_keys(self, *args, **kwargs):
        config_data = {
            "wrong_key": {},
        }

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `annotator`. Not all required attributes were specified. "
                    "Required attributes: annotator. Passed attributes: wrong_key."
                ),
                (
                    "Object `annotator` has no available attribute with name `wrong_key`. "
                    "Available attributes: annotator, annotator_metadata."
                ),
                (
                    "Annotator config must contain only these attributes: "
                    "annotator, annotator_metadata."
                ),
            ],
        )

    def test_validate_unit_config_not_all_required_fields(self, *args, **kwargs):
        config_data = {
            "annotator": {
                "video": "https://your-bucket.s3.amazonaws.com/your/folder/path/file.mp4",
                "segment_fields": [
                    {
                        "help": "Title help",
                        "id": "id_title",
                        "name": "title",
                        "placeholder": "Title placeholder",
                        "tooltip": "Title tooltip",
                        "type": "input",
                        "value": "",
                    },
                ],
                "submit_button": {
                    "instruction": "Submit instruction",
                    "text": "Submit",
                    "tooltip": "Submit tooltip",
                },
            },
        }

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `annotator`. Not all required attributes were specified. "
                    "Required attributes: submit_button, title, video. "
                    "Passed attributes: video, segment_fields, submit_button."
                ),
                (
                    "Object `field` with name `title`. "
                    "Not all required attributes were specified. "
                    "Required attributes: label, name, type. "
                    "Passed attributes: help, id, name, placeholder, tooltip, type, value."
                ),
            ],
        )

    def test_validate_unit_config_no_title_field(self, *args, **kwargs):
        config_data = {
            "annotator": {
                "title": "Video Annotator test",
                "video": "https://your-bucket.s3.amazonaws.com/your/folder/path/file.mp4",
                "segment_fields": [
                    {
                        "help": "Name help",
                        "id": "id_name",
                        "name": "name",
                        "placeholder": "Name placeholder",
                        "tooltip": "Name tooltip",
                        "type": "input",
                        "value": "",
                    },
                ],
                "submit_button": {
                    "instruction": "Submit instruction",
                    "text": "Submit",
                    "tooltip": "Submit tooltip",
                },
            },
        }

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    'First field must be "title". '
                    "If you have it, move it above all fields, or add a new one"
                ),
            ],
        )

    def test_validate_unit_config_with_duplicates(self, *args, **kwargs):
        config_data = {
            "annotator": {
                "title": "Video Annotator test",
                "instruction": "Instruction",
                "video": "https://your-bucket.s3.amazonaws.com/your/folder/path/file.mp4",
                "segment_fields": [
                    {"id": "id_title", "label": "Segment name", "name": "title", "type": "input"},
                    {
                        "id": "id_title",
                        "label": "Segment description",
                        "name": "title",
                        "type": "textarea",
                    },
                ],
                "show_instructions_as_modal": True,
                "submit_button": {
                    "instruction": "Submit button instruction",
                    "text": "Submit",
                    "tooltip": "Submit annotations",
                },
            },
        }

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                "Found duplicate names for unique attribute 'id' in your form config: id_title",
                "Found duplicate names for unique attribute 'name' in your form config: title",
            ],
        )

    def test_validate_unit_config_incorrent_field_type(self, *args, **kwargs):
        config_data = {
            "annotator": {
                "title": "Video Annotator test",
                "instruction": "Instruction",
                "video": "https://your-bucket.s3.amazonaws.com/your/folder/path/file.mp4",
                "segment_fields": [
                    {
                        "id": "id_title",
                        "label": "Segment name",
                        "name": "title",
                        "type": "incorrect_field_type",
                    },
                ],
                "show_instructions_as_modal": True,
                "submit_button": {
                    "instruction": "Submit button instruction {{submit_instruction_token}}",
                    "text": "Submit",
                    "tooltip": "Submit annotations",
                },
            },
        }

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            ["Object 'field' has unsupported 'type' attribute value: incorrect_field_type"],
        )

    def test_validate_unit_config_success(self, *args, **kwargs):
        config_data = {
            "annotator": {
                "title": "Video Annotator test",
                "instruction": "Instruction",
                "video": "https://your-bucket.s3.amazonaws.com/your/folder/path/file.mp4",
                "segment_fields": [
                    {"id": "id_title", "label": "Segment name", "name": "title", "type": "input"},
                ],
                "show_instructions_as_modal": True,
                "submit_button": {
                    "instruction": "Submit button instruction",
                    "text": "Submit",
                    "tooltip": "Submit annotations",
                },
            },
        }

        result, errors = validate_unit_config(config_data)

        self.assertTrue(result)
        self.assertEqual(errors, [])
