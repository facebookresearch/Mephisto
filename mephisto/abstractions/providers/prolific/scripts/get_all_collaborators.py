#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.prolific.prolific_requester import (
    ProlificRequester,
)
import json

import hydra
from hydra.core.config_store import ConfigStore
from dataclasses import dataclass
from typing import Optional, List, cast


@dataclass
class GetCollaboratorsArgs:
    requester_name: Optional[str] = None


cs = ConfigStore.instance()
cs.store(name="getcollaboratorargs", node=GetCollaboratorsArgs)


@hydra.main(version_base=None, config_name="getcollaboratorargs")
def main(args: GetCollaboratorsArgs):
    """
    Script to query all workspaces for the given account, and list all collaborators
    """
    db = LocalMephistoDB()
    requester_options = db.find_requesters(provider_type=PROVIDER_TYPE)
    requester_name_mapping = {
        n.requester_name: cast(ProlificRequester, n) for n in requester_options
    }
    all_requester_names = ", ".join(requester_name_mapping.keys())
    assert len(requester_name_mapping) > 0, "No registered prolific requesters!"
    if args.requester_name is not None:
        requester_name = args.requester_name
        assert requester_name in requester_name_mapping, (
            f"Provided requester name {requester_name} not in "
            f"the available requester names:\n{all_requester_names}"
        )
    else:
        requester_name = input(
            "Enter Prolific Requester Admin account. Available names:\n"
            f"{all_requester_names}\n>> "
        )
        while requester_name not in requester_name_mapping:
            requester_name = input(
                "Invalid Name. Enter Prolific Requester Admin account. "
                f"Available names:\n{all_requester_names}\n>>"
            )

    requester: ProlificRequester = requester_name_mapping[requester_name]

    client = requester._get_client(requester_name=requester_name)
    workspaces = client.Workspaces.list()
    res = {}
    for w in workspaces:
        res[w.id] = {
            "title": w.title,
            "owner": w.owner,
            "users": w.users,
        }

    print(json.dumps(res, indent=4))


if __name__ == "__main__":
    main()
