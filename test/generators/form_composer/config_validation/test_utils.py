import json
import os
import shutil
import tempfile
import unittest
from typing import List
from unittest.mock import patch
from urllib.parse import quote

from botocore.exceptions import BotoCoreError

from mephisto.generators.form_composer.config_validation.utils import (
    _get_bucket_and_key_from_S3_url,
)
from mephisto.generators.form_composer.config_validation.utils import _run_and_handle_boto_errors
from mephisto.generators.form_composer.config_validation.utils import get_file_ext
from mephisto.generators.form_composer.config_validation.utils import get_file_urls_from_s3_storage
from mephisto.generators.form_composer.config_validation.utils import get_s3_presigned_url
from mephisto.generators.form_composer.config_validation.utils import is_s3_url
from mephisto.generators.form_composer.config_validation.utils import make_error_message
from mephisto.generators.form_composer.config_validation.utils import read_config_file
from mephisto.generators.form_composer.config_validation.utils import write_config_to_file
from mephisto.generators.form_composer.constants import CONTENTTYPE_BY_EXTENSION


def get_mock_boto_resource(bucket_object_data: List[dict]):
    class FilterObject:
        key: str

        def __init__(self, data):
            self.key = data["key"]

    class MockResource:
        def __init__(self, *args, **kwargs):
            pass

        class Bucket:
            def __init__(self, *args, **kwargs):
                pass

            class objects:
                @staticmethod
                def filter(*args, **kwargs):
                    return [FilterObject(d) for d in bucket_object_data]

    return MockResource


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_write_config_to_file_success(self, *args, **kwargs):
        expected_data = {"test": "value"}

        config_path = os.path.join(self.data_dir, "test.json")
        write_config_to_file(expected_data, config_path)

        f = open(config_path, "r")
        config_data = json.loads(f.read())

        self.assertEqual(config_data, expected_data)

    def test_read_config_file_non_existent_config_path_without_exit(self, *args, **kwargs):
        non_existent_config_path = os.path.join(self.data_dir, "test.json")
        result = read_config_file(non_existent_config_path, exit_if_no_file=False)

        self.assertIsNone(result)

    def test_read_config_file_non_existent_config_path_with_exit(self, *args, **kwargs):
        non_existent_config_path = os.path.join(self.data_dir, "test.json")

        with self.assertRaises(SystemExit):
            read_config_file(non_existent_config_path, exit_if_no_file=True)

    def test_read_config_file_not_json(self, *args, **kwargs):
        config_path = os.path.join(self.data_dir, "test.json")

        f = open(config_path, "w")
        f.write("not JSON")
        f.close()

        with self.assertRaises(SystemExit):
            read_config_file(config_path, exit_if_no_file=True)

    def test_read_config_file_success(self, *args, **kwargs):
        expected_data = {"test": "value"}
        config_path = os.path.join(self.data_dir, "test.json")

        f = open(config_path, "w")
        f.write(json.dumps(expected_data))
        f.close()

        result = read_config_file(config_path, exit_if_no_file=True)

        self.assertEqual(result, expected_data)

    def test_make_error_message_success(self, *args, **kwargs):
        main_message = "Main message"
        error_list = [
            "error 1",
            "error 2",
        ]

        result = make_error_message(
            main_message=main_message,
            error_list=error_list,
            indent=4,
        )

        self.assertEqual(
            result, f"{main_message}. Errors:\n    - {error_list[0]}\n    - {error_list[1]}"
        )

    def test_get_file_ext_success(self, *args, **kwargs):
        result = get_file_ext("/path/file.jpg")

        self.assertEqual(result, "jpg")

    def test__run_and_handle_boto_errors_success(self, *args, **kwargs):
        def fn():
            raise BotoCoreError()

        error_message = "Test"

        with self.assertRaises(BotoCoreError) as cm:
            _run_and_handle_boto_errors(fn, error_message, reraise=True)

        self.assertEqual(cm.exception.__str__(), "An unspecified error occurred")

    def test_is_s3_url_wrong(self, *args, **kwargs):
        result = is_s3_url("https://example.com")

        self.assertFalse(result)

    def test_is_s3_url_success(self, *args, **kwargs):
        result = is_s3_url("https://test-bucket-private.s3.amazonaws.com/path/test.jpg")

        self.assertTrue(result)

    def test__get_bucket_and_key_from_S3_url_success(self, *args, **kwargs):
        expected_bucket_name = "test-bucket-private"
        expected_s3_key = "path/test.jpg"

        bucket_name, s3_key = _get_bucket_and_key_from_S3_url(
            f"https://{expected_bucket_name}.s3.amazonaws.com/{expected_s3_key}",
        )

        self.assertEqual(bucket_name, expected_bucket_name)
        self.assertEqual(s3_key, expected_s3_key)

    def test__get_bucket_and_key_from_S3_url_error(self, *args, **kwargs):
        with self.assertRaises(SystemExit):
            _get_bucket_and_key_from_S3_url(f"https://test-bucket-private.s3.amazonaws.com")

    @patch("boto3.resource")
    def test_get_file_urls_from_s3_storage_success(self, mock_resource, *args, **kwargs):
        s3_url = "https://test-bucket-private.s3.amazonaws.com/path/"

        mock_resource.return_value = get_mock_boto_resource(
            [
                {
                    "key": "path/file1.jpg",
                },
                {
                    "key": "path/file2.jpg",
                },
            ],
        )

        result = get_file_urls_from_s3_storage(s3_url)

        self.assertEqual(
            result,
            [
                "https://test-bucket-private.s3.amazonaws.com/path/file1.jpg",
                "https://test-bucket-private.s3.amazonaws.com/path/file2.jpg",
            ],
        )

    @patch("botocore.signers.RequestSigner.generate_presigned_url")
    def test_get_s3_presigned_url_success(self, mock_generate_presigned_url, *args, **kwargs):
        presigned_url_expected = "presigned_url"

        mock_generate_presigned_url.return_value = presigned_url_expected

        s3_signing_name = "s3"
        s3_key = "path/image.png"
        s3_bucket = "test-bucket-private"
        s3_url = f"https://{s3_bucket}.{s3_signing_name}.amazonaws.com/{s3_key}"
        content_type = CONTENTTYPE_BY_EXTENSION.get("png")

        result = get_s3_presigned_url(s3_url)

        self.assertEqual(result, presigned_url_expected)

        mock_generate_presigned_url.assert_called_with(
            request_dict={
                "url_path": f"/{s3_key}",
                "query_string": {
                    "response-content-type": content_type,
                },
                "method": "GET",
                "headers": {},
                "body": b"",
                "auth_path": f"/{s3_bucket}/{s3_key}",
                "url": f"{s3_url}?response-content-type={quote(content_type, safe='')}",
                "context": {
                    "is_presign_request": True,
                    "use_global_endpoint": True,
                    "s3_redirect": {
                        "redirected": False,
                        "bucket": s3_bucket,
                        "params": {
                            "Bucket": s3_bucket,
                            "Key": s3_key,
                            "ResponseContentType": content_type,
                        },
                    },
                    "S3Express": {
                        "bucket_name": s3_bucket,
                    },
                    "auth_type": "v4",
                    "signing": {
                        "signing_name": s3_signing_name,
                        "disableDoubleEncoding": True,
                    },
                },
            },
            expires_in=3600,
            operation_name="GetObject",
        )

    @patch("botocore.signers.RequestSigner.generate_presigned_url")
    def test_get_s3_presigned_url_error(self, mock_generate_presigned_url, *args, **kwargs):
        mock_generate_presigned_url.side_effect = BotoCoreError()

        s3_url = f"https://test-bucket-private.s3.amazonaws.com/path/image.png"

        with self.assertRaises(BotoCoreError) as cm:
            get_s3_presigned_url(s3_url)

        self.assertEqual(cm.exception.__str__(), "An unspecified error occurred")
