#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

from mephisto.generators.generators_utils.config_validation.utils import (
    set_custom_triggers_js_env_var,
)
from mephisto.generators.generators_utils.config_validation.utils import (
    set_custom_validators_js_env_var,
)
from mephisto.tools.scripts import build_custom_bundle
from mephisto.utils.console_writer import ConsoleWriter
from . import packages
from .utils import clean_single_react_app

REPO_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
EXAMPLES_PATH = os.path.join(REPO_PATH, "examples")
FORM_COMPOSER_EXAMPLE_PATH = os.path.join(EXAMPLES_PATH, "form_composer_demo")
VIDEO_ANNOTATOR_EXAMPLE_PATH = os.path.join(EXAMPLES_PATH, "video_annotator_demo")
PARLAI_CHAT_TASK_EXAMPLE_PATH = os.path.join(EXAMPLES_PATH, "parlai_chat_task_demo")
REMOTE_PROCEDURE_MNIST_EXAMPLE_PATH = os.path.join(EXAMPLES_PATH, "remote_procedure", "mnist")
REMOTE_PROCEDURE_TEMPLATE_EXAMPLE_PATH = os.path.join(EXAMPLES_PATH, "remote_procedure", "template")
REMOTE_PROCEDURE_TOXICITY_DETECTION_EXAMPLE_PATH = os.path.join(
    EXAMPLES_PATH,
    "remote_procedure",
    "toxicity_detection",
)
STATIC_REACT_TASK_EXAMPLE_PATH = os.path.join(EXAMPLES_PATH, "static_react_task")
STATIC_REACT_TASK_WITH_WORKER_OPINION_EXAMPLE_PATH = os.path.join(
    EXAMPLES_PATH,
    "static_react_task_with_worker_opinion",
)

logger = ConsoleWriter()


# --- Form Composer ---


def clean_form_composer_demo(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(FORM_COMPOSER_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def build_form_composer_simple(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=True)

    # Build Review UI for the application
    build_custom_bundle(
        FORM_COMPOSER_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:simple:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        FORM_COMPOSER_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="dev:simple",
    )


def build_form_composer_simple_with_gold_unit(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    build_form_composer_simple(
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
    )


def build_form_composer_simple_with_onboarding(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    build_form_composer_simple(
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
    )


def build_form_composer_simple_with_screening(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    build_form_composer_simple(
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
    )


def build_form_composer_dynamic(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=True)

    # Set env vars for `custom_validators.js` and `custom_triggers.js`
    from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME

    data_path = os.path.join(FORM_COMPOSER_EXAMPLE_PATH, FORM_COMPOSER__DATA_DIR_NAME, "dynamic")
    set_custom_validators_js_env_var(data_path)
    set_custom_triggers_js_env_var(data_path)

    # Build Review UI for the application
    build_custom_bundle(
        FORM_COMPOSER_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        FORM_COMPOSER_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        post_install_script=post_install_script,
        build_command="dev",
    )


def build_form_composer_dynamic_ec2_mturk_sandbox(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    build_form_composer_dynamic(
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
    )


def build_form_composer_dynamic_ec2_prolific(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    build_form_composer_dynamic(
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
    )


def build_form_composer_dynamic_presigned_urls_ec2_prolific(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=True)

    # Build Review UI for the application
    build_custom_bundle(
        FORM_COMPOSER_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        FORM_COMPOSER_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="build:presigned_urls",
    )


# --- Video Annotator ---


def clean_video_annotator_demo(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(VIDEO_ANNOTATOR_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def build_video_annotator_simple(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=True)

    # Build Review UI for the application
    build_custom_bundle(
        VIDEO_ANNOTATOR_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:simple:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        VIDEO_ANNOTATOR_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="dev:simple",
    )


def build_video_annotator_dynamic(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=True)

    # Set env vars for `custom_validators.js` and `custom_triggers.js`
    from mephisto.client.cli_video_annotator_commands import VIDEO_ANNOTATOR__DATA_DIR_NAME

    data_path = os.path.join(
        VIDEO_ANNOTATOR_EXAMPLE_PATH, VIDEO_ANNOTATOR__DATA_DIR_NAME, "dynamic"
    )
    set_custom_validators_js_env_var(data_path)
    set_custom_triggers_js_env_var(data_path)

    # Build Review UI for the application
    build_custom_bundle(
        VIDEO_ANNOTATOR_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        VIDEO_ANNOTATOR_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        post_install_script=post_install_script,
        build_command="dev",
    )


# --- Parlai Chat ---


def clean_parlai_chat_task_demo(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(PARLAI_CHAT_TASK_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def build_parlai_chat_task_demo(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    # Build Task UI for the application
    build_custom_bundle(
        PARLAI_CHAT_TASK_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        post_install_script=post_install_script,
        build_command="dev",
    )


# --- Remote Procedure ---


def clean_remote_procedure_mnist(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(REMOTE_PROCEDURE_MNIST_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def clean_remote_procedure_template(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(REMOTE_PROCEDURE_TEMPLATE_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def clean_remote_procedure_toxicity_detection(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(REMOTE_PROCEDURE_TOXICITY_DETECTION_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def build_remote_procedure_mnist(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)

    # Build Review UI for the application
    build_custom_bundle(
        REMOTE_PROCEDURE_MNIST_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        REMOTE_PROCEDURE_MNIST_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="dev",
    )


def build_remote_procedure_template(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)

    # Build Task UI for the application
    build_custom_bundle(
        REMOTE_PROCEDURE_TEMPLATE_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="dev",
    )


def build_remote_procedure_toxicity_detection(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)

    # Build Task UI for the application
    build_custom_bundle(
        REMOTE_PROCEDURE_TOXICITY_DETECTION_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="dev",
    )


# --- Static React Task ---


def clean_static_react_task(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(STATIC_REACT_TASK_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def build_static_react_task(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)

    # Build Task UI for the application
    build_custom_bundle(
        STATIC_REACT_TASK_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
    )


# --- Static React Task with Worker Opinion ---


def clean_static_react_task_with_worker_opinion(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(STATIC_REACT_TASK_WITH_WORKER_OPINION_EXAMPLE_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


def build_static_react_task_with_worker_opinion(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=True)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=True)

    # Build Task UI for the application
    build_custom_bundle(
        STATIC_REACT_TASK_WITH_WORKER_OPINION_EXAMPLE_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        build_command="dev",
    )
