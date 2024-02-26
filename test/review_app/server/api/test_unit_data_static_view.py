#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from flask import url_for

from mephisto.abstractions.providers.prolific.api import status
from mephisto.data_model.agent import Agent
from mephisto.utils.testing import get_test_agent
from mephisto.utils.testing import get_test_unit
from test.review_app.server.api.base_test_api_view_case import BaseTestApiViewCase


class TestUnitDataStaticView(BaseTestApiViewCase):
    def test_unit_data_static_no_agent_not_found_error(self, *args, **kwargs):
        unit_id = get_test_unit(self.db)
        with self.app_context:
            url = url_for("unit_data_static", unit_id=unit_id, filename="wrong.filename")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(result["error"], "File not found")

    @patch("mephisto.data_model.unit.Unit.get_assigned_agent")
    def test_unit_data_static_with_agent_not_found_error(
        self,
        mock_get_assigned_agent,
        *args,
        **kwargs,
    ):
        unit_id = get_test_unit(self.db)
        agent_id = get_test_agent(self.db, unit_id=unit_id)

        mock_get_assigned_agent.return_value = Agent.get(self.db, agent_id)

        with self.app_context:
            url = url_for("unit_data_static", unit_id=unit_id, filename="wrong.filename")
            response = self.client.get(url)
            result = response.json

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            result["error"],
            "The requested URL was not found on the server. "
            "If you entered the URL manually please check your spelling and try again.",
        )

    @patch("mephisto.data_model.agent.Agent.get_data_dir")
    @patch("mephisto.data_model.unit.Unit.get_assigned_agent")
    def test_unit_data_static_success_with_filename_from_fs(
        self,
        mock_get_assigned_agent,
        mock_get_data_dir,
        *args,
        **kwargs,
    ):
        unit_id = get_test_unit(self.db)
        agent_id = get_test_agent(self.db, unit_id=unit_id)

        mock_get_assigned_agent.return_value = Agent.get(self.db, agent_id)
        mock_get_data_dir.return_value = self.data_dir

        filename_from_fs = "file.txt"
        txt_file = f"{self.data_dir}/{filename_from_fs}"
        f = open(txt_file, "w")
        f.write("")
        f.close()

        with self.app_context:
            url = url_for("unit_data_static", unit_id=unit_id, filename=filename_from_fs)
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, b"")

    @patch("mephisto.abstractions._subcomponents.agent_state.AgentState.get_parsed_data")
    @patch("mephisto.data_model.agent.Agent.get_data_dir")
    @patch("mephisto.data_model.unit.Unit.get_assigned_agent")
    def test_unit_data_static_success_with_filename_by_original_name(
        self,
        mock_get_assigned_agent,
        mock_get_data_dir,
        mock_get_parsed_data,
        *args,
        **kwargs,
    ):
        unit_id = get_test_unit(self.db)
        agent_id = get_test_agent(self.db, unit_id=unit_id)
        agent = Agent.get(self.db, agent_id)

        mock_get_assigned_agent.return_value = agent
        mock_get_data_dir.return_value = self.data_dir

        filename_original_name = "original_file.txt"
        filename_from_fs = "file.txt"
        txt_file = f"{self.data_dir}/{filename_from_fs}"
        f = open(txt_file, "w")
        f.write("")
        f.close()

        mock_get_parsed_data.return_value = {
            "inputs": {},
            "outputs": {
                "files": [
                    {
                        "originalname": filename_original_name,
                        "filename": filename_from_fs,
                    },
                ],
            },
        }

        with self.app_context:
            url = url_for("unit_data_static", unit_id=unit_id, filename=filename_original_name)
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, b"")


if __name__ == "__main__":
    unittest.main()
