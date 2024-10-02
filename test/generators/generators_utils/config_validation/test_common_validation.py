#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os.path
import shutil
import tempfile
import unittest

from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    AVAILABLE_CONFIG_ATTRS,
)
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    AVAILABLE_FIELDSET_ATTRS,
)
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    AVAILABLE_FORM_ATTRS,
)
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    AVAILABLE_ROW_ATTRS,
)
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    AVAILABLE_SECTION_ATTRS,
)
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    AVAILABLE_SUBMIT_BUTTON_ATTRS,
)
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    COMMON_AVAILABLE_FIELD_ATTRS,
)
from mephisto.generators.generators_utils.config_validation.common_validation import (
    replace_path_to_file_with_its_content,
)
from mephisto.generators.generators_utils.config_validation.common_validation import (
    validate_config_dict_item,
)


class TestCommonValidation(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        set_form_composer_env_vars(use_validation_mapping_cache=False)

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    # --- Config ---
    def test_validate_config_dict_item_config_success(self, *args, **kwargs):
        errors = []

        config_item = {
            "form": {},
        }

        result = validate_config_dict_item(
            item=config_item,
            item_log_name="config",
            available_attrs=AVAILABLE_CONFIG_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_config_error(self, *args, **kwargs):
        errors = []

        config_item = {}

        result = validate_config_dict_item(
            item=config_item,
            item_log_name="config",
            available_attrs=AVAILABLE_CONFIG_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `config`. Not all required attributes were specified. "
                    "Required attributes: form. Passed attributes: ."
                ),
            ],
        )

    # --- Form ---
    def test_validate_config_dict_item_form_success(self, *args, **kwargs):
        errors = []

        form_item = {
            "title": "Form title",
            "instruction": "Form instruction",
            "sections": [],
            "submit_button": {
                "instruction": "Submit instruction",
                "text": "Submit",
                "tooltip": "Submit tooltip",
            },
        }

        result = validate_config_dict_item(
            item=form_item,
            item_log_name="form",
            available_attrs=AVAILABLE_FORM_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_form_error(self, *args, **kwargs):
        errors = []

        form_item = {
            "title": True,
            "instruction": True,
        }

        result = validate_config_dict_item(
            item=form_item,
            item_log_name="form",
            available_attrs=AVAILABLE_FORM_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `form`. Not all required attributes were specified. "
                    "Required attributes: sections, submit_button, title. "
                    "Passed attributes: title, instruction."
                ),
                "Attribute `title` in object `form` must be `String`.",
                "Attribute `instruction` in object `form` must be `String`.",
            ],
        )

    # --- Submit button ---
    def test_validate_config_dict_item_submit_button_success(self, *args, **kwargs):
        errors = []

        submit_button_item = {
            "instruction": "Submit instruction",
            "text": "Submit text",
            "tooltip": "Submit tooltip",
        }

        result = validate_config_dict_item(
            item=submit_button_item,
            item_log_name="submit_button",
            available_attrs=AVAILABLE_SUBMIT_BUTTON_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_submit_button_error(self, *args, **kwargs):
        errors = []

        submit_button_item = {}

        result = validate_config_dict_item(
            item=submit_button_item,
            item_log_name="submit_button",
            available_attrs=AVAILABLE_SUBMIT_BUTTON_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `submit_button`. Not all required attributes were specified. "
                    "Required attributes: text. Passed attributes: ."
                ),
            ],
        )

    # --- Section ---
    def test_validate_config_dict_item_section_success(self, *args, **kwargs):
        errors = []

        section_item = {
            "name": "section_name",
            "title": "Section title",
            "instruction": "Section instruction",
            "collapsable": False,
            "initially_collapsed": True,
            "fieldsets": [],
        }

        result = validate_config_dict_item(
            item=section_item,
            item_log_name="section",
            available_attrs=AVAILABLE_SECTION_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_section_error(self, *args, **kwargs):
        errors = []

        section_item = {
            "name": True,
            "title": True,
        }

        result = validate_config_dict_item(
            item=section_item,
            item_log_name="section",
            available_attrs=AVAILABLE_SECTION_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `section` with name `True`. "
                    "Not all required attributes were specified. "
                    "Required attributes: fieldsets, title. Passed attributes: name, title."
                ),
                "Attribute `name` in object `section` must be `String`.",
                "Attribute `title` in object `section` must be `String`.",
            ],
        )

    # --- Fieldset ---
    def test_validate_config_dict_item_fieldset_success(self, *args, **kwargs):
        errors = []

        fieldset_item = {
            "title": "Fieldset title",
            "instruction": "Fieldset instruction",
            "rows": [],
            "help": "Fieldset help",
        }

        result = validate_config_dict_item(
            item=fieldset_item,
            item_log_name="fieldset",
            available_attrs=AVAILABLE_FIELDSET_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_fieldset_error(self, *args, **kwargs):
        errors = []

        fieldset_item = {
            "title": True,
            "instruction": True,
        }

        result = validate_config_dict_item(
            item=fieldset_item,
            item_log_name="fieldset",
            available_attrs=AVAILABLE_FIELDSET_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `fieldset`. Not all required attributes were specified. "
                    "Required attributes: rows. Passed attributes: title, instruction."
                ),
                "Attribute `title` in object `fieldset` must be `String`.",
                "Attribute `instruction` in object `fieldset` must be `String`.",
            ],
        )

    # --- Row ---
    def test_validate_config_dict_item_row_success(self, *args, **kwargs):
        errors = []

        row_item = {
            "fields": [],
            "help": "Row help",
        }

        result = validate_config_dict_item(
            item=row_item,
            item_log_name="row",
            available_attrs=AVAILABLE_ROW_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_row_error(self, *args, **kwargs):
        errors = []

        row_item = {}

        result = validate_config_dict_item(
            item=row_item,
            item_log_name="row",
            available_attrs=AVAILABLE_ROW_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `row`. Not all required attributes were specified. "
                    "Required attributes: fields. Passed attributes: ."
                ),
            ],
        )

    # --- Field ---
    def test_validate_config_dict_item_field_success(self, *args, **kwargs):
        errors = []

        field_item = {
            "help": "Field help",
            "id": "id_field",
            "label": "Field label",
            "name": "field_name",
            "placeholder": "Field placeholder",
            "tooltip": "Field tooltip",
            "type": "file",
            "validators": {
                "required": True,
                "minLength": 2,
                "maxLength": 20,
                "regexp": ["^[a-zA-Z0-9._-]+@mephisto\\.ai$", "ig"],
            },
            "value": "",
        }

        result = validate_config_dict_item(
            item=field_item,
            item_log_name="field",
            available_attrs=COMMON_AVAILABLE_FIELD_ATTRS,
            errors=errors,
        )

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_config_dict_item_field_error(self, *args, **kwargs):
        errors = []

        field_item = {
            "id": True,
            "name": True,
            "validators": True,
            "value": "",
        }

        result = validate_config_dict_item(
            item=field_item,
            item_log_name="field",
            available_attrs=COMMON_AVAILABLE_FIELD_ATTRS,
            errors=errors,
        )

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "Object `field` with name `True`. Not all required attributes were specified. "
                    "Required attributes: label, name, type. "
                    "Passed attributes: id, name, validators, value."
                ),
                "Attribute `id` in object `field` must be `String`.",
                "Attribute `name` in object `field` must be `String`.",
                "Attribute `validators` in object `field` must be `Object`.",
            ],
        )

    def test_replace_path_to_file_with_its_content_file_not_found(self, *args, **kwargs):
        value_with_file_path = "insertions/test.html"

        with self.assertRaises(FileNotFoundError) as cm:
            replace_path_to_file_with_its_content(value_with_file_path, self.data_dir)

        self.assertEqual(
            cm.exception.__str__(),
            (
                f"Could not open insertion file "
                f"'{os.path.abspath(os.path.join(self.data_dir, value_with_file_path))}'"
            ),
        )

    def test_replace_path_to_file_with_its_content_success(self, *args, **kwargs):
        value_with_file_path = "insertions/test.html"
        html_content = "<b>Test</b>"

        html_path = os.path.abspath(os.path.join(self.data_dir, value_with_file_path))

        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        f = open(html_path, "w")
        f.write(html_content)
        f.close()

        result = replace_path_to_file_with_its_content(value_with_file_path, self.data_dir)

        self.assertEqual(result, html_content)

    def test_replace_path_to_file_with_its_content_success_value_is_not_file(self, *args, **kwargs):
        value_without_file_path = "<b>Test</b>"

        result = replace_path_to_file_with_its_content(value_without_file_path, self.data_dir)

        self.assertEqual(result, value_without_file_path)
