#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Union, Type, Dict, Any, List, TYPE_CHECKING
from mephisto.utils.dirs import get_root_dir, get_provider_dir
from mephisto.operations.hydra_config import register_abstraction_config
import importlib
import os

if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import Blueprint
    from mephisto.abstractions.crowd_provider import CrowdProvider
    from mephisto.abstractions.architect import Architect


BLUEPRINTS: Dict[str, Type["Blueprint"]] = {}
ARCHITECTS: Dict[str, Type["Architect"]] = {}
PROVIDERS: Dict[str, Type["CrowdProvider"]] = {}


def register_mephisto_abstraction():
    """
    Decorator method for classes that extend a mephisto abstraction, used
    to pull Mephisto abstractions out of anywhere that defines them.
    """

    def register_cls(
        base_class: Union[Type["Blueprint"], Type["Architect"], Type["CrowdProvider"]]
    ):
        from mephisto.abstractions.blueprint import Blueprint
        from mephisto.abstractions.crowd_provider import CrowdProvider
        from mephisto.abstractions.architect import Architect

        if issubclass(base_class, Blueprint):
            name = base_class.BLUEPRINT_TYPE
            BLUEPRINTS[name] = base_class
            type_key = "blueprint"
        elif issubclass(base_class, Architect):
            name = base_class.ARCHITECT_TYPE
            ARCHITECTS[name] = base_class
            type_key = "architect"
        elif issubclass(base_class, CrowdProvider):
            name = base_class.PROVIDER_TYPE
            PROVIDERS[name] = base_class
            type_key = "provider"
        else:
            raise AssertionError(
                f"Provided class {base_class} not a child of one of the mephisto "
                "abstractions, expected one of Blueprint, Architect, or CrowdProvider."
            )
        register_abstraction_config(
            name=name, node=base_class.ArgsClass, abstraction_type=type_key
        )
        return base_class

    return register_cls


def uses_mephisto(module: Any):
    """
    Register a module as having defined classes for special Mephisto abstractions.
    Should be put in the __init__.py of the base module.
    """
    # TODO(#653) register the module and file path to the local mephisto registry file
    pass


def fill_registries():
    """
    Ensure that all of the required modules are picked up by the mephisto server
    """
    # TODO(#653) pick up on local file changes such that Mephisto won't need to be
    # restarted to add new abstractions

    # TODO(#653) pass through all of the use_mephisto modules in the local registry file
    # to ensure that all of the modules are added

    # TODO(WISH) these can be made recursive finds with os.walk to pass through subfolders
    # Import Mephisto CrowdProviders
    provider_root = get_provider_dir()
    for dir_name in os.listdir(provider_root):
        provider_dir = os.path.join(provider_root, dir_name)
        if not os.path.isdir(provider_dir):
            continue
        for filename in os.listdir(provider_dir):
            if filename.endswith("provider.py"):
                provider_name = filename[: filename.find(".py")]
                importlib.import_module(
                    f"mephisto.abstractions.providers.{dir_name}.{provider_name}"
                )

    # Import Mephisto Architects
    architect_root = os.path.join(
        get_root_dir(), "mephisto", "abstractions", "architects"
    )
    for filename in os.listdir(architect_root):
        if filename.endswith("architect.py"):
            architect_name = filename[: filename.find(".py")]
            importlib.import_module(
                f"mephisto.abstractions.architects.{architect_name}"
            )
    # After imports are recursive, manage this more cleanly
    importlib.import_module("mephisto.abstractions.architects.ec2.ec2_architect")

    # Import Mephisto Blueprints
    blueprint_root = os.path.join(
        get_root_dir(), "mephisto", "abstractions", "blueprints"
    )
    for dir_name in os.listdir(blueprint_root):
        blueprint_dir = os.path.join(blueprint_root, dir_name)
        if not os.path.isdir(blueprint_dir):
            continue
        for filename in os.listdir(blueprint_dir):
            if filename.endswith("blueprint.py"):
                blueprint_name = filename[: filename.find(".py")]
                importlib.import_module(
                    f"mephisto.abstractions.blueprints.{dir_name}.{blueprint_name}"
                )


def get_crowd_provider_from_type(provider_type: str) -> Type["CrowdProvider"]:
    """Return the crowd provider class for the given string"""
    if provider_type in PROVIDERS:
        return PROVIDERS[provider_type]
    else:
        raise NotImplementedError(
            f"Missing provider type {provider_type}, is it registered?"
        )


def get_blueprint_from_type(task_type: str) -> Type["Blueprint"]:
    """Return the blueprint class for the given string"""
    if task_type in BLUEPRINTS:
        return BLUEPRINTS[task_type]
    else:
        raise NotImplementedError(
            f"Missing blueprint type {task_type}, is it registered?"
        )


def get_architect_from_type(architect_type: str) -> Type["Architect"]:
    """Return the architect class for the given string"""
    if architect_type in ARCHITECTS:
        return ARCHITECTS[architect_type]
    else:
        raise NotImplementedError(
            f"Missing architect type {architect_type}, is it registered?"
        )


def get_valid_provider_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    return list(PROVIDERS.keys())


def get_valid_blueprint_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    return list(BLUEPRINTS.keys())


def get_valid_architect_types() -> List[str]:
    """
    Return the valid provider types that are currently supported by
    the mephisto framework
    """
    return list(ARCHITECTS.keys())
