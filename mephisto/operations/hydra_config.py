#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from hydra.core.config_store import ConfigStoreWithProvider
from mephisto.abstractions.blueprint import BlueprintArgs
from mephisto.abstractions.architect import ArchitectArgs
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.data_model.task_run import TaskRunArgs
from mephisto.utils.logger_core import get_logger, warn_once
from mephisto.utils.dirs import get_run_file_dir
from dataclasses import dataclass, field, fields, Field
from omegaconf import OmegaConf, MISSING, DictConfig
from typing import List, Type, Dict, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import Blueprint


logger = get_logger(name=__name__)
LOGGING_OVERRIDE = {"override /hydra/job_logging": "mephisto_default"}
config = ConfigStoreWithProvider("mephisto")


@dataclass
class DatabaseArgs:
    _database_type: str = "singleton"  # default DB is performant singleton


@dataclass
class MephistoConfig:
    blueprint: BlueprintArgs = MISSING
    provider: ProviderArgs = MISSING
    architect: ArchitectArgs = MISSING
    task: TaskRunArgs = TaskRunArgs()
    database: DatabaseArgs = DatabaseArgs()
    log_level: str = "info"


@dataclass
class TaskConfig:
    mephisto: MephistoConfig = MephistoConfig()
    task_dir: str = get_run_file_dir()
    num_tasks: int = 5
    defaults: List[Any] = field(default_factory=lambda: ["_self_", LOGGING_OVERRIDE])


def register_abstraction_config(name: str, node: Any, abstraction_type: str):
    config.store(
        name=name,
        node=node,
        group=f"mephisto/{abstraction_type}",
    )


def build_default_task_config(conf_name: str) -> Type[TaskConfig]:
    default_list = ["_self_", {"conf": conf_name}, LOGGING_OVERRIDE]

    @dataclass
    class DefaultTaskConfig(TaskConfig):
        defaults: List[Any] = field(default_factory=lambda: default_list)

    return DefaultTaskConfig


@dataclass
class RunScriptConfig(TaskConfig):
    def __post_init__(self):
        warn_once(
            "RunScriptConfig has been deprecated in Mephisto 1.0 in favor "
            "of using TaskConfig and the `task_script` decorator. See "
            "our new examples for usage."
        )


def initialize_named_configs():
    """
    Functionality to register the core mephisto configuration structure. Must be done in __init__
    """
    config.store(
        name="base_mephisto_config",
        node=MephistoConfig,
        group="mephisto",
    )


def register_script_config(name: str, module: Any):
    check_for_hydra_compat()
    config.store(name=name, node=module)


def check_for_hydra_compat():
    # Required for determining 0.3.x to 0.4.0 conversion
    # of scripts
    import inspect
    import os

    callsite = inspect.stack(0)[-1].filename
    call_dir = os.path.dirname(os.path.join(".", callsite))
    if "hydra_configs" not in os.listdir(call_dir):
        logger.warning(
            "\u001b[31;1m"
            f"We noticed you don't have a hydra_configs directory in the folder "
            f"{call_dir} where you are running this script from.\n"
            "Mephisto Version 0.4.0 has breaking changes for user scripts due "
            "to the Hydra 1.1 upgrade. This may prevent scripts from launching. "
            "See https://github.com/facebookresearch/Mephisto/issues/529 for "
            "remediation details."
            "\u001b[0m"
        )


## Hydra argument config parsing helpers for other uses, generally the server API


def get_dict_from_field(in_field: Field) -> Dict[str, Any]:
    """
    Extract all of the arguments from an argument group
    and return a dict mapping from argument dest to argument dict
    """
    try:
        found_type = in_field.type.__name__
    except AttributeError:
        found_type = in_field.metadata.get("type", "unknown")
    return {
        "dest": in_field.name,
        "type": found_type,
        "default": in_field.metadata.get("default", in_field.default),
        "help": in_field.metadata.get("help"),
        "choices": in_field.metadata.get("choices"),
        "required": in_field.metadata.get("required", False),
    }


def get_extra_argument_dicts(customizable_class: Any) -> List[Dict[str, Any]]:
    """
    Produce the argument dicts for the given customizable class
    (Blueprint, Architect, etc)
    """
    dict_fields = fields(customizable_class.ArgsClass)
    usable_fields = []
    group_field = None
    for f in dict_fields:
        if not f.name.startswith("_"):
            usable_fields.append(f)
        elif f.name == "_group":
            group_field = f
    parsed_fields = [get_dict_from_field(f) for f in usable_fields]
    help_text = ""
    if group_field is not None:
        help_text = group_field.metadata.get("help", "")
    return [{"desc": help_text, "args": {f["dest"]: f for f in parsed_fields}}]


def get_task_state_dicts(customizable_class: Type["Blueprint"]) -> List[Dict[str, Any]]:
    """
    Return the SharedTaskState configurable class for the given blueprint
    """
    dict_fields = fields(customizable_class.SharedStateClass)
    usable_fields = []
    for f in dict_fields:
        if not f.name.startswith("_"):
            usable_fields.append(f)
    parsed_fields = [get_dict_from_field(f) for f in usable_fields]
    return [{"desc": "", "args": {f["dest"]: f for f in parsed_fields}}]


def parse_arg_dict(customizable_class: Any, args: Dict[str, Any]) -> DictConfig:
    """
    Get the ArgsClass for a class, then parse the given args using
    it. Return the DictConfig of the finalized namespace.
    """
    return OmegaConf.structured(customizable_class.ArgsClass(**args))
