#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_api_resource import BaseAPIResource
from .data_models import Project


class Projects(BaseAPIResource):
    list_for_workspace_api_endpoint = "workspaces/{workspace_id}/projects/"
    retrieve_for_workspace_api_endpoint = "workspaces/{workspace_id}/projects/{project_id}/"

    @classmethod
    def list_for_workspace(cls, workspace_id: str) -> List[Project]:
        endpoint = cls.list_for_workspace_api_endpoint.format(workspace_id=workspace_id)
        response_json = cls.get(endpoint)
        projects = [Project(**s) for s in response_json["results"]]
        return projects

    @classmethod
    def retrieve_for_workspace(cls, workspace_id: str, project_id: str) -> Project:
        endpoint = cls.retrieve_for_workspace_api_endpoint.format(
            workspace_id=workspace_id,
            project_id=project_id,
        )
        response_json = cls.get(endpoint)
        return Project(**response_json)

    @classmethod
    def create_for_workspace(cls, workspace_id: str, **data) -> Project:
        project = Project(**data)
        project.validate()
        endpoint = cls.list_for_workspace_api_endpoint.format(workspace_id=workspace_id)
        response_json = cls.post(endpoint, params=project.to_dict())
        return Project(**response_json)
