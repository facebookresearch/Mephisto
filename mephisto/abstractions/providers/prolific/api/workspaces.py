#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_api_resource import BaseAPIResource
from .data_models import Workspace
from .data_models import WorkspaceBalance


class Workspaces(BaseAPIResource):
    list_api_endpoint = "workspaces/"
    retrieve_api_endpoint = "workspaces/{id}/"
    get_balance_api_endpoint = "workspaces/{id}/balance/"

    @classmethod
    def list(cls) -> List[Workspace]:
        response_json = cls.get(cls.list_api_endpoint)
        workspaces = [Workspace(**s) for s in response_json["results"]]
        return workspaces

    @classmethod
    def retrieve(cls, id: str) -> Workspace:
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return Workspace(**response_json)

    @classmethod
    def create(cls, **data) -> Workspace:
        workspace = Workspace(**data)
        workspace.validate()
        response_json = cls.post(cls.list_api_endpoint, params=workspace.to_dict())
        return Workspace(**response_json)

    @classmethod
    def update(cls, id: str, **data) -> Workspace:
        endpoint = cls.retrieve_api_endpoint.format(id=id)
        workspace = Workspace(**data)
        workspace.validate(check_required_fields=False)
        params = workspace.to_dict()
        if params["description"] == "":
            params.pop("description", None)
        params.pop("product", None)  # TODO: What is this? Don't see this field in API docs
        response_json = cls.patch(endpoint, params=params)
        return Workspace(**response_json)

    @classmethod
    def get_balance(cls, id: str) -> WorkspaceBalance:
        endpoint = cls.get_balance_api_endpoint.format(id=id)
        response_json = cls.get(endpoint)
        return WorkspaceBalance(**response_json)
