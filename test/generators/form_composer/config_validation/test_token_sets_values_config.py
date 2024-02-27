import json
import os
import shutil
import tempfile
import unittest

from mephisto.client.cli import FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME
from mephisto.client.cli import FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME
from mephisto.generators.form_composer.config_validation.token_sets_values_config import (
    _premutate_separate_tokens,
)
from mephisto.generators.form_composer.config_validation.token_sets_values_config import (
    update_token_sets_values_config_with_premutated_data,
)
from mephisto.generators.form_composer.config_validation.token_sets_values_config import (
    validate_token_sets_values_config,
)


class TestTokenSetsValuesConfig(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_validate_token_sets_values_config_not_list(self, *args, **kwargs):
        config_data = {}
        result, errors = validate_token_sets_values_config(config_data)

        self.assertFalse(result)
        self.assertEqual(errors, ["Config must be a JSON Array."])

    def test_validate_token_sets_values_config_not_list_with_empty_dicts(self, *args, **kwargs):
        config_data = [{}, {}]
        result, errors = validate_token_sets_values_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                "Config must contain at least one non-empty item.",
                (
                    "Object `item_tokens_values`. Not all required attributes were specified. "
                    "Required attributes: tokens_values. Passed attributes: ."
                ),
                (
                    "Object `item_tokens_values`. Not all required attributes were specified. "
                    "Required attributes: tokens_values. Passed attributes: ."
                ),
            ],
        )

    def test_validate_token_sets_values_config_dissimilar_set_of_tokens(self, *args, **kwargs):
        config_data = [
            {
                "tokens_values": {
                    "token 1": "value 1",
                },
            },
            {
                "tokens_values": {
                    "token 2": "value 2",
                },
            },
        ]
        result, errors = validate_token_sets_values_config(config_data)

        self.assertFalse(result)
        self.assertEqual(errors, ["Some token sets contain dissimilar set of token names."])

    def test_validate_token_sets_values_config_success(self, *args, **kwargs):
        config_data = [
            {
                "tokens_values": {
                    "token 1": "value 1",
                },
            },
            {
                "tokens_values": {
                    "token 1": "value 2",
                },
            },
        ]
        result, errors = validate_token_sets_values_config(config_data)

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test__premutate_separate_tokens_success(self, *args, **kwargs):
        config_data = {
            "token 1": [
                "value 1",
                "value 2",
            ],
        }
        result = _premutate_separate_tokens(config_data)

        self.assertEqual(
            result,
            [
                {
                    "tokens_values": {
                        "token 1": "value 1",
                    },
                },
                {
                    "tokens_values": {
                        "token 1": "value 2",
                    },
                },
            ],
        )

    def test_update_token_sets_values_config_with_premutated_data_error(self, *args, **kwargs):
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )

        initial_config_data = {
            "some_token": [],
        }
        f = open(separate_token_values_config_path, "w")
        f.write(json.dumps(initial_config_data))
        f.close()

        with self.assertRaises(ValueError) as cm:
            update_token_sets_values_config_with_premutated_data(
                separate_token_values_config_path,
                token_sets_values_config_path,
            )

        self.assertEqual(
            cm.exception.__str__(),
            (
                "\nSeparate token values config is invalid. Errors:\n"
                "  - You passed empty array of values for token 'some_token'. It must contain "
                "at least one value or just remove it you left it by mistake."
            ),
        )

    def test_update_token_sets_values_config_with_premutated_data_success(self, *args, **kwargs):
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )
        token_sets_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
        )

        initial_config_data = {
            "some_token": ["value 1", "value 2"],
        }
        f = open(separate_token_values_config_path, "w")
        f.write(json.dumps(initial_config_data))
        f.close()

        update_token_sets_values_config_with_premutated_data(
            separate_token_values_config_path,
            token_sets_values_config_path,
        )

        f = open(token_sets_values_config_path, "r")
        token_sets_values_config_data = json.loads(f.read())

        self.assertEqual(
            token_sets_values_config_data,
            [
                {
                    "tokens_values": {
                        "some_token": "value 1",
                    },
                },
                {
                    "tokens_values": {
                        "some_token": "value 2",
                    },
                },
            ],
        )
