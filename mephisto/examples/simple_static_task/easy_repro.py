#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from hydra.core.config_store import ConfigStoreWithProvider
import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] {%(filename)s:%(lineno)d} FROM MY LOGGER: %(levelname)5s - %(message)s",
        "%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


my_logger = get_logger("repro-file-logger")

config = ConfigStoreWithProvider("test")


def register_script_config(name: str, module):
    config.store(name=name, node=module)


@dataclass
class ScriptConfig:
    test: str = "hello"


register_script_config(name="scriptconfig", module=ScriptConfig)


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    my_logger.info("This is a message from my logger")


if __name__ == "__main__":
    main()
