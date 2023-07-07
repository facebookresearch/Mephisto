#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.prolific.prolific_requester import (
    ProlificRequester,
)
from mephisto.abstractions.providers.prolific.prolific_utils import (
    find_or_create_prolific_workspace,
)

import hydra
from hydra.core.config_store import ConfigStore
from dataclasses import dataclass
from typing import Optional, List, cast


@dataclass
class NewProjectArgs:
    requester_name: Optional[str] = None
    project_name: Optional[str] = None
    collaborators: Optional[List[str]] = None


cs = ConfigStore.instance()
cs.store(name="newprojectargs", node=NewProjectArgs)


@hydra.main(version_base=None, config_name="newprojectargs")
def main(args: NewProjectArgs):
    """
    Script to create a new Prolific workspace and invite
    the intended collaborators to join.
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

    project_name = args.project_name
    if project_name is None:
        project_name = input(
            "Provide a name for this workspace, based on the overall project.\n>> "
        )

    collaborators = args.collaborators
    if collaborators is None:
        collaborators = []
        COLLAB_INPUT = (
            "Provide an email for a collaborator. Leave, blank when done.\n>> "
        )
        while len(next_collaborator := input(COLLAB_INPUT).strip()) > 0:
            collaborators.append(next_collaborator)

    print(f"Creating workspace: {project_name}")
    client = requester._get_client(requester_name=requester_name)
    workspace = find_or_create_prolific_workspace(client, project_name)

    print(f"Created workspace for this research group: {workspace.id}")
    print(f"Adding Collaborators")
    res = client.Invitations.create(
        workspace_id=workspace.id, collaborators=collaborators
    )
    print(f"Create result: {res}")


if __name__ == "__main__":
    main()
