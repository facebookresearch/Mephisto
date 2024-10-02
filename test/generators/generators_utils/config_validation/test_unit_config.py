#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.generators.generators_utils.config_validation.unit_config import (
    collect_values_for_unique_attrs_from_item,
)
from mephisto.generators.generators_utils.config_validation.unit_config import (
    duplicate_values_exist,
)


class TestUnitConfig(unittest.TestCase):
    def setUp(self):
        set_form_composer_env_vars(use_validation_mapping_cache=False)

    def test__collect_values_for_unique_attrs_from_item(self, *args, **kwargs):
        item = {
            "help": "Field help",
            "id": "id_field",
            "label": "Field label",
            "name": "field_name",
            "placeholder": "Field placeholder",
            "tooltip": "Field tooltip",
            "type": "file",
            "validators": {
                "required": True,
            },
            "value": "",
        }

        values_for_unique_attrs = {}
        result = collect_values_for_unique_attrs_from_item(
            item=item,
            values_for_unique_attrs=values_for_unique_attrs,
        )

        self.assertEqual(result, {"id": ["id_field"], "name": ["field_name"]})

    def test__duplicate_values_exist_no_duplicates(self, *args, **kwargs):
        no_duplicates_values_for_unique_attrs = {"id": ["id_field"], "name": ["field_name"]}
        errors = []

        result = duplicate_values_exist(no_duplicates_values_for_unique_attrs, errors)

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test__duplicate_values_exist_with_duplicates(self, *args, **kwargs):
        no_duplicates_values_for_unique_attrs = {
            "id": ["id_field", "id_field"],
            "name": ["field_name", "field_name"],
        }
        errors = []

        result = duplicate_values_exist(no_duplicates_values_for_unique_attrs, errors)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                "Found duplicate names for unique attribute 'id' in your form config: id_field",
                "Found duplicate names for unique attribute 'name' in your form config: field_name",
            ],
        )
