#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from copy import deepcopy

from mephisto.client.cli_video_annotator_commands import set_video_annotator_env_vars
from mephisto.client.cli_video_annotator_commands import VIDEO_ANNOTATOR__DATA_CONFIG_NAME
from mephisto.client.cli_video_annotator_commands import (
    VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
)
from mephisto.client.cli_video_annotator_commands import (
    VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME,
)
from mephisto.client.cli_video_annotator_commands import VIDEO_ANNOTATOR__UNIT_CONFIG_NAME
from mephisto.generators.video_annotator.config_validation.task_data_config import (
    collect_unit_config_items_to_extrapolate,
)
from mephisto.generators.video_annotator.config_validation.task_data_config import (
    verify_video_annotator_configs,
)

CORRECT_CONFIG_DATA_WITH_TOKENS = {
    "annotator": {
        "title": "Video Annotator test",
        "instruction": "Instruction {{instruction_token}}",
        "video": "{{video_path}}{{video_file}}",
        "segment_fields": [
            {"id": "id_title", "label": "Segment name", "name": "title", "type": "input"},
            {
                "id": "id_description",
                "label": "Segment description",
                "name": "description",
                "type": "textarea",
            },
            {
                "id": "id_can_understand",
                "label": "Segment understand",
                "name": "can_understand",
                "type": "radio",
                "options": [{"label": "Yes", "value": "yes"}, {"label": "No", "value": "no"}],
            },
            {
                "id": "id_person_name",
                "label": "Segment person name",
                "help": "Segment person name help {{person_name_help_token}}",
                "multiple": False,
                "name": "person_name",
                "type": "select",
                "options": [
                    {"label": "---", "value": ""},
                    {"label": "Bunny", "value": "bunny"},
                    {"label": "Squirrel", "value": "squirrel"},
                ],
                "value": "",
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


class TestTaskDataConfig(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        set_video_annotator_env_vars(use_validation_mapping_cache=False)

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test__collect_unit_config_items_to_extrapolate(self, *args, **kwargs):
        config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)

        items = collect_unit_config_items_to_extrapolate(config_data)

        self.assertEqual(len(items), 6)

    def test_verify_video_annotator_configs_errors(self, *args, **kwargs):
        task_data_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__DATA_CONFIG_NAME,
        )
        unit_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        captured_print_output = io.StringIO()
        sys.stdout = captured_print_output
        verify_video_annotator_configs(
            task_data_config_path,
            unit_config_path,
            token_sets_values_config_path,
            separate_token_values_config_path,
            task_data_config_only=False,
        )
        sys.stdout = sys.__stdout__

        self.assertIn(
            "Required file not found:",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            f"'{self.data_dir}/task_data.json'",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            f"'{self.data_dir}/unit_config.json'",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            f"'{self.data_dir}/token_sets_values_config.json'",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            f"'{self.data_dir}/separate_token_values_config.json'",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            "Provided Video Annotator config files are invalid:",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            (
                "- Separate token values config is invalid. Errors:\n  "
                "- Config must be a key/value JSON Object.\n\n"
            ),
            captured_print_output.getvalue(),
        )

    def test_verify_video_annotator_configs_errors_task_data_config_only(self, *args, **kwargs):
        task_data_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__DATA_CONFIG_NAME,
        )
        unit_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        captured_print_output = io.StringIO()
        sys.stdout = captured_print_output
        verify_video_annotator_configs(
            task_data_config_path,
            unit_config_path,
            token_sets_values_config_path,
            separate_token_values_config_path,
            task_data_config_only=True,
        )
        sys.stdout = sys.__stdout__

        self.assertIn(
            "Required file not found:",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            f"'{self.data_dir}/task_data.json'",
            captured_print_output.getvalue(),
        )

    def test_verify_video_annotator_configs_success(self, *args, **kwargs):
        task_data_config_data = [deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)]
        unit_config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "instruction_token": "value 1",
                    "video_path": "https://your-bucket.s3.amazonaws.com/your/folder/path/",
                    "video_file": "file.mp4",
                    "submit_instruction_token": "value 4",
                    "person_name_help_token": "value 5",
                },
            },
        ]

        separate_token_values_config_data = {
            "instruction_token": [
                "value 1",
            ],
            "video_path": [
                "https://your-bucket.s3.amazonaws.com/your/folder/path/",
            ],
            "video_file": [
                "file.mp4",
            ],
            "submit_instruction_token": [
                "value 4",
            ],
            "person_name_help_token": [
                "value 5",
            ],
        }

        task_data_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__DATA_CONFIG_NAME,
        )
        unit_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            VIDEO_ANNOTATOR__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        task_data_config_f = open(task_data_config_path, "w")
        task_data_config_f.write(json.dumps(task_data_config_data))
        task_data_config_f.close()

        unit_config_f = open(unit_config_path, "w")
        unit_config_f.write(json.dumps(unit_config_data))
        unit_config_f.close()

        token_sets_values_config_f = open(token_sets_values_config_path, "w")
        token_sets_values_config_f.write(json.dumps(token_sets_values_config_data))
        token_sets_values_config_f.close()

        separate_token_values_config_f = open(separate_token_values_config_path, "w")
        separate_token_values_config_f.write(json.dumps(separate_token_values_config_data))
        separate_token_values_config_f.close()

        captured_print_output = io.StringIO()
        sys.stdout = captured_print_output
        verify_video_annotator_configs(
            task_data_config_path,
            unit_config_path,
            token_sets_values_config_path,
            separate_token_values_config_path,
        )
        sys.stdout = sys.__stdout__

        self.assertIn("All configs are valid.", captured_print_output.getvalue(), "\n")
