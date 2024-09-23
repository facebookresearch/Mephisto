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
from unittest.mock import patch

from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import (
    FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
)
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__UNIT_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.generators.form_composer.config_validation.task_data_config import (
    collect_unit_config_items_to_extrapolate,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    _collect_tokens_from_unit_config,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    _combine_extrapolated_unit_configs,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    _extrapolate_tokens_in_unit_config,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    _extrapolate_tokens_values,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    _set_tokens_in_unit_config_item,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    _validate_tokens_in_both_configs,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    prepare_task_config_for_review_app,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    validate_task_data_config,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    verify_generator_configs,
)

CORRECT_CONFIG_DATA_WITH_TOKENS = {
    "form": {
        "title": "Form title {{token_1}}",
        "instruction": "Form instruction {{token_2}}",
        "sections": [
            {
                "name": "section_name",
                "title": "Section title {{token_3}}",
                "instruction": "Section instruction",
                "collapsable": False,
                "initially_collapsed": True,
                "fieldsets": [
                    {
                        "title": "Fieldset title {{token_4}}",
                        "instruction": "Fieldset instruction",
                        "rows": [
                            {
                                "fields": [
                                    {
                                        "help": "Field help {{token_5}}",
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
            "instruction": "Submit instruction {{token_5}}",
            "text": "Submit",
            "tooltip": "Submit tooltip",
        },
    },
}


class TestTaskDataConfig(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        set_form_composer_env_vars()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test__extrapolate_tokens_values_simple(self, *args, **kwargs):
        text = "Test {{token_1}} and {{token_2}}"
        tokens_values = {
            "token_1": "value 1",
            "token_2": "value 2",
        }
        result = _extrapolate_tokens_values(text, tokens_values)

        self.assertEqual(result, "Test value 1 and value 2")

    def test__extrapolate_tokens_values_with_spaces_around(self, *args, **kwargs):
        text = "Test {{ token_1 }} and {{      token_2          }}"
        tokens_values = {
            "token_1": "value 1",
            "token_2": "value 2",
        }
        result = _extrapolate_tokens_values(text, tokens_values)

        self.assertEqual(result, "Test value 1 and value 2")

    def test__extrapolate_tokens_values_with_new_lines_around(self, *args, **kwargs):
        text = "Test {{\ntoken_1\n}} and {{\n\ntoken_2\n\n}}"
        tokens_values = {
            "token_1": "value 1",
            "token_2": "value 2",
        }
        result = _extrapolate_tokens_values(text, tokens_values)

        self.assertEqual(result, "Test value 1 and value 2")

    def test__extrapolate_tokens_values_with_tabs_around(self, *args, **kwargs):
        text = "Test {{\ttoken_1\t}} and {{\t\ttoken_2\t\t}}"
        tokens_values = {
            "token_1": "value 1",
            "token_2": "value 2",
        }
        result = _extrapolate_tokens_values(text, tokens_values)

        self.assertEqual(result, "Test value 1 and value 2")

    def test__extrapolate_tokens_values_with_bracketed_values(self, *args, **kwargs):
        text = "Test {{token_1}} and {{token_2}}"
        tokens_values = {
            "token_1": "{{value 1}}",
            "token_2": "{{value 2}}",
        }
        result = _extrapolate_tokens_values(text, tokens_values)

        self.assertEqual(result, "Test {{value 1}} and {{value 2}}")

    def test__extrapolate_tokens_values_with_procedure_tokens(self, *args, **kwargs):
        text = 'Test {{someProcedureWithArguments({"arg": 1})}} and {{otherProcedure(True)}}'
        tokens_values = {
            'someProcedureWithArguments({"arg": 1})': "value 1",
            "otherProcedure(True)": "value 2",
        }
        result = _extrapolate_tokens_values(text, tokens_values)

        self.assertEqual(result, "Test value 1 and value 2")

    def test__set_tokens_in_unit_config_item(self, *args, **kwargs):
        item = {
            "title": "Form title {{token_1}} and {{token_2}}",
            "instruction": "Form instruction {{token_2}}",
        }
        tokens_values = {
            "token_1": "value 1",
            "token_2": "value 2",
        }

        _set_tokens_in_unit_config_item(item, tokens_values)

        self.assertEqual(
            item,
            {
                "title": "Form title value 1 and value 2",
                "instruction": "Form instruction value 2",
            },
        )

    def test__collect_unit_config_items_to_extrapolate(self, *args, **kwargs):
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

        items = collect_unit_config_items_to_extrapolate(config_data)

        self.assertEqual(len(items), 6)

    def test__collect_tokens_from_unit_config_success(self, *args, **kwargs):
        config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)

        tokens, errors = _collect_tokens_from_unit_config(config_data)

        self.assertEqual(tokens, {"token_1", "token_2", "token_3", "token_4", "token_5"})
        self.assertEqual(errors, [])

    def test__collect_tokens_from_unit_config_with_errors(self, *args, **kwargs):
        config_data = {
            "form": {
                "title": "Form title {{token_1}}",
                "instruction": "Form instruction {{token_2}}",
                "sections": [
                    {
                        "name": "section_name {{token_6}}",
                        "title": "Section title {{token_3}}",
                        "instruction": "Section instruction",
                        "collapsable": False,
                        "initially_collapsed": True,
                        "fieldsets": [
                            {
                                "title": "Fieldset title {{token_4}}",
                                "instruction": "Fieldset instruction",
                                "rows": [
                                    {
                                        "fields": [
                                            {
                                                "help": "Field help {{token_5}}",
                                                "id": "id_field {{token_7}}",
                                                "label": "Field label",
                                                "name": "field_name {{token_8}}",
                                                "placeholder": "Field placeholder",
                                                "tooltip": "Field tooltip",
                                                "type": "file {{token_9}}",
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
                    "instruction": "Submit instruction {{token_5}}",
                    "text": "Submit",
                    "tooltip": "Submit tooltip",
                },
            },
        }

        tokens, errors = _collect_tokens_from_unit_config(config_data)

        self.assertEqual(tokens, {"token_1", "token_2", "token_3", "token_4", "token_5"})
        self.assertEqual(
            sorted(errors),
            sorted(
                [
                    (
                        "You tried to set tokens 'token_6' in attribute 'name' with value "
                        "'section_name {{token_6}}'. You can use tokens only in following attributes: "
                        "help, instruction, label, title, tooltip"
                    ),
                    (
                        "You tried to set tokens 'token_8' in attribute 'name' with value "
                        "'field_name {{token_8}}'. You can use tokens only in following attributes: "
                        "help, instruction, label, title, tooltip"
                    ),
                    (
                        "You tried to set tokens 'token_7' in attribute 'id' with value "
                        "'id_field {{token_7}}'. You can use tokens only in following attributes: "
                        "help, instruction, label, title, tooltip"
                    ),
                    (
                        "You tried to set tokens 'token_9' in attribute 'type' with value "
                        "'file {{token_9}}'. You can use tokens only in following attributes: "
                        "help, instruction, label, title, tooltip"
                    ),
                ]
            ),
        )

    def test__extrapolate_tokens_in_unit_config_success(self, *args, **kwargs):
        config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        tokens_values = {
            "token_1": "value 1",
            "token_2": "value 2",
            "token_3": "value 3",
            "token_4": "value 4",
            "token_5": "value 5",
        }

        result = _extrapolate_tokens_in_unit_config(config_data, tokens_values)

        self.assertEqual(
            result,
            {
                "form": {
                    "title": "Form title value 1",
                    "instruction": "Form instruction value 2",
                    "sections": [
                        {
                            "name": "section_name",
                            "title": "Section title value 3",
                            "instruction": "Section instruction",
                            "collapsable": False,
                            "initially_collapsed": True,
                            "fieldsets": [
                                {
                                    "title": "Fieldset title value 4",
                                    "instruction": "Fieldset instruction",
                                    "rows": [
                                        {
                                            "fields": [
                                                {
                                                    "help": "Field help value 5",
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
                        "instruction": "Submit instruction value 5",
                        "text": "Submit",
                        "tooltip": "Submit tooltip",
                    },
                },
            },
        )

    def test__validate_tokens_in_both_configs_success(self, *args, **kwargs):
        config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "token_1": "value 1",
                    "token_2": "value 2",
                    "token_3": "value 3",
                    "token_4": "value 4",
                    "token_5": "value 5",
                },
            },
        ]

        (
            overspecified_tokens,
            underspecified_tokens,
            tokens_in_unexpected_attrs_errors,
        ) = _validate_tokens_in_both_configs(config_data, token_sets_values_config_data)

        self.assertEqual(len(overspecified_tokens), 0)
        self.assertEqual(len(underspecified_tokens), 0)
        self.assertEqual(tokens_in_unexpected_attrs_errors, [])

    def test__validate_tokens_in_both_configs_with_errors(self, *args, **kwargs):
        config_data = {
            "form": {
                "title": "Form title",
                "instruction": "Form instruction {{token_2}}",
                "sections": [
                    {
                        "name": "section_name",
                        "title": "Section title {{token_3}}",
                        "instruction": "Section instruction",
                        "collapsable": False,
                        "initially_collapsed": True,
                        "fieldsets": [
                            {
                                "title": "Fieldset title {{token_4}}",
                                "instruction": "Fieldset instruction",
                                "rows": [
                                    {
                                        "fields": [
                                            {
                                                "help": "Field help {{token_5}}",
                                                "id": "id_field {{token_5}}",
                                                "label": "Field label {{token_6}}",
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
                    "instruction": "Submit instruction {{token_5}}",
                    "text": "Submit",
                    "tooltip": "Submit tooltip",
                },
            },
        }
        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "token_1": "value 1",
                    "token_2": "value 2",
                    "token_3": "value 3",
                    "token_4": "value 4",
                    "token_5": "value 5",
                },
            },
        ]

        (
            overspecified_tokens,
            underspecified_tokens,
            tokens_in_unexpected_attrs_errors,
        ) = _validate_tokens_in_both_configs(config_data, token_sets_values_config_data)

        self.assertEqual(overspecified_tokens, {"token_1"})
        self.assertEqual(underspecified_tokens, {"token_6"})
        self.assertEqual(
            tokens_in_unexpected_attrs_errors,
            [
                (
                    "You tried to set tokens 'token_5' in attribute 'id' with value 'id_field "
                    "{{token_5}}'. You can use tokens only in following attributes: help, "
                    "instruction, label, title, tooltip"
                ),
            ],
        )

    def test__combine_extrapolated_unit_configs_success(self, *args, **kwargs):
        config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "token_1": "value 1",
                    "token_2": "value 2",
                    "token_3": "value 3",
                    "token_4": "value 4",
                    "token_5": "value 5",
                },
            },
        ]

        result = _combine_extrapolated_unit_configs(config_data, token_sets_values_config_data)

        self.assertEqual(
            result,
            [
                {
                    "form": {
                        "title": "Form title value 1",
                        "instruction": "Form instruction value 2",
                        "sections": [
                            {
                                "collapsable": False,
                                "fieldsets": [
                                    {
                                        "help": "Fieldset help",
                                        "instruction": "Fieldset instruction",
                                        "rows": [
                                            {
                                                "fields": [
                                                    {
                                                        "help": "Field help value 5",
                                                        "id": "id_field",
                                                        "label": "Field label",
                                                        "name": "field_name",
                                                        "placeholder": "Field placeholder",
                                                        "tooltip": "Field tooltip",
                                                        "type": "file",
                                                        "value": "",
                                                    },
                                                ],
                                                "help": "Row help",
                                            },
                                        ],
                                        "title": "Fieldset title value 4",
                                    },
                                ],
                                "initially_collapsed": True,
                                "instruction": "Section instruction",
                                "name": "section_name",
                                "title": "Section title value 3",
                            },
                        ],
                        "submit_button": {
                            "instruction": "Submit instruction value 5",
                            "text": "Submit",
                            "tooltip": "Submit tooltip",
                        },
                    },
                    "form_metadata": {
                        "tokens_values": {
                            "token_1": "value 1",
                            "token_2": "value 2",
                            "token_3": "value 3",
                            "token_4": "value 4",
                            "token_5": "value 5",
                        }
                    },
                },
            ],
        )

    def test__replace_html_paths_with_html_file_content_success(self, *args, **kwargs):
        value_with_file_path_1 = "insertions/test1.html"
        value_with_file_path_2 = "insertions/test2.html"
        html_content_1 = "<b>Test {{token_1}}</b>"
        html_content_2 = "<b>Test {{token_2}}</b>"

        html_path_1 = os.path.abspath(os.path.join(self.data_dir, value_with_file_path_1))
        html_path_2 = os.path.abspath(os.path.join(self.data_dir, value_with_file_path_2))

        os.makedirs(os.path.dirname(html_path_1), exist_ok=True)
        f = open(html_path_1, "w")
        f.write(html_content_1)
        f.close()
        f = open(html_path_2, "w")
        f.write(html_content_2)
        f.close()

        unit_config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        unit_config_data["form"]["title"] = value_with_file_path_1
        unit_config_data["form"]["instruction"] = value_with_file_path_2

        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "token_1": "value 1",
                    "token_2": "value 2",
                    "token_3": "value 3",
                    "token_4": "value 4",
                    "token_5": "value 5",
                },
            },
        ]

        unit_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        task_data_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__DATA_CONFIG_NAME,
        )

        unit_config_f = open(unit_config_path, "w")
        unit_config_f.write(json.dumps(unit_config_data))
        unit_config_f.close()

        token_sets_values_config_f = open(token_sets_values_config_path, "w")
        token_sets_values_config_f.write(json.dumps(token_sets_values_config_data))
        token_sets_values_config_f.close()

        create_extrapolated_config(
            unit_config_path=unit_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            task_data_config_path=task_data_config_path,
            data_path=self.data_dir,
        )

        f = open(task_data_config_path, "r")
        task_config_data = json.loads(f.read())

        self.assertEqual(
            task_config_data,
            [
                {
                    "form": {
                        "title": "<b>Test value 1</b>",
                        "instruction": "<b>Test value 2</b>",
                        "sections": [
                            {
                                "collapsable": False,
                                "fieldsets": [
                                    {
                                        "help": "Fieldset help",
                                        "instruction": "Fieldset instruction",
                                        "rows": [
                                            {
                                                "fields": [
                                                    {
                                                        "help": "Field help value 5",
                                                        "id": "id_field",
                                                        "label": "Field label",
                                                        "name": "field_name",
                                                        "placeholder": "Field placeholder",
                                                        "tooltip": "Field tooltip",
                                                        "type": "file",
                                                        "value": "",
                                                    },
                                                ],
                                                "help": "Row help",
                                            },
                                        ],
                                        "title": "Fieldset title value 4",
                                    },
                                ],
                                "initially_collapsed": True,
                                "instruction": "Section instruction",
                                "name": "section_name",
                                "title": "Section title value 3",
                            },
                        ],
                        "submit_button": {
                            "instruction": "Submit instruction value 5",
                            "text": "Submit",
                            "tooltip": "Submit tooltip",
                        },
                    },
                    "form_metadata": {
                        "tokens_values": {
                            "token_1": "value 1",
                            "token_2": "value 2",
                            "token_3": "value 3",
                            "token_4": "value 4",
                            "token_5": "value 5",
                        }
                    },
                },
            ],
        )

    def test_create_extrapolated_config_file_not_found(self, *args, **kwargs):
        unit_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        task_data_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__DATA_CONFIG_NAME,
        )

        with self.assertRaises(FileNotFoundError) as cm:
            create_extrapolated_config(
                unit_config_path=unit_config_path,
                token_sets_values_config_path=token_sets_values_config_path,
                task_data_config_path=task_data_config_path,
                data_path=self.data_dir,
            )

        self.assertEqual(
            cm.exception.__str__(),
            f"Create file '{unit_config_path}' with form configuration.",
        )

    def test_create_extrapolated_config_success(self, *args, **kwargs):
        unit_config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "token_1": "value 1",
                    "token_2": "value 2",
                    "token_3": "value 3",
                    "token_4": "value 4",
                    "token_5": "value 5",
                },
            },
        ]

        unit_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        task_data_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__DATA_CONFIG_NAME,
        )

        unit_config_f = open(unit_config_path, "w")
        unit_config_f.write(json.dumps(unit_config_data))
        unit_config_f.close()

        token_sets_values_config_f = open(token_sets_values_config_path, "w")
        token_sets_values_config_f.write(json.dumps(token_sets_values_config_data))
        token_sets_values_config_f.close()

        create_extrapolated_config(
            unit_config_path=unit_config_path,
            token_sets_values_config_path=token_sets_values_config_path,
            task_data_config_path=task_data_config_path,
            data_path=self.data_dir,
        )

        f = open(task_data_config_path, "r")
        task_config_data = json.loads(f.read())

        self.assertEqual(
            task_config_data,
            [
                {
                    "form": {
                        "title": "Form title value 1",
                        "instruction": "Form instruction value 2",
                        "sections": [
                            {
                                "collapsable": False,
                                "fieldsets": [
                                    {
                                        "help": "Fieldset help",
                                        "instruction": "Fieldset instruction",
                                        "rows": [
                                            {
                                                "fields": [
                                                    {
                                                        "help": "Field help value 5",
                                                        "id": "id_field",
                                                        "label": "Field label",
                                                        "name": "field_name",
                                                        "placeholder": "Field placeholder",
                                                        "tooltip": "Field tooltip",
                                                        "type": "file",
                                                        "value": "",
                                                    },
                                                ],
                                                "help": "Row help",
                                            },
                                        ],
                                        "title": "Fieldset title value 4",
                                    },
                                ],
                                "initially_collapsed": True,
                                "instruction": "Section instruction",
                                "name": "section_name",
                                "title": "Section title value 3",
                            },
                        ],
                        "submit_button": {
                            "instruction": "Submit instruction value 5",
                            "text": "Submit",
                            "tooltip": "Submit tooltip",
                        },
                    },
                    "form_metadata": {
                        "tokens_values": {
                            "token_1": "value 1",
                            "token_2": "value 2",
                            "token_3": "value 3",
                            "token_4": "value 4",
                            "token_5": "value 5",
                        }
                    },
                },
            ],
        )

    def test_validate_task_data_config_success(self, *args, **kwargs):
        task_config_data = [deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)]

        result, errors = validate_task_data_config(task_config_data)

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_task_data_config_not_list(self, *args, **kwargs):
        task_config_data = {}

        result, errors = validate_task_data_config(task_config_data)

        self.assertFalse(result)
        self.assertEqual(errors, ["Config must be a JSON Array."])

    def test_validate_task_data_config_errors(self, *args, **kwargs):
        task_config_data = [
            {
                "wrong_key": {},
            }
        ]

        result, errors = validate_task_data_config(task_config_data)

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

    def test_verify_form_composer_configs_errors(self, *args, **kwargs):
        task_data_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__DATA_CONFIG_NAME,
        )
        unit_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        captured_print_output = io.StringIO()
        sys.stdout = captured_print_output
        verify_generator_configs(
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
            "Provided Form Composer config files are invalid:",
            captured_print_output.getvalue(),
        )
        self.assertIn(
            (
                "- Separate token values config is invalid. Errors:\n  "
                "- Config must be a key/value JSON Object.\n\n"
            ),
            captured_print_output.getvalue(),
        )

    def test_verify_form_composer_configs_errors_task_data_config_only(self, *args, **kwargs):
        task_data_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__DATA_CONFIG_NAME,
        )
        unit_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        captured_print_output = io.StringIO()
        sys.stdout = captured_print_output
        verify_generator_configs(
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

    def test_verify_form_composer_configs_success(self, *args, **kwargs):
        task_data_config_data = [deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)]
        unit_config_data = deepcopy(CORRECT_CONFIG_DATA_WITH_TOKENS)
        token_sets_values_config_data = [
            {
                "tokens_values": {
                    "token_1": "value 1",
                    "token_2": "value 2",
                    "token_3": "value 3",
                    "token_4": "value 4",
                    "token_5": "value 5",
                },
            },
        ]

        separate_token_values_config_data = {
            "token_1": [
                "value 1",
            ],
            "token_2": [
                "value 2",
            ],
            "token_3": [
                "value 3",
            ],
            "token_4": [
                "value 4",
            ],
            "token_5": [
                "value 5",
            ],
        }

        task_data_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__DATA_CONFIG_NAME,
        )
        unit_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__UNIT_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
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
        verify_generator_configs(
            task_data_config_path,
            unit_config_path,
            token_sets_values_config_path,
            separate_token_values_config_path,
        )
        sys.stdout = sys.__stdout__

        self.assertIn("All configs are valid.", captured_print_output.getvalue(), "\n")

    @patch(
        "mephisto.generators.generators_utils.config_validation.task_data_config.get_s3_presigned_url"
    )
    def test_prepare_task_config_for_review_app_success(
        self,
        mock_get_s3_presigned_url,
        *args,
        **kwargs,
    ):
        presigned_url_expected = "presigned_url"
        config_data = {
            "form": {
                "title": 'Form title {{getMultiplePresignedUrls("https://example.com/1.jpg")}}',
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

        mock_get_s3_presigned_url.return_value = presigned_url_expected

        result = prepare_task_config_for_review_app(config_data)

        self.assertEqual(
            result,
            {
                "form": {
                    "title": f"Form title {presigned_url_expected}",
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
            },
        )
