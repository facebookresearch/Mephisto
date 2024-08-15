#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse

from mephisto.tools.building_react_apps import examples
from mephisto.tools.building_react_apps import generators
from mephisto.tools.building_react_apps import packages
from mephisto.tools.building_react_apps import review_app
from mephisto.utils.console_writer import ConsoleWriter

logger = ConsoleWriter()


def _clean(remove_package_locks: bool):
    verbose = True

    if verbose:
        logger.info("[blue]Started cleaning up all `build` and `node_modules` directories[/blue]")

    # TODO: --- Cannot be built (maybe outdated configs). Fix and uncomment later ---
    # packages.clean_annotated_bbox_package(remove_package_locks, verbose=verbose)
    # packages.clean_annotated_keypoint_package(remove_package_locks, verbose=verbose)
    # packages.clean_annotated_shell_package(remove_package_locks, verbose=verbose)
    # packages.clean_annotated_video_player_package(remove_package_locks, verbose=verbose)
    # packages.clean_annotation_toolkit_package(remove_package_locks, verbose=verbose)
    # packages.clean_mephisto_review_hook_package(remove_package_locks, verbose=verbose)
    # TODO: --- End ---
    packages.clean_bootstrap_chat_package(remove_package_locks, verbose=verbose)
    packages.clean_global_context_store_package(remove_package_locks, verbose=verbose)
    packages.clean_mephisto_task_package(remove_package_locks, verbose=verbose)
    packages.clean_mephisto_task_multipart_package(remove_package_locks, verbose=verbose)
    packages.clean_mephisto_task_addons_package(remove_package_locks, verbose=verbose)
    packages.clean_mephisto_worker_addons_package(remove_package_locks, verbose=verbose)
    packages.clean_react_form_composer_package(remove_package_locks, verbose=verbose)

    generators.clean_form_composer_generator(remove_package_locks, verbose=verbose)

    review_app.clean_review_app(remove_package_locks, verbose=verbose)

    examples.clean_form_composer_demo(remove_package_locks, verbose=verbose)
    examples.clean_parlai_chat_task_demo(remove_package_locks, verbose=verbose)
    examples.clean_remote_procedure_mnist(remove_package_locks, verbose=verbose)
    examples.clean_remote_procedure_template(remove_package_locks, verbose=verbose)
    examples.clean_remote_procedure_toxicity_detection(remove_package_locks, verbose=verbose)
    examples.clean_static_react_task(remove_package_locks, verbose=verbose)
    examples.clean_static_react_task_with_worker_opinion(remove_package_locks, verbose=verbose)

    if verbose:
        logger.info(
            "[green]"
            "Finished cleaning up all `build` and `node_modules` directories successfully!"
            "[/green]"
        )


def _build():
    force_rebuild = True
    verbose = True

    if verbose:
        logger.info("[blue]Started building web apps[/blue]")

    # TODO: --- Cannot be built (maybe outdated configs). Fix and uncomment later ---
    # packages.build_annotated_bbox_package(force_rebuild=force_rebuild, verbose=verbose)
    # packages.build_annotated_keypoint_package(force_rebuild=force_rebuild, verbose=verbose)
    # packages.build_annotated_shell_package(force_rebuild=force_rebuild, verbose=verbose)
    # packages.build_annotated_video_player_package(force_rebuild=force_rebuild, verbose=verbose)
    # packages.build_annotation_toolkit_package(force_rebuild=force_rebuild, verbose=verbose)
    # packages.build_mephisto_review_hook_package(force_rebuild=force_rebuild, verbose=verbose)
    # TODO: --- End ---
    packages.build_bootstrap_chat_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_global_context_store_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_mephisto_task_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_mephisto_worker_addons_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_react_form_composer_package(force_rebuild=force_rebuild, verbose=verbose)

    generators.build_form_composer_generator(force_rebuild=force_rebuild, verbose=verbose)

    review_app.build_review_app_ui(force_rebuild=force_rebuild, verbose=verbose)

    examples.build_form_composer_simple(force_rebuild=force_rebuild)
    examples.build_form_composer_dynamic(force_rebuild=force_rebuild)
    examples.build_form_composer_dynamic_presigned_urls_ec2_prolific(force_rebuild=force_rebuild)
    examples.build_parlai_chat_task_demo(force_rebuild=force_rebuild)
    examples.build_remote_procedure_mnist(force_rebuild=force_rebuild)
    examples.build_remote_procedure_template(force_rebuild=force_rebuild)
    examples.build_remote_procedure_toxicity_detection(force_rebuild=force_rebuild)
    examples.build_static_react_task(force_rebuild=force_rebuild)
    examples.build_static_react_task_with_worker_opinion(force_rebuild=force_rebuild)

    if verbose:
        logger.info("[green]Finished building web apps successfully![/green]")


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("scripts")
    parser.add_argument("tests")
    parser.add_argument("clean")
    parser.add_argument("--rebuild-package-locks", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    return args


def clean():
    args = _parse_arguments()
    _clean(remove_package_locks=args.rebuild_package_locks)


def build():
    _build()


def rebuild():
    clean()
    build()


if __name__ == "__main__":
    rebuild()
