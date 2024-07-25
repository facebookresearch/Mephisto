#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional
from typing import Union

from flask import current_app as app
from flask import Response
from flask import send_from_directory
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from mephisto.data_model.agent import Agent
from mephisto.data_model.unit import Unit


class UnitDataStaticByFieldNameView(MethodView):
    @staticmethod
    def _get_filename_by_fieldname(agent: Agent, fieldname: str) -> Union[str, None]:
        unit_parsed_data = agent.state.get_parsed_data()
        outputs = unit_parsed_data.get("outputs") or {}
        # In case if there is outdated code that returns `final_submission`
        # under `outputs` key, we should use the value in side `final_submission`
        if "final_submission" in outputs:
            outputs = outputs["final_submission"]

        files_data = outputs.get("filesByFields", {})
        file_data = files_data.get(fieldname)
        if file_data:
            if isinstance(file_data, dict):
                # Deprecated logic, but it can be needed for already existing Tasks
                return file_data.get("filename")
            elif isinstance(file_data, list):
                # TODO: Make this work with more than one file. For now it returns only first one
                return file_data[0].get("filename")

        return None

    def get(
        self,
        unit_id: str = None,
        fieldname: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Union[Response, dict]:
        """
        Return static file from `data` directory for specific unit.

        It can return files by name from file system (auto generated name) or
        by original name (that name with what user uploaded a file)
        """
        unit: Unit = Unit.get(app.db, str(unit_id))
        app.logger.debug(f"Found Unit in DB: {unit}")

        agent = unit.get_assigned_agent()
        if not agent:
            app.logger.debug(f"No agent found for {unit}")
            raise NotFound("File not found")

        filename = self._get_filename_by_fieldname(agent, fieldname)
        if not filename:
            raise NotFound("File not found")

        unit_data_folder = agent.get_data_dir()
        return send_from_directory(unit_data_folder, filename)
