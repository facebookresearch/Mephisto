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


class UnitDataStaticView(MethodView):
    @staticmethod
    def _get_filename_by_original_name(unit: Unit, filename: str) -> Union[str, None]:
        agent: Agent = unit.get_assigned_agent()
        if agent:
            unit_parsed_data = agent.state.get_parsed_data()
            outputs = unit_parsed_data.get("outputs", {})
            # In case if there is outdated code that returns `final_submission`
            # under `outputs` key, we should use the value in side `final_submission`
            if "final_submission" in outputs:
                outputs = outputs["final_submission"]
            files_data = outputs.get("files", [])

            for file_data in files_data:
                original_filename = file_data.get("originalname")
                if original_filename == filename:
                    return file_data.get("filename")

        return None

    def get(
        self,
        unit_id: str = None,
        filename: Optional[str] = None,
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

        # Mephisto saves files with its own format of file names,
        # but saves file's original name under key `originalname`,
        # and in `outputs` data it adds only that `originalname`.
        # So this is a shortcut for the UI to get files without parsing data to reach full filename
        filename_by_original_name = self._get_filename_by_original_name(unit, filename)
        if filename_by_original_name:
            filename = filename_by_original_name

        agent = unit.get_assigned_agent()
        if not agent:
            app.logger.debug(f"No agent found for {unit}")
            raise NotFound("File not found")

        unit_data_folder = agent.get_data_dir()
        return send_from_directory(unit_data_folder, filename)
