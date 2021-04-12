#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Utilities that are useful for Mephisto-related scripts.
"""

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.operations.utils import get_mock_requester, get_root_data_dir

from omegaconf import DictConfig, OmegaConf

import argparse
from typing import Tuple, Dict, Any, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB


def load_db_and_process_config(
    cfg: DictConfig, print_config=False
) -> Tuple["MephistoDB", DictConfig]:
    """
    Using a Hydra DictConfig built from a RunScriptConfig,
    load the desired MephistoDB and
    validate the config against the database contents, then
    return the database and validated config.

    Takes in an option to print out the configuration before returning
    """
    db = get_db_from_config(cfg)
    valid_config = augment_config_from_db(cfg, db)
    if print_config:
        print(OmegaConf.to_yaml(valid_config))
    return db, valid_config


def get_db_from_config(cfg: DictConfig) -> "MephistoDB":
    """
    Get a MephistoDB from the given configuration. As of now
    this defaults to a LocalMephistoDB
    """
    datapath = cfg.mephisto.get("datapath", None)

    if datapath is None:
        datapath = get_root_data_dir()

    database_path = os.path.join(datapath, "database.db")

    database_type = cfg.mephisto.database._database_type

    if database_type == "local":
        return LocalMephistoDB(database_path=database_path)
    elif database_type == "singleton":
        return MephistoSingletonDB(database_path=database_path)
    else:
        raise AssertionError(f"Provided database_type {database_type} is not valid")


def augment_config_from_db(script_cfg: DictConfig, db: "MephistoDB") -> DictConfig:
    """
    Check the database for validity of the incoming MephistoConfig, ensure
    that the config has all the necessary fields set.
    """
    cfg = script_cfg.mephisto
    requester_name = cfg.provider.get("requester_name", None)
    provider_type = cfg.provider.get("_provider_type", None)
    architect_type = cfg.architect.get("_architect_type", None)

    if requester_name is None:
        if provider_type is None:
            print("No requester specified, defaulting to mock")
            provider_type = "mock"
        if provider_type == "mock":
            req = get_mock_requester(db)
            requester_name = req.requester_name
        else:
            reqs = db.find_requesters(provider_type=provider_type)
            # TODO (#93) proper logging
            if len(reqs) == 0:
                print(
                    f"No requesters found for provider type {provider_type}, please "
                    f"register one. You can register with `mephisto register {provider_type}`, "
                    f"or `python mephisto/client/cli.py register {provider_type}` if you haven't "
                    "installed Mephisto using poetry."
                )
                exit(1)
            elif len(reqs) == 1:
                req = reqs[0]
                requester_name = req.requester_name
                print(
                    f"Found one `{provider_type}` requester to launch with: {requester_name}"
                )
            else:
                req = reqs[-1]
                requester_name = req.requester_name
                print(
                    f"Found many `{provider_type}` requesters to launch with, "
                    f"choosing the most recent: {requester_name}"
                )
    else:
        # Ensure provided requester exists
        reqs = db.find_requesters(requester_name=requester_name)
        if len(reqs) == 0:
            print(
                f"No requesters found under name {requester_name}, "
                "have you registered with `mephisto register`?"
            )
            exit(1)
        provider_type = reqs[0].provider_type

    if provider_type in ["mturk"]:
        input(
            f"This task is going to launch live on {provider_type}, press enter to continue: "
        )
    if provider_type in ["mturk_sandbox", "mturk"] and architect_type != "heroku":
        input(
            f"This task is going to launch live on {provider_type}, but your "
            f"provided architect is {architect_type}, are you sure you "
            "want to do this? : "
        )

    cfg.provider.requester_name = requester_name
    cfg.provider._provider_type = provider_type
    return script_cfg
