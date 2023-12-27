#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.utils.testing import get_test_unit
from mephisto.utils.testing import MOCK_ARCHITECT_ARGS
from mephisto.utils.testing import MOCK_BLUEPRINT_ARGS
from mephisto.utils.testing import MOCK_PROVIDER_ARGS
from mephisto.utils.testing import MOCK_TASK_ARGS
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


def get_mock_config(bundle_js_path: str) -> MephistoConfig:
    blueprint = MOCK_BLUEPRINT_ARGS

    # Override `task_source_review` with just created file in TMP dir
    blueprint.task_source_review = bundle_js_path

    return MephistoConfig(
        provider=MOCK_PROVIDER_ARGS,
        blueprint=blueprint,
        architect=MOCK_ARCHITECT_ARGS,
        task=MOCK_TASK_ARGS,
    )


class TestUnitBundleJSView(BaseTestApiViewCase):
    def test_bundle_js_success(self, *args, **kwargs):
        react_reviewapp_bundle_js_data = "Test JS"

        react_reviewapp_bundle_js_path = f"{self.data_dir}/bundle.js"
        f = open(react_reviewapp_bundle_js_path, "w")
        f.write(react_reviewapp_bundle_js_data)
        f.close()

        # Use just created `bundle.js` file as `task_source_review`.
        # We need this for creating DB objects,
        # because it'll be written in DB and further code uses it from DB
        mock_config = get_mock_config(react_reviewapp_bundle_js_path)
        with patch("mephisto.utils.testing.MOCK_CONFIG", mock_config):
            unit_id = get_test_unit(self.db)

        with self.app_context:
            url = url_for("unit_review_bundle", unit_id=unit_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, react_reviewapp_bundle_js_data.encode())
        self.assertEqual(response.mimetype, "text/javascript")

    def test_bundle_js_not_found_error(self, *args, **kwargs):
        unit_id = get_test_unit(self.db)

        with self.app_context:
            url = url_for("unit_review_bundle", unit_id=unit_id)
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue("error" in response.json)


if __name__ == "__main__":
    unittest.main()
