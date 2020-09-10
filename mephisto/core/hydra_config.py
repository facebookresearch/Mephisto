
from hydra.core.config_store import ConfigStoreWithProvider
from mephisto.data_model.blueprint import BlueprintArgs
from mephisto.data_model.task_config import TaskConfigArgs
from dataclasses import dataclass, field
from omegaconf import MISSING
from typing import List, Any

config = ConfigStoreWithProvider("mephisto")

@dataclass
class MephistoConfig:
    blueprint: BlueprintArgs = MISSING
    provider: Any = MISSING
    architect: Any = MISSING
    task: TaskConfigArgs = TaskConfigArgs()

@dataclass
class ScriptConfig:
    mephisto: MephistoConfig = MephistoConfig()


def register_abstraction_config(name: str, node: Any, abstraction_type: str):
    config.store(name=name, node=node, group=f"mephisto.{abstraction_type}", package="_group_")
     

def initialize_named_configs():
    config.store(name="base_mephisto_config", node=MephistoConfig, group="mephisto", package="_group_")


def register_script_config(name: str, module: Any):
    config.store(name=name, node=module)