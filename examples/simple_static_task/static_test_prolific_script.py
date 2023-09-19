#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.data_model.qualification import QUAL_GREATER_EQUAL
from mephisto.tools.scripts import task_script
from mephisto.utils.qualifications import make_qualification_dict


@task_script(default_config_file="prolific_example")
def main(operator, cfg: DictConfig) -> None:
    shared_state = SharedStaticTaskState()

    # Mephisto qualifications
    # shared_state.qualifications = [
    #     make_qualification_dict('sample_qual_name', QUAL_GREATER_EQUAL, 1),
    # ]

    # Prolific qualifications
    # Note that we'll prefix names with a customary `web.eligibility.models.` later in the code
    shared_state.prolific_specific_qualifications = [
        {
            "name": "AgeRangeEligibilityRequirement",
            "min_age": 18,
            "max_age": 100,
        },
    ]

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
