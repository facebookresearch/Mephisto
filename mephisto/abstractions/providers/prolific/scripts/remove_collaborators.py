#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.prolific.prolific_requester import (
    ProlificRequester,
)
from mephisto.abstractions.providers.prolific.api.data_models import Workspace
import json

import hydra
from hydra.core.config_store import ConfigStore
from dataclasses import dataclass
from typing import Optional, List, Set, cast


@dataclass
class RemoveCollaboratorArgs:
    requester_name: Optional[str] = None
    removals: Optional[List[List[str]]] = None


cs = ConfigStore.instance()
cs.store(name="removecollaboratorargs", node=RemoveCollaboratorArgs)


@hydra.main(version_base=None, config_name="removecollaboratorargs")
def main(args: RemoveCollaboratorArgs):
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

    if args.removals is not None:
        removals = args.removals
    else:
        removals = []
        REMOVE_INPUT = (
            "Provide the user id and workspace id to remove "
            "from, line by line comma separated. Leave empty "
            "to continue\n>> "
        )
        while len(next_remove := input(REMOVE_INPUT).strip()) > 0:
            removals.append(next_remove.split(",", 1))

    requester: ProlificRequester = requester_name_mapping[requester_name]

    client = requester._get_client(requester_name=requester_name)
    workspaces = client.Workspaces.list()
    workspace_map = {w.id: w for w in workspaces}
    edited_workspaces = {}

    def get_existing_ids(workspace: Workspace) -> Set[str]:
        return set([u["id"] for u in workspace.users])

    for (remove_id, w_id) in removals:
        if w_id not in edited_workspaces:
            edited_workspaces[w_id] = get_existing_ids(workspace_map[w_id])
        edited_workspaces[w_id].remove(remove_id)

    for w_id, final_users in edited_workspaces.items():
        workspace = workspace_map[w_id]
        workspace.users = [u for u in workspace.users if u["id"] in final_users]
        client.Workspaces.update(workspace)
        print(f"Updated {w_id} to remove any listed users")


if __name__ == "__main__":
    main()
