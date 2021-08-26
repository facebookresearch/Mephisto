#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from hydra.core.config_store import ConfigStoreWithProvider
from mephisto.abstractions.blueprint import BlueprintArgs
from mephisto.abstractions.architect import ArchitectArgs
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.data_model.task_config import TaskConfigArgs
from mephisto.operations.logger_core import get_logger
from dataclasses import dataclass, field
from omegaconf import MISSING
from typing import List, Any

logger = get_logger(name=__name__)

config = ConfigStoreWithProvider("mephisto")


@dataclass
class DatabaseArgs:
    _database_type: str = "local"  # default DB is local


@dataclass
class MephistoConfig:
    blueprint: BlueprintArgs = MISSING
    provider: ProviderArgs = MISSING
    architect: ArchitectArgs = MISSING
    task: TaskConfigArgs = TaskConfigArgs()
    database: DatabaseArgs = DatabaseArgs()
    log_level: str = "info"


@dataclass
class RunScriptConfig:
    mephisto: MephistoConfig = MephistoConfig()


def register_abstraction_config(name: str, node: Any, abstraction_type: str):
    config.store(
        name=name,
        node=node,
        group=f"mephisto/{abstraction_type}",
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
    for entry in inspect.stack(0):
        print(entry.filename)
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
