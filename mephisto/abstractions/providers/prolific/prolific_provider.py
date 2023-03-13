#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass
from typing import Any
from typing import cast
from typing import ClassVar
from typing import Type
from typing import TYPE_CHECKING

from mephisto.abstractions.crowd_provider import CrowdProvider
from mephisto.abstractions.crowd_provider import ProviderArgs
from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.prolific.prolific_agent import ProlificAgent
from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
from mephisto.abstractions.providers.prolific.prolific_unit import ProlificUnit
from mephisto.abstractions.providers.prolific.prolific_worker import ProlificWorker
from mephisto.operations.registry import register_mephisto_abstraction

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent
    from mephisto.abstractions.blueprint import SharedTaskState
    from omegaconf import DictConfig


@dataclass
class ProlificProviderArgs(ProviderArgs):
    """Base class for arguments to configure Crowd Providers"""
    _provider_type: str = PROVIDER_TYPE


@register_mephisto_abstraction()
class ProlificProvider(CrowdProvider):
    """
    Prolific implementation of a CrowdProvider that stores everything
    in a local state in the class for use in tests.
    """
    UnitClass: ClassVar[Type["Unit"]] = ProlificUnit

    RequesterClass: ClassVar[Type["Requester"]] = ProlificRequester

    WorkerClass: ClassVar[Type["Worker"]] = ProlificWorker

    AgentClass: ClassVar[Type["Agent"]] = ProlificAgent

    ArgsClass = ProlificProviderArgs

    PROVIDER_TYPE = PROVIDER_TYPE

    curr_db_location: ClassVar[str]

    def initialize_provider_datastore(self, storage_path: str) -> Any:
        return ProlificDatastore(datastore_root=storage_path)

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client"""
        return self.datastore.get_client_for_requester(requester_name)

    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        requester = cast('ProlificRequester', task_run.get_requester())
        task_run_id = task_run.db_id

        # Set up Task Run config
        config_dir = os.path.join(self.datastore.datastore_root, task_run_id)
        task_args = args.task

        # Find or create relevant qualifications
        qualifications = []
        for qualification in shared_state.qualifications:
            applicable_providers = qualification['applicable_providers']

            if applicable_providers is None or self.PROVIDER_TYPE in applicable_providers:
                qualifications.append(qualification)

        for qualification in qualifications:
            qualification_name = qualification['qualification_name']

            if self.datastore.get_qualification_mapping(qualification_name) is None:
                qualification['id'] = requester.create_new_qualification(qualification_name)

        if hasattr(shared_state, 'prolific_specific_qualifications'):
            # TODO(OWN) standardize provider-specific qualifications
            qualifications += shared_state.prolific_specific_qualifications

        # Set up Task Run (Prolific Project)
        client = self._get_client(requester.requester_name)
        project_id = prolific_utils.create_study(client, task_args, qualifications)
        frame_height = task_run.get_blueprint().get_frontend_args().get('frame_height', 0)
        self.datastore.register_run(task_run_id, project_id, config_dir, frame_height)

    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        return None

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")
