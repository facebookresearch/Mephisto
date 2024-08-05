#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script for an easy rebuild of all FormComposer-related apps/packages (`build` and `node_modules`):
    - examples
    - generators
    - Review App
    - react packages

This is needed due to inter-dependency of Mephisto's rapidly evolving JS components.

To run this command:
    mephisto scripts form_composer rebuild_all_apps
"""

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

    packages.clean_mephisto_task_multipart_package(remove_package_locks, verbose=verbose)
    packages.clean_mephisto_task_addons_package(remove_package_locks, verbose=verbose)
    packages.clean_react_form_composer_package(remove_package_locks, verbose=verbose)

    generators.clean_form_composer_generator(remove_package_locks, verbose=verbose)

    review_app.clean_review_app(remove_package_locks, verbose=verbose)

    examples.clean_form_composer_demo(remove_package_locks, verbose=verbose)

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

    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_mephisto_task_addons_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_react_form_composer_package(force_rebuild=force_rebuild, verbose=verbose)

    generators.build_form_composer_generator(force_rebuild=force_rebuild, verbose=verbose)

    review_app.build_review_app_ui(force_rebuild=force_rebuild, verbose=verbose)

    examples.build_form_composer_dynamic(force_rebuild=force_rebuild)

    if verbose:
        logger.info("[green]Finished building web apps successfully![/green]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scripts")
    parser.add_argument("form_composer")
    parser.add_argument("rebuild_all_apps")
    parser.add_argument("--rebuild-package-locks", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    _clean(remove_package_locks=args.rebuild_package_locks)
    _build()


if __name__ == "__main__":
    main()
