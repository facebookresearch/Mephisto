#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from json import JSONDecodeError
from typing import Any
from typing import Dict
from typing import List

from omegaconf import DictConfig

from examples.form_composer_demo.data.simple.gold_units.gold_units_validation import (
    validate_gold_unit,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.abstractions.blueprints.mixins.use_gold_unit import get_gold_factory
from mephisto.abstractions.blueprints.mixins.use_gold_unit import UseGoldUnit
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _get_gold_data() -> List[Dict[str, Any]]:
    gold_data_path = os.path.join(
        # Root project directory
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "simple",
        "gold_units",
        "gold_units_data.json",
    )

    try:
        with open(gold_data_path) as config_file:
            gold_data = json.load(config_file)
    except (JSONDecodeError, TypeError) as e:
        print(f"[red]Could not read Gold Unit data from file: '{gold_data_path}': {e}.[/red]")
        exit()

    return gold_data


@task_script(default_config_file="example_local_mock_with_gold_unit")
def main(operator: Operator, cfg: DictConfig) -> None:
    # 1. Build packages
    examples.build_form_composer_simple_with_gold_unit(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    # 2. Prepare ShareState with Gold Units
    gold_data = _get_gold_data()
    shared_state = SharedStaticTaskState(
        get_gold_for_worker=get_gold_factory(gold_data),
        on_unit_submitted=UseGoldUnit.create_validation_function(cfg.mephisto, validate_gold_unit),
    )
    shared_state.qualifications += UseGoldUnit.get_mixin_qualifications(cfg.mephisto, shared_state)

    # 3. Launch TaskRun
    operator.launch_task_run(cfg.mephisto, shared_state=shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
