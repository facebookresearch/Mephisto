#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_api_resource import BaseAPIResource
from .constants import WorkspaceRole

from typing import List


class Invitations(BaseAPIResource):
    invitations_api_endpoint = "invitations/"

    @classmethod
    def create(
        cls,
        workspace_id: str,
        collaborators: List[str],
        role: str = WorkspaceRole.WORKSPACE_ADMIN,
    ) -> dict:
        endpoint = cls.invitations_api_endpoint
        params = {
            "association": workspace_id,
            "emails": collaborators,
            "role": role,
        }
        response_json = cls.post(endpoint, params=params)
        return response_json
