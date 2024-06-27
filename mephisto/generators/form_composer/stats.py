#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from mephisto.data_model.task import Task
from mephisto.data_model.unit import Unit
from mephisto.tools.data_browser import DataBrowser

FIELD_TYPES_FOR_HISTOGRAM = ["radio", "checkbox", "select"]


def _get_unit_data(data_browser: DataBrowser, unit: Unit) -> dict:
    unit_data = data_browser.get_data_from_unit(unit)

    unit_inputs = unit_data.get("data", {}).get("inputs") or {}
    unit_outputs = unit_data.get("data", {}).get("outputs") or {}
    # In case if there is outdated code that returns `final_submission`
    # under `inputs` and `outputs` keys, we should use the value in side `final_submission`
    if "final_submission" in unit_inputs:
        unit_inputs = unit_inputs["final_submission"]
    if "final_submission" in unit_outputs:
        unit_outputs = unit_outputs["final_submission"]

    return {
        "unit_inputs": unit_inputs,
        "unit_outputs": unit_outputs,
    }


def _get_unit_fields_for_histogram(unit_inputs: dict) -> dict:
    fields = {}
    form_data = unit_inputs["form"]
    for section in form_data["sections"]:
        for fieldset in section["fieldsets"]:
            for row in fieldset["rows"]:
                for field in row["fields"]:
                    if field["type"] in FIELD_TYPES_FOR_HISTOGRAM:
                        fields[field["name"]] = field
    return fields


def _update_data_for_histogram(data: dict, fields: dict, unit_outputs: dict) -> dict:
    for field_name, field in fields.items():
        histogram_name = field["label"]
        prev_histogram_value = data.get(histogram_name, {})

        field_options_to_dict = {o["value"]: o["label"] for o in field["options"]}

        is_multiple = field.get("multiple") is True

        unit_field_result = unit_outputs.get(field_name)

        # Radio
        if isinstance(unit_field_result, dict):
            unit_field_result = [k for k, v in unit_field_result.items() if v is True]
            is_multiple = True

        unit_field_result = unit_field_result if is_multiple else [unit_field_result]
        for option_value, option_name in field_options_to_dict.items():
            prev_option_value = prev_histogram_value.get(option_name, 0)

            plus_worker = 1 if option_value in unit_field_result else 0
            prev_histogram_value[option_name] = prev_option_value + plus_worker

        data[histogram_name] = prev_histogram_value

    return data


def collect_task_stats(task: Task) -> dict:
    data_for_histogram = {}

    data_browser = DataBrowser(db=task.db)

    units: List[Unit] = task.db.find_units(task_id=task.db_id)
    for unit in units:
        unit_data = _get_unit_data(data_browser, unit)
        unit_inputs = unit_data["unit_inputs"]
        unit_outputs = unit_data["unit_outputs"]
        unit_fields_for_histogram = _get_unit_fields_for_histogram(unit_inputs)
        data_for_histogram = _update_data_for_histogram(
            data_for_histogram,
            unit_fields_for_histogram,
            unit_outputs,
        )

    return {
        "stats": data_for_histogram,
        "task_id": task.db_id,
        "task_name": task.task_name,
        "workers_count": len(set(([u.worker_id for u in units]))),
    }


def check_task_has_fields_for_stats(task: Task) -> bool:
    data_browser = DataBrowser(db=task.db)

    units: List[Unit] = task.db.find_units(task_id=task.db_id)
    for unit in units:
        unit_data = _get_unit_data(data_browser, unit)
        unit_inputs = unit_data["unit_inputs"]
        unit_fields_for_histogram = _get_unit_fields_for_histogram(unit_inputs)
        if unit_fields_for_histogram:
            return True

    return False
