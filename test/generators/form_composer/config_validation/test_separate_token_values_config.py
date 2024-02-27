import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from botocore.exceptions import NoCredentialsError

from mephisto.client.cli import FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME
from mephisto.generators.form_composer.config_validation.separate_token_values_config import (
    update_separate_token_values_config_with_file_urls,
)
from mephisto.generators.form_composer.config_validation.separate_token_values_config import (
    validate_separate_token_values_config,
)


class TestSeparateTokenValuesConfig(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_validate_separate_token_values_config_success(self, *args, **kwargs):
        config_data = {
            "file_location": [
                "https://example.com/1.jpg",
                "https://example.com/2.jpg",
            ],
        }
        result, errors = validate_separate_token_values_config(config_data)

        self.assertTrue(result)
        self.assertEqual(errors, [])

    def test_validate_separate_token_values_config_not_dict(self, *args, **kwargs):
        config_data = []
        result, errors = validate_separate_token_values_config(config_data)

        self.assertFalse(result)
        self.assertEqual(errors, ["Config must be a key/value JSON Object."])

    def test_validate_separate_token_values_config_empty_value_list(self, *args, **kwargs):
        config_data = {
            "file_location": [],
        }
        result, errors = validate_separate_token_values_config(config_data)

        self.assertFalse(result)
        self.assertEqual(
            errors,
            [
                (
                    "You passed empty array of values for token 'file_location'. "
                    "It must contain at least one value or just remove it you left it by mistake."
                ),
            ],
        )

    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "read_config_file"
    )
    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "get_file_urls_from_s3_storage"
    )
    def test_update_separate_token_values_config_with_file_urls_credentials_error(
        self,
        mock_get_file_urls_from_s3_storage,
        mock_read_config_file,
        *args,
        **kwargs,
    ):
        url = "https://test-bucket-private.s3.amazonaws.com/path/"
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        mock_get_file_urls_from_s3_storage.side_effect = NoCredentialsError()

        result = update_separate_token_values_config_with_file_urls(
            url,
            separate_token_values_config_path,
        )

        self.assertIsNone(result)
        mock_read_config_file.assert_not_called()

    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "read_config_file"
    )
    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "get_file_urls_from_s3_storage"
    )
    def test_update_separate_token_values_config_with_file_urls_no_file_locations(
        self,
        mock_get_file_urls_from_s3_storage,
        mock_read_config_file,
        *args,
        **kwargs,
    ):
        url = "https://test-bucket-private.s3.amazonaws.com/path/"
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        mock_get_file_urls_from_s3_storage.return_value = []

        result = update_separate_token_values_config_with_file_urls(
            url,
            separate_token_values_config_path,
        )

        self.assertIsNone(result)
        mock_read_config_file.assert_not_called()

    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "get_file_urls_from_s3_storage"
    )
    def test_update_separate_token_values_config_with_file_urls_success_new_config_file(
        self,
        mock_get_file_urls_from_s3_storage,
        *args,
        **kwargs,
    ):
        url = "https://test-bucket-private.s3.amazonaws.com/path/"
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        mock_get_file_urls_from_s3_storage.return_value = [
            "https://example.com/1.jpg",
            "https://example.com/2.jpg",
        ]

        update_separate_token_values_config_with_file_urls(
            url,
            separate_token_values_config_path,
        )

        f = open(separate_token_values_config_path, "r")
        result_config_data = json.loads(f.read())

        self.assertEqual(
            result_config_data,
            {
                "file_location": [
                    "https://example.com/1.jpg",
                    "https://example.com/2.jpg",
                ],
            },
        )

    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "get_file_urls_from_s3_storage"
    )
    def test_update_separate_token_values_config_with_file_urls_success_updated_config_file(
        self,
        mock_get_file_urls_from_s3_storage,
        *args,
        **kwargs,
    ):
        url = "https://test-bucket-private.s3.amazonaws.com/path/"
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        mock_get_file_urls_from_s3_storage.return_value = [
            "https://example.com/1.jpg",
            "https://example.com/2.jpg",
        ]

        initial_config_data = {
            "some_token": ["value 1", "value 2"],
        }
        f = open(separate_token_values_config_path, "w")
        f.write(json.dumps(initial_config_data))
        f.close()

        update_separate_token_values_config_with_file_urls(
            url,
            separate_token_values_config_path,
        )

        f = open(separate_token_values_config_path, "r")
        result_config_data = json.loads(f.read())

        expected_config_data = {
            "file_location": [
                "https://example.com/1.jpg",
                "https://example.com/2.jpg",
            ],
        }
        expected_config_data.update(initial_config_data)

        self.assertEqual(result_config_data, expected_config_data)

    @patch(
        "mephisto.generators.form_composer.config_validation.separate_token_values_config."
        "get_file_urls_from_s3_storage"
    )
    def test_update_separate_token_values_config_with_file_urls_success_new_config_file_presigned(
        self,
        mock_get_file_urls_from_s3_storage,
        *args,
        **kwargs,
    ):
        url = "https://test-bucket-private.s3.amazonaws.com/path/"
        separate_token_values_config_path = os.path.join(
            self.data_dir,
            FORM_COMPOSER__SEPARATE_TOKEN_VALUES_CONFIG_NAME,
        )

        mock_get_file_urls_from_s3_storage.return_value = [
            "https://example.com/1.jpg",
            "https://example.com/2.jpg",
        ]

        update_separate_token_values_config_with_file_urls(
            url,
            separate_token_values_config_path,
            use_presigned_urls=True,
        )

        f = open(separate_token_values_config_path, "r")
        result_config_data = json.loads(f.read())

        self.assertEqual(
            result_config_data,
            {
                "file_location": [
                    '{{getMultiplePresignedUrls("https://example.com/1.jpg")}}',
                    '{{getMultiplePresignedUrls("https://example.com/2.jpg")}}',
                ],
            },
        )
