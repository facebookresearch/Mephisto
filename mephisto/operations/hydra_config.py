#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from hydra.core.config_store import ConfigStoreWithProvider
from mephisto.abstractions.blueprint import BlueprintArgs
from mephisto.abstractions.architect import ArchitectArgs
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.data_model.task_config import TaskConfigArgs
from dataclasses import dataclass, field
from omegaconf import MISSING
from typing import List, Any

config = ConfigStoreWithProvider("mephisto")


@dataclass
class DatabaseArgs:
    _database_type: str = "local"  # default DB is local


@dataclass
class MephistoConfig:
    blueprint: BlueprintArgs = BlueprintArgs()
    provider: ProviderArgs = ProviderArgs()
    architect: ArchitectArgs = ArchitectArgs()
    task: TaskConfigArgs = TaskConfigArgs()
    database: DatabaseArgs = DatabaseArgs()
    log_level: str = "info"


@dataclass
class RunScriptConfig:
    mephisto: MephistoConfig = MephistoConfig()


def register_abstraction_config(name: str, node: Any, abstraction_type: str):
    config.store(
        name=name, node=node, group=f"mephisto/{abstraction_type}", package="_group_"
    )


def initialize_named_configs():
    """
    Functionality to register the core mephisto configuration structure. Must be done in __init__
    """
    config.store(
        name="base_mephisto_config",
        node=MephistoConfig,
        group="mephisto",
        package="_group_",
    )


def register_script_config(name: str, module: Any):
    config.store(name=name, node=module)
