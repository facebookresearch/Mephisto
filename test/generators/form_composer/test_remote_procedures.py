import unittest
from unittest.mock import patch
from urllib.parse import quote

from mephisto.generators.form_composer.constants import CONTENTTYPE_BY_EXTENSION
from mephisto.generators.form_composer.remote_procedures import _get_multiple_presigned_urls
from mephisto.generators.form_composer.remote_procedures import _get_presigned_url
from mephisto.generators.form_composer.remote_procedures import _get_presigned_url_for_thread


class TestRemoteProcedures(unittest.TestCase):
    @patch("botocore.signers.RequestSigner.generate_presigned_url")
    def test__get_presigned_url_success(self, mock_generate_presigned_url, *args, **kwargs):
        presigned_url_expected = "presigned_url"

        mock_generate_presigned_url.return_value = presigned_url_expected

        s3_signing_name = "s3"
        s3_key = "path/image.png"
        s3_bucket = "test-bucket-private"
        s3_url = f"https://{s3_bucket}.{s3_signing_name}.amazonaws.com/{s3_key}"
        content_type = CONTENTTYPE_BY_EXTENSION.get("png")

        url = _get_presigned_url(
            "random-string",
            s3_url,
            None,
        )

        self.assertEqual(url, presigned_url_expected)
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

    def test__get_presigned_url_for_thread_not_s3_url_error(self, *args, **kwargs):
        test_url = "https://any.other/url"

        url, presigned_url, error = _get_presigned_url_for_thread(test_url)

        self.assertEqual(url, test_url)
        self.assertIsNone(presigned_url)
        self.assertEqual(error, f"Not a valid S3 URL: '{test_url}'")

    @patch("mephisto.generators.form_composer.remote_procedures.get_s3_presigned_url")
    def test__get_presigned_url_for_thread_exception(
        self,
        mock_get_s3_presigned_url,
        *args,
        **kwargs,
    ):
        test_url = "https://test-bucket-private.s3.amazonaws.com/path/image.png"

        mock_get_s3_presigned_url.side_effect = Exception("Error")

        url, presigned_url, error = _get_presigned_url_for_thread(test_url)

        self.assertEqual(url, test_url)
        self.assertIsNone(presigned_url)
        self.assertEqual(error, "Error")

    @patch("mephisto.generators.form_composer.remote_procedures.get_s3_presigned_url")
    def test__get_presigned_url_for_thread_success(
        self,
        mock_get_s3_presigned_url,
        *args,
        **kwargs,
    ):
        presigned_url_expected = "presigned_url"
        test_url = "https://test-bucket-private.s3.amazonaws.com/path/image.png"

        mock_get_s3_presigned_url.return_value = presigned_url_expected

        url, presigned_url, error = _get_presigned_url_for_thread(test_url)

        self.assertEqual(url, test_url)
        self.assertEqual(presigned_url, presigned_url_expected)
        self.assertIsNone(error)

    @patch("mephisto.generators.form_composer.remote_procedures.get_s3_presigned_url")
    def test__get_multiple_presigned_urls_errors(
        self,
        mock_get_s3_presigned_url,
        *args,
        **kwargs,
    ):
        test_url = "https://test-bucket-private.s3.amazonaws.com/path/image.png"

        mock_get_s3_presigned_url.side_effect = Exception("Error")

        with self.assertRaises(ValueError) as cm:
            _get_multiple_presigned_urls("random-string", [test_url], None)

        self.assertEqual(
            cm.exception.__str__(),
            f"Could not presign URL '{test_url}' because of error: Error.",
        )

    @patch("mephisto.generators.form_composer.remote_procedures.get_s3_presigned_url")
    def test__get_multiple_presigned_urls_success(
        self,
        mock_get_s3_presigned_url,
        *args,
        **kwargs,
    ):
        presigned_url_expected = "presigned_url"
        test_url = "https://test-bucket-private.s3.amazonaws.com/path/image.png"

        mock_get_s3_presigned_url.return_value = presigned_url_expected

        result = _get_multiple_presigned_urls("random-string", [test_url], None)

        self.assertEqual(result, [(test_url, presigned_url_expected)])
