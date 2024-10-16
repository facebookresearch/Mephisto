#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.client.cli_form_composer_commands import set_form_composer_env_vars
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit
from mephisto.generators.form_composer.config_validation.config_validation_constants import (
    FORM_COMPOSER_TASK_TAG,
)
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    prepare_task_config_for_review_app,
)
from mephisto.generators.video_annotator.config_validation.config_validation_constants import (
    VIDEO_ANNOTATOR_TASK_TAG,
)
from mephisto.review_app.server.utils.video_annotator import convert_annotation_tracks_to_webvtt


def _find_worker_reviews(
    db: LocalMephistoDB,
    unit_id: str,
) -> List[dict]:
    """Return all unit reviews for unit"""

    with db.table_access_condition:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute(
            f"""
            SELECT
                blocked_worker,
                bonus,
                creation_date,
                qualification_name,
                review_note,
                revoked_qualification_id,
                status,
                updated_qualification_id,
                updated_qualification_value
            FROM worker_review AS wr
            LEFT JOIN (
                SELECT
                    qualification_id,
                    qualification_name
                FROM qualifications
            ) AS q ON (
                (
                    wr.updated_qualification_id = q.qualification_id AND
                    wr.revoked_qualification_id IS NULL
                )
                OR
                (
                    wr.revoked_qualification_id = q.qualification_id AND
                    wr.updated_qualification_id IS NULL
                )
            )
            WHERE unit_id = ?1
            ORDER BY creation_date DESC;
            """,
            [unit_id],
        )
        rows = c.fetchall()

        worker_reviews = [
            {
                "blocked_worker": r["blocked_worker"],
                "bonus": r["bonus"],
                "creation_date": r["creation_date"],
                "qualification_id": r["updated_qualification_id"] or ["revoked_qualification_id"],
                "qualification_name": r["qualification_name"],
                "review_note": r["review_note"],
                "status": r["status"],
                "value": r["updated_qualification_value"],
            }
            for r in rows
        ]
        return worker_reviews


class UnitsDetailsView(MethodView):
    def get(self) -> dict:
        """Get full input for specified workers results (`unit_ids` is mandatory)"""

        unit_ids: Optional[str] = request.args.get("unit_ids")

        app.logger.debug(f"Params: {unit_ids=}")

        # Parse `unit_ids`
        if unit_ids:
            try:
                unit_ids: List[int] = [int(i.strip()) for i in unit_ids.split(",")]
            except ValueError:
                raise BadRequest("`unit_ids` must be a comma-separated list of integers.")

        # Validate params
        if not unit_ids:
            raise BadRequest("`unit_ids` parameter must be specified.")

        # Get units
        db_units: List[Unit] = app.db.find_units()

        # Prepare response
        units = []
        for unit in db_units:
            if unit_ids and int(unit.db_id) not in unit_ids:
                continue

            try:
                unit_data = app.data_browser.get_data_from_unit(unit)
            except AssertionError:
                # In case if this is Expired Unit. It raises and axceptions
                unit_data = {}

            task_run: TaskRun = unit.get_task_run()
            has_task_source_review = bool(task_run.args.get("blueprint").get("task_source_review"))

            # Initial task data and data that user submitted
            inputs = unit_data.get("data", {}).get("inputs") or {}
            outputs = unit_data.get("data", {}).get("outputs") or {}

            # Get Task tags
            task_tags = task_run.args.get("task").get("task_tags") or ""
            is_form_composer_task = FORM_COMPOSER_TASK_TAG in task_tags
            is_video_annotator_task = VIDEO_ANNOTATOR_TASK_TAG in task_tags

            # In case if there is outdated code that returns `final_submission`
            # under `inputs` and `outputs` keys, we should use the value in side `final_submission`
            if "final_submission" in inputs:
                inputs = inputs["final_submission"]
            if "final_submission" in outputs:
                outputs = outputs["final_submission"]

            # Perform any dynamic action on task config for current unit
            # to make it the same as it looked like for a worker
            prepared_inputs = inputs
            if is_form_composer_task:
                set_form_composer_env_vars(use_validation_mapping_cache=False)
                prepared_inputs = prepare_task_config_for_review_app(inputs)

            # Prepare metadata
            metadata = unit_data.get("metadata", {})
            if is_video_annotator_task:
                task_name = task_run.get_task().task_name
                metadata["webvtt"] = convert_annotation_tracks_to_webvtt(task_name, inputs, outputs)

            metadata["worker_reviews"] = _find_worker_reviews(app.db, unit.db_id)

            # Get Unit data path
            agent = unit.get_assigned_agent()
            unit_data_folder = agent.get_data_dir() if agent else None

            units.append(
                {
                    "has_task_source_review": has_task_source_review,
                    "id": unit.db_id,
                    "inputs": inputs,  # instructions for worker
                    "metadata": metadata,
                    "outputs": outputs,  # response from worker
                    "prepared_inputs": prepared_inputs,  # prepared instructions from worker
                    "unit_data_folder": unit_data_folder,  # path to data dir in file system
                }
            )

        return {
            "units": units,
        }
