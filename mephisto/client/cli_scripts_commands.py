# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import List
from typing import Optional

import click

import mephisto.scripts.form_composer.rebuild_all_apps as rebuild_all_apps_form_composer
import mephisto.scripts.heroku.initialize_heroku as initialize_heroku
import mephisto.scripts.local_db.clear_worker_onboarding as clear_worker_onboarding_local_db
import mephisto.scripts.local_db.load_data_to_mephisto_db as load_data_local_db
import mephisto.scripts.local_db.remove_accepted_tip as remove_accepted_tip_local_db
import mephisto.scripts.local_db.review_feedback_for_task as review_feedback_local_db
import mephisto.scripts.local_db.review_tips_for_task as review_tips_local_db
import mephisto.scripts.metrics.shutdown_metrics as shutdown_metrics
import mephisto.scripts.metrics.view_metrics as view_metrics
import mephisto.scripts.mturk.cleanup as cleanup_mturk
import mephisto.scripts.mturk.identify_broken_units as identify_broken_units_mturk
import mephisto.scripts.mturk.launch_makeup_hits as launch_makeup_hits_mturk
import mephisto.scripts.mturk.print_outstanding_hit_status as soft_block_workers_by_mturk_id_mturk
from mephisto.scripts.local_db import auto_generate_all_docs_reference_md
from mephisto.utils.console_writer import ConsoleWriter

FORM_COMPOSER_VALID_SCRIPTS_NAMES = [
    "rebuild_all_apps",
]
HEROKU_VALID_SCRIPTS_NAMES = [
    "initialize",
]
LOCAL_DB_VALID_SCRIPTS_NAMES = [
    "review_tips",
    "remove_tip",
    "review_feedback",
    "load_data",
    "clear_worker_onboarding",
    "auto_generate_all_docs_reference_md",
]
METRICS_VALID_SCRIPTS_NAMES = [
    "view",
    "shutdown",
]
MTURK_VALID_SCRIPTS_NAMES = [
    "cleanup",
    "identify_broken_units",
    "launch_makeup_hits",
    "print_outstanding_hit_status",
    "soft_block_workers_by_mturk_id",
]
VALID_SCRIPT_TYPES = [
    "local_db",
    "heroku",
    "metrics",
    "mturk",
    "form_composer",
]

logger = ConsoleWriter()


@click.argument("script_type", required=False, nargs=1)
@click.argument("script_name", required=False, nargs=1)
@click.argument("args", nargs=-1)  # Allow arguments for low level commands
def run_script(script_type, script_name, args: Optional[Any] = None):
    """Run one of the many mephisto scripts."""

    def print_non_markdown_list(items: List[str]):
        res = ""
        for item in items:
            res += "\n  * " + item
        return res

    if script_type is None or script_type.strip() not in VALID_SCRIPT_TYPES:
        logger.info("")
        raise click.UsageError(
            "You must specify a valid script_type from below. \n\nValid script types are:"
            + print_non_markdown_list(VALID_SCRIPT_TYPES)
        )
    script_type = script_type.strip()

    script_type_to_scripts_data = {
        "local_db": {
            "valid_script_names": LOCAL_DB_VALID_SCRIPTS_NAMES,
            "scripts": {
                LOCAL_DB_VALID_SCRIPTS_NAMES[0]: review_tips_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[1]: remove_accepted_tip_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[2]: review_feedback_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[3]: load_data_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[4]: clear_worker_onboarding_local_db.main,
                LOCAL_DB_VALID_SCRIPTS_NAMES[5]: auto_generate_all_docs_reference_md.main,
            },
        },
        "heroku": {
            "valid_script_names": HEROKU_VALID_SCRIPTS_NAMES,
            "scripts": {HEROKU_VALID_SCRIPTS_NAMES[0]: initialize_heroku.main},
        },
        "metrics": {
            "valid_script_names": METRICS_VALID_SCRIPTS_NAMES,
            "scripts": {
                METRICS_VALID_SCRIPTS_NAMES[0]: view_metrics.launch_servers,
                METRICS_VALID_SCRIPTS_NAMES[1]: shutdown_metrics.shutdown_servers,
            },
        },
        "mturk": {
            "valid_script_names": MTURK_VALID_SCRIPTS_NAMES,
            "scripts": {
                MTURK_VALID_SCRIPTS_NAMES[0]: cleanup_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[1]: identify_broken_units_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[2]: launch_makeup_hits_mturk.main,
                MTURK_VALID_SCRIPTS_NAMES[3]: rebuild_all_apps_form_composer.main,
                MTURK_VALID_SCRIPTS_NAMES[4]: soft_block_workers_by_mturk_id_mturk.main,
            },
        },
        "form_composer": {
            "valid_script_names": FORM_COMPOSER_VALID_SCRIPTS_NAMES,
            "scripts": {
                FORM_COMPOSER_VALID_SCRIPTS_NAMES[0]: rebuild_all_apps_form_composer.main,
            },
        },
    }

    if script_name is None or (
        script_name not in script_type_to_scripts_data[script_type]["valid_script_names"]
    ):
        logger.info("")
        raise click.UsageError(
            "You must specify a valid script_name from below. \n\nValid script names are:"
            + print_non_markdown_list(
                script_type_to_scripts_data[script_type]["valid_script_names"]
            )
        )

    # runs the script
    script_type_to_scripts_data[script_type]["scripts"][script_name]()
