#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from unittest.mock import patch
from urllib.parse import urljoin

import pytest
from requests import Response
from requests.exceptions import HTTPError

from mephisto.abstractions.providers.prolific.api import status
from mephisto.abstractions.providers.prolific.api.base_api_resource import BaseAPIResource
from mephisto.abstractions.providers.prolific.api.base_api_resource import HTTPMethod
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificAPIKeyError
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificAuthenticationError
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificException
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificRequestError


API_KEY_PATH = "mephisto.abstractions.providers.prolific.api.base_api_resource.PROLIFIC_API_KEY"
API_KEY = "test"


class TestApiResource(BaseAPIResource):
    pass


@pytest.mark.prolific
class TestBaseAPIResource(unittest.TestCase):
    @patch("requests.get")
    def test__base_request_success(self, mock_requests_get, *args):
        method = HTTPMethod.GET
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }
        content = b'{"id": "60d9aadeb86739de712faee0","name": "Study"}'

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_200_OK
        mock_response._content = content

        mock_requests_get.return_value = mock_response

        result = TestApiResource._base_request(
            method=method,
            api_endpoint=api_endpoint,
            params=params,
            headers=headers,
            api_key=API_KEY,
        )

        self.assertEqual(json.loads(content), result)
        mock_requests_get.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={**headers, **{"Authorization": f"Token {API_KEY}"}},
            params=params,
        )

    @patch("requests.get")
    def test__base_request_success_no_content(self, mock_requests_get, *args):
        method = HTTPMethod.GET
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }
        content = None

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_204_NO_CONTENT
        mock_response._content = content

        mock_requests_get.return_value = mock_response

        result = TestApiResource._base_request(
            method=method,
            api_endpoint=api_endpoint,
            params=params,
            headers=headers,
            api_key=API_KEY,
        )

        self.assertEqual(None, result)
        mock_requests_get.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={**headers, **{"Authorization": f"Token {API_KEY}"}},
            params=params,
        )

    @patch(API_KEY_PATH, "")
    @patch("requests.get")
    def test__base_request_no_api_key(self, mock_requests_get, *args):
        method = HTTPMethod.GET
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }

        with self.assertRaises(ProlificAPIKeyError) as cm:
            TestApiResource._base_request(
                method=method,
                api_endpoint=api_endpoint,
                params=params,
                headers=headers,
            )

        self.assertEqual(cm.exception.message, ProlificAPIKeyError.default_message)
        mock_requests_get.assert_not_called()

    @patch("requests.get")
    def test__base_request_incorrect_request_method(self, mock_requests_get, *args):
        method = "unreal_method"
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }

        with self.assertRaises(ProlificException) as cm:
            TestApiResource._base_request(
                method=method,
                api_endpoint=api_endpoint,
                params=params,
                headers=headers,
                api_key=API_KEY,
            )

        self.assertEqual(cm.exception.message, "Invalid HTTP method.")
        mock_requests_get.assert_not_called()

    @patch("requests.get")
    def test__base_request_request_httperror(self, mock_requests_get, *args):
        method = HTTPMethod.GET
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }
        content = b"test"

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_204_NO_CONTENT
        mock_response._content = content

        error_message = "Error"
        exception = HTTPError(error_message)
        exception.response = mock_response

        mock_requests_get.side_effect = exception

        with self.assertRaises(ProlificRequestError) as cm:
            TestApiResource._base_request(
                method=method,
                api_endpoint=api_endpoint,
                params=params,
                headers=headers,
                api_key=API_KEY,
            )

        self.assertEqual(cm.exception.message, f'{error_message}. {content.decode("utf8")}')
        mock_requests_get.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={**headers, **{"Authorization": f"Token {API_KEY}"}},
            params=params,
        )

    @patch("requests.get")
    def test__base_request_request_httperror_unauthorized(self, mock_requests_get, *args):
        method = HTTPMethod.GET
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }
        content = b"test"

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED
        mock_response._content = content

        error_message = "Error"
        exception = HTTPError(error_message)
        exception.response = mock_response

        mock_requests_get.side_effect = exception

        with self.assertRaises(ProlificAuthenticationError) as cm:
            TestApiResource._base_request(
                method=method,
                api_endpoint=api_endpoint,
                params=params,
                headers=headers,
                api_key=API_KEY,
            )

        self.assertEqual(cm.exception.message, ProlificAuthenticationError.default_message)
        self.assertEqual(cm.exception.status_code, ProlificAuthenticationError.status_code)
        mock_requests_get.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={**headers, **{"Authorization": f"Token {API_KEY}"}},
            params=params,
        )

    @patch("requests.get")
    def test__base_request_unexpected_exception(self, mock_requests_get, *args):
        method = HTTPMethod.GET
        api_endpoint = "test/"
        params = {
            "param": "test",
        }
        headers = {
            "header": "test",
        }

        error_message = "Error"
        exception = ValueError(error_message)

        mock_requests_get.side_effect = exception

        with self.assertRaises(ProlificException) as cm:
            TestApiResource._base_request(
                method=method,
                api_endpoint=api_endpoint,
                params=params,
                headers=headers,
                api_key=API_KEY,
            )

        self.assertEqual(cm.exception.message, ProlificException.default_message)
        mock_requests_get.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={**headers, **{"Authorization": f"Token {API_KEY}"}},
            params=params,
        )

    @patch(API_KEY_PATH, API_KEY)
    @patch("requests.get")
    def test_get(self, mock_requests_get, *args):
        api_endpoint = "test-get/"
        params = {
            "param": "test",
        }
        content = b'{"id": "60d9aadeb86739de712faee0","name": "Study"}'

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_200_OK
        mock_response._content = content

        mock_requests_get.return_value = mock_response

        result = TestApiResource.get(api_endpoint=api_endpoint, params=params)

        self.assertEqual(json.loads(content), result)
        mock_requests_get.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={"Authorization": f"Token {API_KEY}"},
            params=params,
        )

    @patch(API_KEY_PATH, API_KEY)
    @patch("requests.post")
    def test_post(self, mock_requests_post, *args):
        api_endpoint = "test-post/"
        params = {
            "param": "test",
        }
        content = b'{"id": "60d9aadeb86739de712faee0","name": "Study"}'

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_200_OK
        mock_response._content = content

        mock_requests_post.return_value = mock_response

        result = TestApiResource.post(api_endpoint=api_endpoint, params=params)

        self.assertEqual(json.loads(content), result)
        mock_requests_post.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={"Authorization": f"Token {API_KEY}"},
            params=params,
        )

    @patch(API_KEY_PATH, API_KEY)
    @patch("requests.patch")
    def test_patch(self, mock_requests_patch, *args):
        api_endpoint = "test-patch/"
        params = {
            "param": "test",
        }
        content = b'{"id": "60d9aadeb86739de712faee0","name": "Study"}'

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_200_OK
        mock_response._content = content

        mock_requests_patch.return_value = mock_response

        result = TestApiResource.patch(api_endpoint=api_endpoint, params=params)

        self.assertEqual(json.loads(content), result)
        mock_requests_patch.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={"Authorization": f"Token {API_KEY}"},
            params=params,
        )

    @patch(API_KEY_PATH, API_KEY)
    @patch("requests.delete")
    def test_delete(self, mock_requests_delete, *args):
        api_endpoint = "test-delete/"
        params = {
            "param": "test",
        }
        content = b'{"id": "60d9aadeb86739de712faee0","name": "Study"}'

        mock_response = Response()
        mock_response.raise_for_status = lambda: None
        mock_response.status_code = status.HTTP_200_OK
        mock_response._content = content

        mock_requests_delete.return_value = mock_response

        result = TestApiResource.delete(api_endpoint=api_endpoint, params=params)

        self.assertEqual(json.loads(content), result)
        mock_requests_delete.called_once_with(
            urljoin("https://api.prolific.co/api/v1/", api_endpoint),
            headers={"Authorization": f"Token {API_KEY}"},
            params=params,
        )


if __name__ == "__main__":
    unittest.main()
