#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.generators.form_composer.config_validation.unit_config import validate_unit_config
from mephisto.generators.generators_utils.config_validation.unit_config import (
    collect_values_for_unique_attrs_from_item,
)
from mephisto.generators.generators_utils.config_validation.unit_config import (
    duplicate_values_exist,
)


class TestFormConfig(unittest.TestCase):
    def setUp(self):
        set_form_composer_env_vars()

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

    def test_validate_unit_config_not_dict(self, *args, **kwargs):
        config_data = []

        result, errors = validate_unit_config(config_data)

        self.assertFalse(result)
        self.assertEqual(errors, ["Unit config must be a key/value JSON Object."])

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
                    "Object `form`. Not all required attributes were specified. "
                    "Required attributes: form. Passed attributes: wrong_key."
                ),
                (
                    "Object `form` has no available attribute with name `wrong_key`. "
                    "Available attributes: form, form_metadata."
                ),
                "Unit config must contain only these attributes: form, form_metadata.",
            ],
        )

    def test_validate_unit_config_not_all_required_fields(self, *args, **kwargs):
        config_data = {
            "form": {
                "instruction": "Form instruction",
                "sections": [
                    {
                        "name": "section_name",
                        "title": "Section title",
                        "instruction": "Section instruction",
                        "collapsable": False,
                        "initially_collapsed": True,
                        "fieldsets": [
                            {
                                "title": "Fieldset title",
                                "instruction": "Fieldset instruction",
                                "rows": [
                                    {
                                        "fields": [
                                            {
                                                "help": "Field help",
                                                "id": "id_field",
                                                "name": "field_name",
                                                "placeholder": "Field placeholder",
                                                "tooltip": "Field tooltip",
                                                "type": "file",
                                                "value": "",
                                            }
                                        ],
                                        "help": "Row help",
                                    },
                                ],
                                "help": "Fieldset help",
                            },
                        ],
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
                    "Object `form`. Not all required attributes were specified. "
                    "Required attributes: sections, submit_button, title. "
                    "Passed attributes: instruction, sections, submit_button."
                ),
                (
                    "Object `field` with name `field_name`. "
                    "Not all required attributes were specified. "
                    "Required attributes: label, name, type. "
                    "Passed attributes: help, id, name, placeholder, tooltip, type, value."
                ),
            ],
        )

    def test_validate_unit_config_with_duplicates(self, *args, **kwargs):
        config_data = {
            "form": {
                "title": "Form title",
                "instruction": "Form instruction",
                "sections": [
                    {
                        "name": "section_name",
                        "title": "Section title",
                        "instruction": "Section instruction",
                        "collapsable": False,
                        "initially_collapsed": True,
                        "fieldsets": [
                            {
                                "title": "Fieldset title",
                                "instruction": "Fieldset instruction",
                                "rows": [
                                    {
                                        "fields": [
                                            {
                                                "help": "Field help",
                                                "id": "id_field",
                                                "label": "Field label",
                                                "name": "section_name",
                                                "placeholder": "Field placeholder",
                                                "tooltip": "Field tooltip",
                                                "type": "file",
                                                "value": "",
                                            },
                                            {
                                                "help": "Field help 2",
                                                "id": "id_field",
                                                "label": "Field label 2",
                                                "name": "field_name",
                                                "placeholder": "Field placeholder 2",
                                                "tooltip": "Field tooltip 2",
                                                "type": "input",
                                                "value": "",
                                            },
                                        ],
                                        "help": "Row help",
                                    },
                                ],
                                "help": "Fieldset help",
                            },
                        ],
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
                    "Found duplicate names for unique attribute 'name' "
                    "in your form config: section_name"
                ),
                "Found duplicate names for unique attribute 'id' in your form config: id_field",
            ],
        )

    def test_validate_unit_config_incorrent_field_type(self, *args, **kwargs):
        config_data = {
            "form": {
                "title": "Form title",
                "instruction": "Form instruction",
                "sections": [
                    {
                        "name": "section_name",
                        "title": "Section title",
                        "instruction": "Section instruction",
                        "collapsable": False,
                        "initially_collapsed": True,
                        "fieldsets": [
                            {
                                "title": "Fieldset title",
                                "instruction": "Fieldset instruction",
                                "rows": [
                                    {
                                        "fields": [
                                            {
                                                "help": "Field help",
                                                "id": "id_field",
                                                "label": "Field label",
                                                "name": "field_name",
                                                "placeholder": "Field placeholder",
                                                "tooltip": "Field tooltip",
                                                "type": "incorrect_field_type",
                                                "value": "",
                                            }
                                        ],
                                        "help": "Row help",
                                    },
                                ],
                                "help": "Fieldset help",
                            },
                        ],
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
            ["Object 'field' has unsupported 'type' attribute value: incorrect_field_type"],
        )

    def test_validate_unit_config_success(self, *args, **kwargs):
        config_data = {
            "form": {
                "title": "Form title",
                "instruction": "Form instruction",
                "sections": [
                    {
                        "name": "section_name",
                        "title": "Section title",
                        "instruction": "Section instruction",
                        "collapsable": False,
                        "initially_collapsed": True,
                        "fieldsets": [
                            {
                                "title": "Fieldset title",
                                "instruction": "Fieldset instruction",
                                "rows": [
                                    {
                                        "fields": [
                                            {
                                                "help": "Field help",
                                                "id": "id_field",
                                                "label": "Field label",
                                                "name": "field_name",
                                                "placeholder": "Field placeholder",
                                                "tooltip": "Field tooltip",
                                                "type": "file",
                                                "value": "",
                                            }
                                        ],
                                        "help": "Row help",
                                    },
                                ],
                                "help": "Fieldset help",
                            },
                        ],
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

        self.assertTrue(result)
        self.assertEqual(errors, [])
